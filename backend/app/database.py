from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings


def _build_database_url(url: str) -> str:
    """Convierte mysql:// a mysql+pymysql:// (Railway entrega el URL sin dialecto)."""
    if url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+pymysql://", 1)
    return url


_db_url = _build_database_url(settings.DATABASE_URL)

engine = create_engine(
    _db_url,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import user, trip  # noqa: F401
    Base.metadata.create_all(bind=engine)
