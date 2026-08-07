import importlib
import sys


def test_environment_configuration_is_used(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "db.internal")
    monkeypatch.setenv("POSTGRES_PORT", "6543")
    monkeypatch.setenv("POSTGRES_DB", "codeatlas_test")
    monkeypatch.setenv("POSTGRES_USER", "app_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "s3cr3t")
    monkeypatch.setenv("NEO4J_URI", "bolt://neo4j.internal:7687")
    monkeypatch.setenv("NEO4J_USER", "neo4j_user")
    monkeypatch.setenv("NEO4J_PASSWORD", "neo4j_secret")
    monkeypatch.setenv("REDIS_URL", "redis://redis.internal:6380/1")

    sys.modules.pop("apps.api.config", None)
    config = importlib.import_module("apps.api.config")

    assert config.get_database_url() == (
        "postgresql+psycopg://app_user:s3cr3t@db.internal:6543/codeatlas_test"
    )
    assert config.get_neo4j_uri() == "bolt://neo4j.internal:7687"
    assert config.get_neo4j_auth() == ("neo4j_user", "neo4j_secret")
    assert config.get_redis_url() == "redis://redis.internal:6380/1"
