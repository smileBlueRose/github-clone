from loguru import logger

from application.commands.git import DeleteRepositoryCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.exceptions.common import PermissionDenied
from domain.exceptions.git import RepositoryNotFoundException
from domain.filters.git import RepositoryFilter
from domain.services.policy_service import PolicyEngine
from domain.services.repository import RepositoryService
from infrastructure.repositories.repository import RepositoryReader, RepositoryWriter
from infrastructure.repositories.user import UserReadRepository
from infrastructure.storage.git_storage import GitPythonStorage


class DeleteRepositoryUseCase(AbstractUseCase[DeleteRepositoryCommand]):
    def __init__(self, uow: AbstractUnitOfWork, git_storage: GitPythonStorage, policy_service: PolicyEngine) -> None:
        self._uow = uow
        self._storage = git_storage
        self._policy_service = policy_service

    async def execute(self, command: DeleteRepositoryCommand) -> None:
        """:raises RepositoryNotFoundException:"""

        logger.bind(
            use_case=self.__class__.__name__, user_id=command.user_id, repository_name=command.repository_name
        ).info("Starting repository deletion")

        async with self._uow:
            user = await UserReadRepository(session=self._uow.session).get_by_identity(command.user_id)

            if not user.is_active:
                logger.warning("Deletion failed: user is disabled")
                raise PermissionDenied("User is disabled")

            reader = RepositoryReader(session=self._uow.session)
            result = await reader.get_all(
                RepositoryFilter(username=command.username, repository_name=command.repository_name)
            )

            if not result:
                logger.debug("Repository not found for deletion")
                raise RepositoryNotFoundException(username=command.username, repository_name=command.repository_name)

            repository = result[0]
            is_allowed: bool = self._policy_service.can(
                action="repository:delete",
                subject=user.to_policy_context(),
                resource=repository.to_policy_context(),
            )
            if not is_allowed:
                logger.warning("Permission denied for repository deletion")
                raise PermissionDenied(f"User {user.email} is not allowed to delete repository {repository.name}")

            logger.debug("Policy check passed")

            writer = RepositoryWriter(session=self._uow.session)
            await writer.delete_by_identity(identity=repository.id)
            logger.debug("Repository deleted from the database")

            service = RepositoryService(reader=reader)
            repository_path = service.get_repository_path(user_id=user.id, repository_id=repository.id)
            await self._storage.delete_repository(repo_path=repository_path)
            logger.bind(repository_path=repository_path).debug("Repository deleted from the file system")

            await self._uow.commit()

            logger.info("Repository deleted successfully")
