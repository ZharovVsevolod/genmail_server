from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from sqlalchemy import create_engine
from os import environ
from contextlib import contextmanager

class PGHandler:
    def __init__(self) -> None:
        uri = environ.get(
            "POSTGRES_URI",
            f"postgresql://{environ['POSTGRES_USER']}:{environ['POSTGRES_PASSWORD']}@postgres/{environ['POSTGRES_DB_NAME']}",
        )
        self.engine = create_engine(uri)
        self.Base = declarative_base()
        self.SessionLocal = sessionmaker(self.engine)

    def create_tables(self) -> None:
        self.Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # For FastAPI's Depends    
    def get_session_dep(self):
        return self.get_session()
