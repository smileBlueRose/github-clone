from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from application.ports.uow import AbstractUnitOfWork
from domain.entities.git import Repository
from domain.ports.session import AsyncSessionP
from domain.services.repository import RepositoryService
from infrastructure.repositories.repository import RepositoryWriter
from infrastructure.storage.git_storage import GitPythonStorage


@pytest.fixture
def repository_entity() -> Repository:
    return Repository(
        id=uuid4(),
        name="test-repo",
        owner_id=uuid4(),
        description="Test description",
        created_at=datetime.now(UTC),
        updated_at=None,
    )


@pytest.fixture
def mock_repository_service() -> AsyncMock:
    service = AsyncMock(spec=RepositoryService)
    service.get_repository_path = MagicMock(return_value="user_123/repository_456")
    service.check_repository_name = AsyncMock()
    return service


@pytest.fixture
def mock_repository_writer(repository_entity: Repository) -> AsyncMock:
    writer = AsyncMock(spec=RepositoryWriter)
    writer.create.return_value = repository_entity
    return writer


@pytest.fixture
def mock_git_storage() -> AsyncMock:
    return AsyncMock(spec=GitPythonStorage)


@pytest.fixture
def mock_uow() -> AsyncMock:
    uow = AsyncMock(spec=AbstractUnitOfWork)
    uow.session = AsyncMock(spec=AsyncSessionP)

    return uow
