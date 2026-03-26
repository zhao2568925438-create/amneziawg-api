from __future__ import annotations

import os
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Settings:
    api_host: str
    api_port: int
    api_token: str
    database_path: Path
    storage_dir: Path
    ssh_multiplexing_enabled: bool
    ssh_control_dir: Path
    ssh_control_persist: str
    server_queue_timeout: int


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        api_host=os.getenv("API_HOST", "127.0.0.1"),
        api_port=int(os.getenv("API_PORT", "8000")),
        api_token=os.getenv("API_TOKEN", "change-me"),
        database_path=Path(os.getenv("DATABASE_PATH", "./data/app.db")).expanduser(),
        storage_dir=Path(os.getenv("STORAGE_DIR", "./storage")).expanduser(),
        ssh_multiplexing_enabled=os.getenv("SSH_MULTIPLEXING_ENABLED", "true").lower() in {"1", "true", "yes", "on"},
        ssh_control_dir=Path(os.getenv("SSH_CONTROL_DIR", "/tmp/amneziawg-ssh")).expanduser(),
        ssh_control_persist=os.getenv("SSH_CONTROL_PERSIST", "10m"),
        server_queue_timeout=int(os.getenv("SERVER_QUEUE_TIMEOUT", "120")),
    )
