import os
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_dotenv()


def _get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


def get_database_url() -> str:
    host = _get_env("POSTGRES_HOST", "localhost")
    port = _get_env("POSTGRES_PORT", "5432")
    db = _get_env("POSTGRES_DB", "codeatlas")
    user = _get_env("POSTGRES_USER", "codeatlas")
    password = _get_env("POSTGRES_PASSWORD", "codeatlas")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


def get_neo4j_uri() -> str:
    return _get_env("NEO4J_URI", "bolt://localhost:7687")


def get_neo4j_auth() -> tuple[str, str]:
    username = _get_env("NEO4J_USER", "neo4j")
    password = _get_env("NEO4J_PASSWORD", "codeatlas")
    return username, password


def get_redis_url() -> str:
    return _get_env("REDIS_URL", "redis://localhost:6379")
