"""Runtime configuration for backend services."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    engine: str
    path: Path | None


@dataclass(frozen=True)
class ChromaConfig:
    persist_directory: Path
    collection: str


def get_database_config() -> DatabaseConfig:
    url = os.getenv("DATABASE_URL", "sqlite:///data/alarm_agent.db")
    if url.startswith("sqlite:///"):
        raw_path = url.removeprefix("sqlite:///")
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        return DatabaseConfig(url=url, engine="sqlite", path=path)
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        return DatabaseConfig(url=url, engine="postgresql", path=None)
    raise ValueError(f"Unsupported DATABASE_URL: {url}")


def get_chroma_config() -> ChromaConfig:
    raw_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "data/chroma")
    path = Path(raw_dir)
    if not path.is_absolute():
        path = ROOT / path
    return ChromaConfig(
        persist_directory=path,
        collection=os.getenv("CHROMA_COLLECTION", "process_knowledge"),
    )

