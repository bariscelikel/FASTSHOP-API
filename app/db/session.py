from collections.abc import Iterator
import sqlite3

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(connection: sqlite3.Connection, _: object) -> None:
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db_and_tables() -> None:
    from app.models import Category, Product

    SQLModel.metadata.create_all(
        engine, tables=[Category.__table__, Product.__table__]
    )


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
