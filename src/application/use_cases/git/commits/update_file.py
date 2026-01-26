import base64

from loguru import logger

from application.commands.git import UpdateFileCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.exceptions.common import PermissionDenied
from domain.exceptions.git import RepositoryNotFoundException
from domain.filters.git import RepositoryFilter
from domain.schemas.repository_storage import UpdateFileSchema
from domain.services.policy_service import PolicyEngine
from domain.services.repository import RepositoryService
from domain.value_objects.git import Author, CommitInfo
from infrastructure.repositories.repository import RepositoryReader
from infrastructure.repositories.user import UserReadRepository
from infrastructure.storage.git_storage import GitPythonStorage


class UpdateFileUseCase(AbstractUseCase[UpdateFileCommand]):
    def __init__(self, uow: AbstractUnitOfWork, git_storage: GitPythonStorage, policy_service: PolicyEngine) -> None:
        self._uow = uow
        self._git_storage = git_storage
        self._policy_service = policy_service

    async def execute(self, command: UpdateFileCommand) -> CommitInfo:
        logger.bind(
            user_id=command.user_id,
            use_case=self.__class__.__name__,
            repository_name=command.repo_name,
            branch_name=command.branch_name,
            file_path=command.file_path,
            file_size=len(command.data),
        ).info("Start updating file")

        async with self._uow:
            # TODO: optimize this convertion
            try:
                content = command.data.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                content = base64.b64encode(command.data).decode("ascii")
                encoding = "base64"
            logger.debug(f"{encoding = }")

            user = await UserReadRepository(self._uow.session).get_by_identity(identity=command.user_id)

            reader = RepositoryReader(session=self._uow.session)
            result = await reader.get_all(
                RepositoryFilter(username=command.username, repository_name=command.repo_name)
            )

            if not result:
                raise RepositoryNotFoundException(username=command.username, repository_name=command.repo_name)
            repository = result[0]

            is_allowed = self._policy_service.can(
                action="repository:commit",
                subject=user.to_policy_context(),
                resource=repository.to_policy_context(),
            )
            if not is_allowed:
                logger.warning("Permission denied for comitting to repository")
                raise PermissionDenied(f"User {user.email} is not allowed to commit to repository '{repository.name}'")
            logger.debug("User allowed to commit")

            repository_service = RepositoryService(reader=reader)
            repository_path = repository_service.get_repository_path(
                user_id=command.user_id, repository_id=repository.id
            )
            logger.debug(f"{repository_path = }")

            schema = UpdateFileSchema(
                repo_path=repository_path,
                file_path=command.file_path,
                content=content,
                encoding=encoding,
                message=command.message,
                branch_name=command.branch_name,
                author=Author(name=user.username, email=user.email),
            )
            commit = await self._git_storage.update_file(schema)

            logger.bind(commit=commit).info("File updated successfully")

            return commit
