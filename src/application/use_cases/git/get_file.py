from loguru import logger

from application.commands.git import GetFileCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.exceptions.git import RepositoryNotFoundException
from domain.filters.git import RepositoryFilter
from domain.schemas.repository_storage import FileContent, GetFileSchema
from domain.services.repository import RepositoryService
from infrastructure.repositories.repository import RepositoryReader
from infrastructure.storage.git_storage import GitPythonStorage


class GetFileUseCase(AbstractUseCase[GetFileCommand]):
    def __init__(self, uow: AbstractUnitOfWork, git_storage: GitPythonStorage) -> None:
        self._uow = uow
        self._git_storage = git_storage

    async def execute(self, command: GetFileCommand) -> FileContent:
        logger.bind(use_case=self.__class__.__name__).info("Starting fetching the file")

        async with self._uow:

            result = await RepositoryReader(session=self._uow.session).get_all(
                RepositoryFilter(username=command.owner_username, repository_name=command.repository_name)
            )
            if not result:
                logger.info("Repository not found")
                raise RepositoryNotFoundException(
                    username=command.owner_username, repository_name=command.repository_name
                )
            logger.debug("Repository found")

            repository = result[0]
            repository_path = RepositoryService.get_repository_path(
                user_id=repository.owner_id, repository_id=repository.id
            )
            file_content = await self._git_storage.get_file(
                GetFileSchema(repo_path=repository_path, file_path=command.file_path, branch_name=command.ref)
            )

            logger.info("File fetched")
            return file_content
