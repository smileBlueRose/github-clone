import os
import sys

if os.getenv("ENV") != "test":
    print("ERROR: ENV must be set to 'test' to run tests")
    sys.exit(1)

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings
from domain.entities.user import User
from infrastructure.database.models.base import Base


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
    engine = create_async_engine(str(settings.db.url), echo=False)

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
