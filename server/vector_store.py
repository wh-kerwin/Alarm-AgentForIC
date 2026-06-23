"""ChromaDB vector store configuration placeholder."""

from __future__ import annotations

from dataclasses import asdict

from server.config import get_chroma_config


class ChromaProcessKnowledgeStore:
    """Reserved boundary for ChromaDB-backed process knowledge retrieval."""

    def status(self) -> dict:
        config = get_chroma_config()
        return {
            "status": "reserved",
            "provider": "chromadb",
            "config": asdict(config),
            "message": "ChromaDB process knowledge retrieval is reserved for the next knowledge indexing slice.",
        }

