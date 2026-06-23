"""Initialize the local SQLite database schema."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.db import connect, get_database_path  # noqa: E402


def main() -> None:
    path = get_database_path()
    with connect():
        pass
    print(f"Initialized database: {path}")


if __name__ == "__main__":
    main()

