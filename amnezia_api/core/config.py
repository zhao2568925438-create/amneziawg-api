from __future__ import annotations

import os
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


def get_settings() -> Settings:
    return Settings(
        api_host=os.getenv("API_HOST", "127.0.0.1"),
        api_port=int(os.getenv("API_PORT", "8000")),
        api_token=os.getenv("API_TOKEN", "change-me"),
        database_path=Path(os.getenv("DATABASE_PATH", "./data/app.db")).expanduser(),
        storage_dir=Path(os.getenv("STORAGE_DIR", "./storage")).expanduser(),
    )
