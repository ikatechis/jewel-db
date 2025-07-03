from sqlmodel import Session, create_engine

from .settings import settings

_engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)


def get_engine():
    """Return the singleton SQLModel engine (override in tests if needed)."""
    return _engine


def get_session():
    """
    FastAPI dependency that yields a scoped Session
    and closes it afterwards.
    """
    with Session(_engine) as session:
        yield session
