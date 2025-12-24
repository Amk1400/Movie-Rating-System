from typing import Generator, Optional
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None
Base = declarative_base()


def init_engine(database_url: str) -> None:
    """Initialize SQLAlchemy engine and session factory.

    Args:
        database_url (str): SQLAlchemy database URL.

    Returns:
        None: nothing.

    Raises:
        None: idempotent initializer.
    """
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(database_url, future=True)
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, class_=Session)


def close_engine() -> None:
    """Dispose SQLAlchemy engine if exists.

    Returns:
        None: nothing.

    Raises:
        None: safe no-op if uninitialized.
    """
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
        _engine = None
        _SessionLocal = None


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy Session for manual use.

    Returns:
        Generator[Session, None, None]: yields a session.

    Raises:
        RuntimeError: if sessionmaker is not initialized.
    """
    global _SessionLocal
    if _SessionLocal is None:
        init_engine(
            os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://postgres:secret@localhost:5432/movie_db",
            )
        )
    assert _SessionLocal is not None
    session: Session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_sessionmaker() -> sessionmaker:
    """Return the initialized sessionmaker.

    Returns:
        sessionmaker: session factory.

    Raises:
        RuntimeError: if not initialized.
    """
    global _SessionLocal
    if _SessionLocal is None:
        raise RuntimeError("Sessionmaker is not initialized; call init_engine first")
    return _SessionLocal
