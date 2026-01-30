from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from application.commands.git import CreateRepositoryCommand
from application.ports.uow import AbstractUnitOfWork
from application.use_cases.git.create_repository import CreateRepositoryUseCase
from domain.entities.git import Repository
from domain.exceptions.git import RepositoryAlreadyExistsException
from domain.ports.repositories.git_repo import AbstractRepositoryWriter
from domain.ports.repository_storage import AbstractRepositoryStorage
from domain.services.repository import RepositoryService


@pytest.fixture
def command() -> CreateRepositoryCommand:
    return CreateRepositoryCommand(repository_name="test-repo", user_id=uuid4(), description="Test description")


SERVICE = RepositoryService
WRITER = AbstractRepositoryWriter
STORAGE = AbstractRepositoryStorage
UOW = AbstractUnitOfWork


async def test_create_repository_success(
    command: CreateRepositoryCommand,
    repository_entity: Repository,
    mock_repository_service: AsyncMock,
    mock_repository_writer: AsyncMock,
    mock_git_storage: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    manager = MagicMock()
    manager.attach_mock(mock_repository_service, str(SERVICE))
    manager.attach_mock(mock_repository_writer, str(WRITER))
    manager.attach_mock(mock_git_storage, str(STORAGE))
    manager.attach_mock(mock_uow, str(UOW))

    use_case = CreateRepositoryUseCase(
        uow=mock_uow,
        git_storage=mock_git_storage,
        writer_factory=lambda *args: mock_repository_writer,
        repository_service_factory=lambda *args: mock_repository_service,
    )
    assert repository_entity == await use_case.execute(command=command)

    expected_calls = [
        f"{UOW}.{UOW.__aenter__.__name__}",
        f"{SERVICE}.{SERVICE.check_repository_name.__name__}",
        f"{WRITER}.{WRITER.create.__name__}",
        f"{SERVICE}.{SERVICE.get_repository_path.__name__}",
        f"{STORAGE}.{STORAGE.init_repository.__name__}",
        f"{UOW}.{UOW.commit.__name__}",
        f"{UOW}.{UOW.__aexit__.__name__}",
    ]

    actual_calls = [i[0] for i in manager.mock_calls]

    assert expected_calls == actual_calls


@pytest.mark.asyncio
async def test_create_repository_error_no_commit(
    command: CreateRepositoryCommand,
    mock_repository_service: AsyncMock,
    mock_repository_writer: AsyncMock,
    mock_git_storage: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    mock_repository_service.check_repository_name.side_effect = RepositoryAlreadyExistsException(
        repository_name=command.repository_name
    )

    use_case = CreateRepositoryUseCase(
        uow=mock_uow,
        git_storage=mock_git_storage,
        writer_factory=lambda session: mock_repository_writer,
        repository_service_factory=lambda session: mock_repository_service,
    )

    with pytest.raises(RepositoryAlreadyExistsException):
        await use_case.execute(command)

    mock_uow.commit.assert_not_awaited()
