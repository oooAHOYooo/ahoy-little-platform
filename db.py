import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/ahoy")

# Create SQLAlchemy engine with pool_pre_ping for resiliency
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Thread-safe scoped session factory
SessionFactory = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
)


@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations.

    Usage:
        with get_session() as session:
            session.query(...)
    """
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


