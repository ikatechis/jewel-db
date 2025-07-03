from fastapi import Depends
from sqlmodel import Session

from .database import get_session
from .settings import Settings, settings


def get_settings() -> Settings:
    return settings


def get_db(session: Session = Depends(get_session)) -> Session:  # re-export
    return session
