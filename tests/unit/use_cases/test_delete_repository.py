from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from application.commands.git import DeleteRepositoryCommand
from application.use_cases.git.delete_repository import DeleteRepositoryUseCase
from domain.exceptions.user import UserInactiveException
from domain.services.repository import RepositoryService


@pytest.fixture
def command() -> DeleteRepositoryCommand:
    return DeleteRepositoryCommand(initiator_id=uuid4(), owner_username="username", repository_name="repository")


async def test_delete_repository_success(
    command: DeleteRepositoryCommand,
    mock_uow: AsyncMock,
    mock_git_storage: AsyncMock,
    mock_policy_service: MagicMock,
    mock_user_reader: AsyncMock,
    mock_repository_reader: AsyncMock,
    mock_repository_writer: AsyncMock,
    mock_user: MagicMock,
    mock_repository: MagicMock,
) -> None:
    call_manager = MagicMock()
    call_manager.attach_mock(mock_uow, "uow")
    call_manager.attach_mock(mock_policy_service, "policy")
    call_manager.attach_mock(mock_repository_writer, "writer")
    call_manager.attach_mock(mock_git_storage, "storage")

    use_case = DeleteRepositoryUseCase(
        uow=mock_uow,
        git_storage=mock_git_storage,
        policy_service=mock_policy_service,
        user_reader_factory=lambda _: mock_user_reader,
        repository_reader_factory=lambda _: mock_repository_reader,
        repository_writer_factory=lambda _: mock_repository_writer,
    )

    # Act
    await use_case.execute(command)

    # Assert: order
    expected_order = [
        "uow.__aenter__",
        "policy.can",
        "writer.delete_by_identity",
        "storage.delete_repository",
        "uow.commit",
        "uow.__aexit__",
    ]
    actual_order = [call[0] for call in call_manager.mock_calls]
    assert expected_order == actual_order

    # Assert: correct arguments
    mock_repository_reader.get_by_username_and_repository_name.assert_called_once_with(
        username=command.owner_username, repository_name=command.repository_name
    )

    mock_repository_writer.delete_by_identity.assert_called_once_with(identity=mock_repository.id)

    expected_path = RepositoryService.get_repository_path(user_id=mock_user.id, repository_id=mock_repository.id)
    mock_git_storage.delete_repository.assert_called_once_with(repo_path=expected_path)


async def test_delete_repository_error_no_commit(
    command: DeleteRepositoryCommand,
    mock_uow: AsyncMock,
    mock_git_storage: AsyncMock,
    mock_policy_service: MagicMock,
    mock_user_reader: AsyncMock,
    mock_repository_reader: AsyncMock,
    mock_repository_writer: AsyncMock,
    mock_user: MagicMock,
) -> None:
    mock_user.ensure_active.side_effect = UserInactiveException
    use_case = DeleteRepositoryUseCase(
        uow=mock_uow,
        git_storage=mock_git_storage,
        policy_service=mock_policy_service,
        user_reader_factory=lambda _: mock_user_reader,
        repository_reader_factory=lambda _: mock_repository_reader,
        repository_writer_factory=lambda _: mock_repository_writer,
    )

    with pytest.raises(UserInactiveException):
        await use_case.execute(command)

    mock_uow.commit.assert_not_awaited()
