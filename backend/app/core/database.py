"""SQLite connection and initialization helpers shared by repositories."""

from contextlib import contextmanager
import sqlite3
from collections.abc import Iterator

from app.core.settings import get_settings


SCHEMA_VERSION = 1


def get_connection() -> sqlite3.Connection:
    database_path = get_settings().sqlite_database_path
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    """Provide one committed-or-rolled-back connection for a unit of work."""
    connection = get_connection()
    try:
        connection.execute("BEGIN")
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_schema_version(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "INSERT OR IGNORE INTO schema_metadata (key, value) VALUES ('schema_version', ?)",
        (str(SCHEMA_VERSION),),
    )
