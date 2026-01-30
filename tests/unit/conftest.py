from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from application.ports.uow import AbstractUnitOfWork
from domain.entities.user import User
from domain.ports.repositories.git_repo import AbstractRepositoryReader
from domain.ports.session import AsyncSessionP
from domain.services.repository import RepositoryService
from infrastructure.repositories.repository import RepositoryWriter
from infrastructure.repositories.user import UserReadRepository
from infrastructure.storage.git_storage import GitPythonStorage


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.id = uuid4()

    return user


@pytest.fixture
def mock_repository(mock_user: MagicMock) -> MagicMock:
    repository = MagicMock()
    repository.id = uuid4()
    repository.owner_id = mock_user.id

    return repository


@pytest.fixture
def mock_repository_service() -> AsyncMock:
    service = AsyncMock(spec=RepositoryService)
    service.get_repository_path = MagicMock(return_value="user_123/repository_456")
    service.check_repository_name = AsyncMock()

    return service


@pytest.fixture
def mock_repository_reader(mock_repository: MagicMock) -> AsyncMock:
    reader = AsyncMock(spec=AbstractRepositoryReader)
    reader.get_by_username_and_repository_name.return_value = mock_repository

    return reader


@pytest.fixture
def mock_repository_writer(mock_repository: MagicMock) -> AsyncMock:
    writer = AsyncMock(spec=RepositoryWriter)
    writer.create.return_value = mock_repository

    return writer


@pytest.fixture
def mock_user_reader(mock_user: MagicMock) -> AsyncMock:
    reader = AsyncMock(spec=UserReadRepository)
    reader.get_by_identity.return_value = mock_user
    return reader


@pytest.fixture
def mock_git_storage() -> AsyncMock:
    return AsyncMock(spec=GitPythonStorage)


@pytest.fixture
def mock_uow() -> AsyncMock:
    uow = AsyncMock(spec=AbstractUnitOfWork)
    uow.session = AsyncMock(spec=AsyncSessionP)

    return uow


@pytest.fixture
def mock_policy_service() -> MagicMock:
    service = MagicMock()
    service.can.return_value = True

    return service
