from collections.abc import Generator

from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db as _get_db


def init_db() -> None:
    """
    Ensure all tables are created.
    """
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Thin wrapper around the legacy get_db to keep imports consistent.
    """
    yield from _get_db()


