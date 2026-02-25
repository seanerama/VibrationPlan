"""Tests for application configuration."""

from app.config import Settings


def test_config_loads_with_defaults():
    """Config loads successfully with all default values when no env vars are set."""
    settings = Settings()
    assert settings.ENVIRONMENT == "development"
    assert settings.FUZZY_MATCH_THRESHOLD == 70.0
    assert settings.MAX_UPLOAD_SIZE_MB == 10


def test_database_url_defaults_to_sqlite():
    """DATABASE_URL defaults to SQLite for local development."""
    settings = Settings()
    assert settings.DATABASE_URL.startswith("sqlite")


def test_azure_sql_fields_default_empty():
    """Azure SQL fields default to empty strings."""
    settings = Settings()
    assert settings.AZURE_SQL_SERVER == ""
    assert settings.AZURE_SQL_DATABASE == ""
    assert settings.AZURE_SQL_USERNAME == ""
    assert settings.AZURE_SQL_PASSWORD == ""
