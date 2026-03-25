from __future__ import annotations

import time
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

from amnezia_api.api.schemas import (
    ArtifactLinks,
    ClientCreate,
    ClientCreateResponse,
    ClientDeleteResponse,
    ClientExtend,
    ClientExtendResponse,
    ClientListItem,
    ClientListResponse,
    ServerCreate,
    ServerResponse,
)
from amnezia_api.core.auth import require_bearer_token
from amnezia_api.core.config import get_settings
from amnezia_api.core.database import Database
from amnezia_api.repositories.artifact_repository import ArtifactRepository
from amnezia_api.repositories.server_repository import ServerRepository
from amnezia_api.services.amneziawg_manager import AmneziaWGError, AmneziaWGManager, SSHConfig
from amnezia_api.services.artifact_service import ArtifactService
from amnezia_api.services.subscription_service import (
    SubscriptionError,
    calculate_extension,
    format_timestamp,
    parse_prolong_until,
)


settings = get_settings()
database = Database(settings.database_path)
server_repository = ServerRepository(database)
artifact_repository = ArtifactRepository(database)
artifact_service = ArtifactService(artifact_repository)

app = FastAPI(title="AmneziaWG API", version="0.1.0")


def auth_dependency(_: None = Depends(require_bearer_token)) -> None:
    return None


def api_error(status_code: int, error: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"succsess": False, "error": error})


def manager_from_server(server: dict[str, object]) -> AmneziaWGManager:
    return AmneziaWGManager(
        SSHConfig(
            host=str(server["host"]),
            user=str(server["user"]),
            port=int(server["port"]),
            identity_file=server["identity_file"],
            strict_host_key_checking=str(server["strict_host_key_checking"]),
        ),
        manage_script_path=str(server["manage_script_path"]),
    )


def get_manager(server_id: int) -> AmneziaWGManager:
    try:
        server = server_repository.get(server_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return manager_from_server(server)


def build_server_response(server: dict[str, object], include_connectivity: bool = False) -> ServerResponse:
    payload = dict(server)
    if include_connectivity:
        payload.update(manager_from_server(server).check_connectivity())
    return ServerResponse(**payload)


def build_artifact_url(request: Request, artifact_id: str) -> str:
    return str(request.url_for("download_artifact", artifact_id=artifact_id))


@app.on_event("startup")
def on_startup() -> None:
    database.init()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root(_: None = Depends(auth_dependency)) -> dict[str, object]:
    return {"succsess": True, "service": "amneziawg-api"}


@app.post("/api/servers", response_model=ServerResponse)
def create_server(payload: ServerCreate, _: None = Depends(auth_dependency)) -> ServerResponse:
    return build_server_response(server_repository.create(payload.model_dump()), include_connectivity=True)


@app.get("/api/servers", response_model=list[ServerResponse])
def list_servers(_: None = Depends(auth_dependency)) -> list[ServerResponse]:
    return [build_server_response(server, include_connectivity=True) for server in server_repository.list()]


@app.get("/api/clients/{server_id}", response_model=ClientListResponse)
def list_clients(server_id: int, _: None = Depends(auth_dependency)) -> ClientListResponse | JSONResponse:
    manager = get_manager(server_id)
    try:
        data = manager.list_clients_structured()
    except AmneziaWGError as exc:
        return api_error(400, str(exc))

    return ClientListResponse(
        succsess=True,
        server_id=server_id,
        count=data["count"],
        clients=[ClientListItem(**client) for client in data["clients"]],
    )


@app.post("/api/clients", response_model=ClientCreateResponse)
def create_client(
    payload: ClientCreate,
    request: Request,
    _: None = Depends(auth_dependency),
) -> ClientCreateResponse | JSONResponse:
    manager = get_manager(payload.server_id)
    output_dir = settings.storage_dir / f"server_{payload.server_id}" / payload.client_name

    try:
        manager.add_client(payload.client_name, expires=payload.expires)
        config_path, png_path = manager.fetch_client_bundle(payload.client_name, output_dir=output_dir)
    except AmneziaWGError as exc:
        return api_error(400, str(exc))

    conf_id = uuid.uuid4().hex
    png_id = uuid.uuid4().hex
    artifact_repository.save(conf_id, payload.server_id, payload.client_name, "conf", config_path, config_path.name)
    artifact_repository.save(png_id, payload.server_id, payload.client_name, "png", png_path, png_path.name)

    return ClientCreateResponse(
        succsess=True,
        server_id=payload.server_id,
        client_name=payload.client_name,
        files=ArtifactLinks(
            conf_url=build_artifact_url(request, conf_id),
            png_url=build_artifact_url(request, png_id),
        ),
    )


@app.patch("/api/clients/subscription", response_model=ClientExtendResponse)
def extend_client_subscription(
    payload: ClientExtend,
    _: None = Depends(auth_dependency),
) -> ClientExtendResponse | JSONResponse:
    manager = get_manager(payload.server_id)
    try:
        current_expiry = manager.get_client_expiry(payload.client_name)
        target_dt = parse_prolong_until(payload.prolong_until)
        extension = calculate_extension(
            target_dt=target_dt,
            current_expiry_ts=current_expiry,
            now_ts=int(time.time()),
        )
        manager.extend_client(payload.client_name, extension.duration)
        new_expiry = manager.get_client_expiry(payload.client_name)
    except AmneziaWGError as exc:
        error_text = str(exc)
        if "не найден" in error_text.lower():
            return api_error(404, error_text)
        return api_error(400, error_text)
    except SubscriptionError as exc:
        return api_error(400, str(exc))

    if new_expiry is None:
        return api_error(500, "Не удалось получить новый срок действия клиента после продления.")

    return ClientExtendResponse(
        succsess=True,
        server_id=payload.server_id,
        client_name=payload.client_name,
        prolong_until=payload.prolong_until,
        applied_duration=extension.duration,
        expires_at=format_timestamp(new_expiry),
    )


@app.delete("/api/clients/{server_id}/{client_name}", response_model=ClientDeleteResponse)
def delete_client(
    server_id: int,
    client_name: str,
    _: None = Depends(auth_dependency),
) -> ClientDeleteResponse | JSONResponse:
    manager = get_manager(server_id)
    try:
        manager.remove_client(client_name)
    except AmneziaWGError as exc:
        error_text = str(exc)
        if "не найден" in error_text.lower():
            return api_error(404, error_text)
        return api_error(400, error_text)

    artifact_service.cleanup_client_artifacts(server_id, client_name)
    return ClientDeleteResponse(succsess=True, server_id=server_id, client_name=client_name)


@app.get("/api/files/{artifact_id}", name="download_artifact")
def download_artifact(artifact_id: str, _: None = Depends(auth_dependency)) -> FileResponse:
    try:
        artifact = artifact_repository.get(artifact_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    file_path = Path(artifact["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(path=file_path, filename=artifact["download_name"], media_type="application/octet-stream")
