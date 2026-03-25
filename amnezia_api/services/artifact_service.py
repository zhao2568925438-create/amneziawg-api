from __future__ import annotations

import shutil
from pathlib import Path

from amnezia_api.repositories.artifact_repository import ArtifactRepository


class ArtifactService:
    def __init__(self, artifact_repository: ArtifactRepository) -> None:
        self.artifact_repository = artifact_repository

    def cleanup_client_artifacts(self, server_id: int, client_name: str) -> None:
        artifacts = self.artifact_repository.list_by_client(server_id, client_name)
        directories_to_remove: set[Path] = set()

        for artifact in artifacts:
            file_path = Path(artifact["file_path"])
            if file_path.exists():
                file_path.unlink()
            directories_to_remove.add(file_path.parent)

        self.artifact_repository.delete_by_client(server_id, client_name)

        for directory in sorted(directories_to_remove, reverse=True):
            if directory.exists():
                shutil.rmtree(directory, ignore_errors=True)
