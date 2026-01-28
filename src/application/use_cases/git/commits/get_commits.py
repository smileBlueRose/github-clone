from typing import Any

from loguru import logger

from application.commands.git import GetCommitsCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.exceptions.git import RepositoryNotFoundException
from domain.filters.git import RepositoryFilter
from domain.schemas.repository_storage import GetCommitsSchema
from domain.services.repository import RepositoryService
from infrastructure.repositories.repository import RepositoryReader
from infrastructure.storage.git_storage import GitPythonStorage


class GetCommitsUseCase(AbstractUseCase[GetCommitsCommand]):
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        git_storage: GitPythonStorage,
    ) -> None:
        self._uow = uow
        self._git_storage = git_storage

    async def execute(self, command: GetCommitsCommand) -> Any:
        logger.bind(use_case=self.__class__.__name__, command=command).info("Starting fethcing commits")

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

            commits = await self._git_storage.get_commits(
                schema=GetCommitsSchema(
                    repo_path=repository_path,
                    branch_name=command.branch_name,
                )
            )
            logger.debug(f"Found {len(commits)} commits")

            return commits
