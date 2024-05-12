"""TODO."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine
from sqlmodel import (
    Session,
    SQLModel,
    create_engine,
)

from vk_extract_audio_bot.settings import (
    CONFIG,
)


engine: Engine = create_engine(CONFIG.DB_URL)


def init_db() -> None:
    """Инициализация БД."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Создание сессии для взаимодействия с БД."""
    session: Session = None
    try:
        session = Session(engine)
        yield session
    finally:
        session.close()
