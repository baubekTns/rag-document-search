import sqlite3

import pytest

from app.core.database import get_connection, transaction
from app.core.settings import get_settings


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch, tmp_path):
    monkeypatch.setenv("SQLITE_DATABASE_PATH", str(tmp_path / "test.db"))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_connections_enable_foreign_keys():
    connection = get_connection()
    try:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        connection.close()


def test_transaction_rolls_back_on_error():
    with pytest.raises(RuntimeError):
        with transaction() as connection:
            connection.execute("CREATE TABLE records (id INTEGER PRIMARY KEY)")
            connection.execute("INSERT INTO records (id) VALUES (1)")
            raise RuntimeError("force rollback")

    connection = get_connection()
    try:
        with pytest.raises(sqlite3.OperationalError):
            connection.execute("SELECT * FROM records").fetchall()
    finally:
        connection.close()
