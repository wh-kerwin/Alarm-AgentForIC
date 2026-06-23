import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from server.config import get_chroma_config, get_database_config
from server.db import connect
from server.vector_store import ChromaProcessKnowledgeStore


class DatabaseConfigTests(unittest.TestCase):
    def test_sqlite_database_config_resolves_relative_path(self):
        with patch.dict("os.environ", {"DATABASE_URL": "sqlite:///data/example.db"}):
            config = get_database_config()

        self.assertEqual(config.engine, "sqlite")
        self.assertTrue(str(config.path).endswith("data\\example.db") or str(config.path).endswith("data/example.db"))

    def test_postgresql_database_config_is_reserved(self):
        with patch.dict("os.environ", {"DATABASE_URL": "postgresql://user:pass@localhost/db"}):
            config = get_database_config()

        self.assertEqual(config.engine, "postgresql")
        self.assertIsNone(config.path)

    def test_sqlite_schema_initializes(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_url = f"sqlite:///{Path(tmp) / 'test.db'}"
            with patch.dict("os.environ", {"DATABASE_URL": db_url}):
                with connect() as conn:
                    tables = {
                        row["name"]
                        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                    }

        self.assertIn("feedback_records", tables)
        self.assertIn("knowledge_cases", tables)
        self.assertIn("audit_records", tables)

    def test_chroma_store_is_reserved_with_config(self):
        with patch.dict("os.environ", {"CHROMA_PERSIST_DIRECTORY": "data/chroma-test", "CHROMA_COLLECTION": "test_collection"}):
            config = get_chroma_config()
            status = ChromaProcessKnowledgeStore().status()

        self.assertEqual(config.collection, "test_collection")
        self.assertEqual(status["provider"], "chromadb")
        self.assertEqual(status["status"], "reserved")


if __name__ == "__main__":
    unittest.main()
