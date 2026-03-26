from __future__ import annotations

from pathlib import Path
from typing import Any

from amnezia_api.core.database import Database


class ArtifactRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save(
        self,
        artifact_id: str,
        server_id: int,
        client_name: str,
        file_type: str,
        file_path: Path,
        download_name: str,
    ) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO artifacts (
                    id, server_id, client_name, file_type, file_path, download_name
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    server_id,
                    client_name,
                    file_type,
                    str(file_path),
                    download_name,
                ),
            )

    def get(self, artifact_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM artifacts WHERE id = ?",
                (artifact_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Artifact {artifact_id} not found")
        return dict(row)

    def list_by_client(self, server_id: int, client_name: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM artifacts
                WHERE server_id = ? AND client_name = ?
                ORDER BY created_at ASC
                """,
                (server_id, client_name),
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_by_client(self, server_id: int, client_name: str) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "DELETE FROM artifacts WHERE server_id = ? AND client_name = ?",
                (server_id, client_name),
            )

    def list_by_server(self, server_id: int) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM artifacts
                WHERE server_id = ?
                ORDER BY created_at ASC
                """,
                (server_id,),
            ).fetchall()
        return [dict(row) for row in rows]
