from app.core.settings import get_settings


def test_settings_read_environment_values(monkeypatch, tmp_path):
    monkeypatch.setenv("SQLITE_DATABASE_PATH", str(tmp_path / "custom.db"))
    monkeypatch.setenv("UPLOAD_DIRECTORY", str(tmp_path / "files"))
    monkeypatch.setenv("MAX_UPLOAD_SIZE_BYTES", "123")
    monkeypatch.setenv("CORS_ORIGINS", "http://one.test, http://two.test")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "4.5")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.sqlite_database_path == tmp_path / "custom.db"
    assert settings.upload_directory == tmp_path / "files"
    assert settings.max_upload_size_bytes == 123
    assert settings.cors_origins == ("http://one.test", "http://two.test")
    assert settings.ollama_timeout_seconds == 4.5
    get_settings.cache_clear()
