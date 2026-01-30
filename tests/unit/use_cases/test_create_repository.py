from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from application.commands.git import CreateRepositoryCommand
from application.use_cases.git.create_repository import CreateRepositoryUseCase
from domain.exceptions.git import RepositoryAlreadyExistsException


@pytest.fixture
def command() -> CreateRepositoryCommand:
    return CreateRepositoryCommand(repository_name="test-repo", user_id=uuid4(), description="Test description")


async def test_create_repository_success(
    command: CreateRepositoryCommand,
    mock_repository: MagicMock,
    mock_repository_service: AsyncMock,
    mock_repository_writer: AsyncMock,
    mock_git_storage: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    # Arrange
    call_manager = MagicMock()
    call_manager.attach_mock(mock_uow, "uow")
    call_manager.attach_mock(mock_repository_service, "service")
    call_manager.attach_mock(mock_repository_writer, "writer")
    call_manager.attach_mock(mock_git_storage, "storage")

    use_case = CreateRepositoryUseCase(
        uow=mock_uow,
        git_storage=mock_git_storage,
        writer_factory=lambda _: mock_repository_writer,
        repository_service_factory=lambda _: mock_repository_service,
    )

    # Act
    result = await use_case.execute(command=command)

    # Assert: operations order
    expected_order = [
        "uow.__aenter__",
        "service.check_repository_name",
        "writer.create",
        "service.get_repository_path",
        "storage.init_repository",
        "uow.commit",
        "uow.__aexit__",
    ]

    actual_order = [call[0] for call in call_manager.mock_calls]
    assert expected_order == actual_order

    # Assert: returned value
    assert result == mock_repository


async def test_create_repository_error_no_commit(
    command: CreateRepositoryCommand,
    mock_repository_service: AsyncMock,
    mock_repository_writer: AsyncMock,
    mock_git_storage: AsyncMock,
    mock_uow: AsyncMock,
) -> None:
    # Arrange
    mock_repository_service.check_repository_name.side_effect = RepositoryAlreadyExistsException(
        repository_name=command.repository_name
    )

    use_case = CreateRepositoryUseCase(
        uow=mock_uow,
        git_storage=mock_git_storage,
        writer_factory=lambda _: mock_repository_writer,
        repository_service_factory=lambda _: mock_repository_service,
    )

    # Act & Assert
    with pytest.raises(RepositoryAlreadyExistsException):
        await use_case.execute(command)

    mock_uow.commit.assert_not_awaited()
