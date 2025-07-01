# jewel_db/db.py

from sqlmodel import Session, SQLModel, create_engine

from .config import DATABASE_URL, DEBUG

engine = create_engine(
    DATABASE_URL,
    echo=DEBUG,
    connect_args={"check_same_thread": False},
)


def init_db():
    # import all models for metadata

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
