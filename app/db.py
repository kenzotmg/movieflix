import os, pathlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

def _read_secret(path_env: str):
    path = os.getenv(path_env)
    if path and pathlib.Path(path).exists():
        return pathlib.Path(path).read_text().strip()
    return None

def make_db_url() -> str:
    host = os.getenv("DB_HOST", "db")
    port = os.getenv("DB_PORT", "5432")
    name = _read_secret("DB_NAME_FILE") or os.getenv("DB_NAME", "MV_APP")
    user = _read_secret("DB_USER_FILE") or os.getenv("DB_USER")
    pwd  = _read_secret("DB_PASSWORD_FILE") or os.getenv("DB_PASSWORD")
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{name}"


engine = create_engine(make_db_url(), echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
