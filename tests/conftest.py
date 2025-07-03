# tests/conftest.py
import pathlib
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from jewel_db.core.dependencies import get_db
from jewel_db.core.models_import import import_models
from jewel_db.main import app


# ── Engine & temp DB file ────────────────────────────────────────────────
@pytest.fixture(scope="session")
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield pathlib.Path(d)


@pytest.fixture(scope="session")
def engine(tmp_dir):
    url = f"sqlite:///{tmp_dir}/test.db"
    engine = create_engine(url, echo=False)

    # discover ORM classes then create tables once
    import_models()
    SQLModel.metadata.create_all(engine)
    return engine


# ── FastAPI test client with per-request Session ─────────────────────────
@pytest.fixture(scope="function")
def client(engine):
    """
    Override FastAPI's DB dependency so that *each* HTTP request handled
    by the TestClient gets its own short-lived Session—mirroring production
    behaviour and preventing SQLAlchemy identity-map warnings.
    """

    def _get_test_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
