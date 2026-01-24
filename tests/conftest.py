import os
import sys

if os.getenv("ENV") != "test":
    print("ERROR: ENV must be set to 'test' to run tests")
    sys.exit(1)

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Generator
from unittest.mock import PropertyMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domain.entities.user import User
from infrastructure.database.models.base import Base


def pytest_sessionstart(session: pytest.Session) -> None:
    test_url = "postgresql+asyncpg://user:pass@localhost:5433/test_db"

    patcher_method = patch("src.config.config.DatabaseConfig.read_db_password", return_value="N/A")

    patcher_url = patch(
        "src.config.config.DatabaseConfig.url",
        new_callable=PropertyMock,
        return_value=test_url,
    )

    patcher_method.start()
    patcher_url.start()

    session.db_patchers = [patcher_method, patcher_url]  # type: ignore[attr-defined]


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    db_patchers: list[Any] | None = getattr(session, "db_patchers", None)
    if db_patchers:
        for patcher in db_patchers:
            patcher.stop()


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_secrets_dir(project_root: Path) -> Path:
    return project_root / "tests" / "secrets"


@pytest.fixture(scope="session")
def test_images_dir(project_root: Path) -> Path:
    return project_root / "tests" / "images"


@pytest.fixture(scope="session")
def private_key(test_secrets_dir: Path) -> str:
    return (test_secrets_dir / "test-private.pem").read_text()


@pytest.fixture(scope="session")
def another_private_key(test_secrets_dir: Path) -> str:
    return (test_secrets_dir / "another-private.pem").read_text()


@pytest.fixture(scope="session")
def public_key(test_secrets_dir: Path) -> str:
    return (test_secrets_dir / "test-public.pem").read_text()


@pytest.fixture(scope="session")
def another_public_key(test_secrets_dir: Path) -> str:
    return (test_secrets_dir / "another-public.pem").read_text()


@pytest.fixture
def user() -> User:
    return User(
        id=uuid4(),
        email="test@example.com",
        username="scarlet-scarf",
        password_hash="$2b$12$6rEUV1t6EHbC.HnelrKE9OntR1MUITbOJqteguORQ0un0CIRu/EzS",
    )


@pytest.fixture(scope="function")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def session(
    event_loop: asyncio.AbstractEventLoop,
) -> AsyncGenerator[AsyncSession, None]:
    test_url = "postgresql+asyncpg://user:pass@localhost:5433/test_db"

    engine = create_async_engine(test_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with sessionmaker() as session:
        yield session
        await session.rollback()

    await engine.dispose()
