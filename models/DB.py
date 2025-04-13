from models import *
from Config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import logging


logger = logging.getLogger(__name__)

Base = declarative_base()
engine = create_engine(
    f"sqlite:///{Config.DB_PATH}",
    connect_args={"check_same_thread": False},
    pool_size=Config.DB_POOL_SIZE,
    max_overflow=Config.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
)


def init_db():
    # Configure SQLite for better concurrency
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.execute(text("PRAGMA busy_timeout=5000"))

    Base.metadata.create_all(engine)


Session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of database operations.

    Yields:
        Session: A SQLAlchemy database session

    Raises:
        Exception: Any exception that occurs during the transaction will be
                  logged and re-raised after rolling back the transaction.
    """
    session = Session()
    try:
        yield session
        session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        session.rollback()
        logger.error(
            "Database transaction failed", exc_info=True, extra={"exception": str(e)}
        )
    finally:
        session.close()
        logger.debug("Session closed")
