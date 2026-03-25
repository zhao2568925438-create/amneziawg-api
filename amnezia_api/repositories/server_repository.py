from __future__ import annotations

from typing import Any

from amnezia_api.core.database import Database


class ServerRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO servers (
                    name, host, user, port, identity_file,
                    manage_script_path, strict_host_key_checking
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["name"],
                    payload["host"],
                    payload["user"],
                    payload["port"],
                    payload["identity_file"],
                    payload["manage_script_path"],
                    payload["strict_host_key_checking"],
                ),
            )
            server_id = cursor.lastrowid
        return self.get(server_id)

    def list(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT * FROM servers ORDER BY id ASC").fetchall()
        return [dict(row) for row in rows]

    def get(self, server_id: int) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM servers WHERE id = ?",
                (server_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Server {server_id} not found")
        return dict(row)
