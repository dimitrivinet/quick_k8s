from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
import sqlalchemy.exc

from app.database.orm import Base
from app.config import cfg
from app import database
from app.utils import auth

_engine: Engine
_session = sessionmaker(autocommit=False, expire_on_commit=True)


def setup_engine(url: str, echo: bool = False) -> Engine:
    """Sets up engine with provided url. Set echo to True if you want
    commands sent to database to be echoed in terminal."""

    global _engine

    _engine = create_engine(url, echo=echo)
    _session.configure(bind=_engine)


def create_tables():
    """Creates tables as registered in orm.py.
    Doesn't change anything if tables already exist."""

    if _engine is None:
        raise ValueError(
            "Engine is not setup. Call setup_engine() before create_tables()."
        )

    Base.metadata.create_all(_engine)


def get_session() -> Session:
    """Returns a session to interact with the database. Expires after each commit."""

    if _engine is None:
        raise ValueError(
            "Engine is not setup. Call setup_engine() before get_session()."
        )

    session = _session()

    return session
