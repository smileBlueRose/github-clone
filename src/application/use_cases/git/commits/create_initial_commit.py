from typing import Any

from loguru import logger

from application.commands.git import CreateInitialCommitCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.entities.git import Repository
from domain.entities.user import User
from domain.exceptions.common import PermissionDenied
from domain.exceptions.git import (
    RepositoryAlreadyInitializedException,
    RepositoryNotFoundException,
)
from domain.filters.git import RepositoryFilter
from domain.schemas.repository_storage import UpdateFileSchema
from domain.services.policy_service import PolicyEngine
from domain.services.repository import RepositoryService
from domain.value_objects.git import Author
from infrastructure.repositories.repository import RepositoryReader
from infrastructure.repositories.user import UserReadRepository
from infrastructure.storage.git_storage import GitPythonStorage


class CreateInitialCommitUseCase(AbstractUseCase[CreateInitialCommitCommand]):
    def __init__(self, uow: AbstractUnitOfWork, git_storage: GitPythonStorage, policy_service: PolicyEngine) -> None:
        self._uow = uow
        self._git_storage = git_storage
        self._policy_service = policy_service

    async def execute(self, command: CreateInitialCommitCommand) -> Any:
        logger.bind(use_case=self.__class__.__name__, command=command).info("Starting creating initial commit")
        # TODO: refactor it, repeating code of fetching repository & initiator (same code in create branch use case)
        # I think it's good to use inheritance for repository & commit use cases

        async with self._uow:
            user_reader = UserReadRepository(session=self._uow.session)
            repository_reader = RepositoryReader(session=self._uow.session)

            initiator = await user_reader.get_by_identity(command.initiator_id)
            logger.bind(email=initiator.email).debug("Initiator fetched")

            result = await repository_reader.get_all(
                RepositoryFilter(username=command.owner_username, repository_name=command.repository_name)
            )
            if not result:
                logger.info("Repository not found")
                raise RepositoryNotFoundException(
                    username=command.owner_username, repository_name=command.repository_name
                )
            repository = result[0]
            logger.bind(repository_id=repository.id).debug("Repository found")

            repository_path = RepositoryService(repository_reader).get_repository_path(
                user_id=repository.owner_id, repository_id=repository.id
            )

            if await self._git_storage.get_branches(repository_path):
                raise RepositoryAlreadyInitializedException(repository_name=command.repository_name)

            self.check_permissions(initiator, repository)

            schema = UpdateFileSchema(
                repo_path=repository_path,
                file_path="README.md",
                content=f"# {repository.name}\n\nInitial commit",
                encoding="utf-8",
                message=command.msg,
                branch_name=command.branch_name,
                author=Author(name=initiator.username, email=initiator.email),
            )
            commit = await self._git_storage.update_file(schema)
            logger.bind(commit=commit).info("Initial commit created")

            return commit

    def check_permissions(self, user: User, repository: Repository) -> None:
        """:raises PermissionDenied:"""

        is_allowed: bool = self._policy_service.can(
            action="repository:commit",
            subject=user.to_policy_context(),
            resource=repository.to_policy_context(),
        )

        if not is_allowed:
            logger.warning("Permission denied for comitting")
            raise PermissionDenied(f"User {user.email} is not allowed to commit to the repository {repository.name}")
        logger.debug("Policy check passed")

        return None
