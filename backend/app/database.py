from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# check_same_thread is only needed for SQLite (local dev/tests); Postgres
# in production ignores this argument entirely, so it's safe to always pass.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency - gives each request its own DB session and always
    closes it afterwards, even if the request raised an error."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
