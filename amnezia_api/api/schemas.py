from __future__ import annotations

from pydantic import BaseModel, Field


class ServerCreate(BaseModel):
    name: str = Field(min_length=1)
    host: str = Field(min_length=1)
    user: str = "root"
    port: int = 22
    identity_file: str | None = None
    manage_script_path: str = "/root/awg/manage_amneziawg.sh"
    strict_host_key_checking: str = "accept-new"


class ServerResponse(BaseModel):
    id: int
    name: str
    host: str
    user: str
    port: int
    identity_file: str | None
    manage_script_path: str
    strict_host_key_checking: str
    created_at: str
    is_reachable: bool | None = None
    status: str | None = None
    status_label: str | None = None


class ClientListItem(BaseModel):
    name: str
    has_conf: bool
    has_qr: bool
    status: str
    status_label: str
    expires_in: str | None = None


class ClientCreate(BaseModel):
    server_id: int
    client_name: str = Field(min_length=1)
    expires: str | None = None


class ClientExtend(BaseModel):
    server_id: int
    client_name: str = Field(min_length=1)
    expires: str = Field(min_length=2)


class ClientDeleteResponse(BaseModel):
    succsess: bool
    server_id: int
    client_name: str


class ArtifactLinks(BaseModel):
    conf_url: str
    png_url: str


class ClientCreateResponse(BaseModel):
    succsess: bool
    server_id: int
    client_name: str
    files: ArtifactLinks


class ClientExtendResponse(BaseModel):
    succsess: bool
    server_id: int
    client_name: str
    expires: str


class ClientListResponse(BaseModel):
    succsess: bool
    server_id: int
    count: int
    clients: list[ClientListItem]
