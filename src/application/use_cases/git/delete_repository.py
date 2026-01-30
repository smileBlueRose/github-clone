from typing import Callable

from loguru import logger

from application.commands.git import DeleteRepositoryCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.entities.git import Repository
from domain.entities.user import User
from domain.exceptions.common import PermissionDenied
from domain.ports.session import AsyncSessionP
from domain.services.policy_service import PolicyEngine
from domain.services.repository import RepositoryService
from infrastructure.repositories.repository import RepositoryReader, RepositoryWriter
from infrastructure.repositories.user import UserReadRepository
from infrastructure.storage.git_storage import GitPythonStorage


class DeleteRepositoryUseCase(AbstractUseCase[DeleteRepositoryCommand]):
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        git_storage: GitPythonStorage,
        policy_service: PolicyEngine,
        user_reader_factory: Callable[[AsyncSessionP], UserReadRepository],
        repository_reader_factory: Callable[[AsyncSessionP], RepositoryReader],
        repository_writer_factory: Callable[[AsyncSessionP], RepositoryWriter],
    ) -> None:
        self._uow = uow
        self._storage = git_storage
        self._policy_service = policy_service

        self._user_reader_factory = user_reader_factory
        self._repository_reader_factory = repository_reader_factory
        self._repository_writer_factory = repository_writer_factory

    async def execute(self, command: DeleteRepositoryCommand) -> None:
        """:raises RepositoryNotFoundException:"""

        logger.bind(
            use_case=self.__class__.__name__, user_id=command.initiator_id, repository_name=command.repository_name
        ).info("Starting repository deletion")

        async with self._uow:
            initiator = await self._user_reader_factory(self._uow.session).get_by_identity(command.initiator_id)
            initiator.ensure_active()

            target_repository = await self._repository_reader_factory(
                self._uow.session
            ).get_by_username_and_repository_name(
                username=command.owner_username, repository_name=command.repository_name
            )

            self._check_policy(initiator, target_repository)

            await self._repository_writer_factory(self._uow.session).delete_by_identity(identity=target_repository.id)
            logger.debug("Repository deleted from the database")

            repository_path = RepositoryService.get_repository_path(
                user_id=target_repository.owner_id, repository_id=target_repository.id
            )
            await self._storage.delete_repository(repo_path=repository_path)
            logger.bind(repository_path=repository_path).debug("Repository deleted from the file system")

            await self._uow.commit()

            logger.info("Repository deleted successfully")

    def _check_policy(self, initiator: User, target_repository: Repository) -> None:
        """:raises PermissionDenied:"""

        is_allowed = self._policy_service.can(
            action="repository:delete",
            subject=initiator.to_policy_context(),
            resource=target_repository.to_policy_context(),
        )

        if not is_allowed:
            logger.warning("Permission denied for repository deletion")
            raise PermissionDenied(
                f"User {initiator.email} is not allowed to delete repository {target_repository.name}"
            )
        logger.debug("Policy check passed")
