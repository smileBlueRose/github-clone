from typing import Any

from loguru import logger

from application.commands.git import GetBranchesCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.exceptions.git import RepositoryNotFoundException
from domain.filters.git import RepositoryFilter
from domain.services.repository import RepositoryService
from infrastructure.repositories.repository import RepositoryReader
from infrastructure.repositories.user import UserReadRepository
from infrastructure.storage.git_storage import GitPythonStorage


class GetBranchesUseCase(AbstractUseCase[GetBranchesCommand]):
    def __init__(self, uow: AbstractUnitOfWork, git_storage: GitPythonStorage) -> None:
        self._uow = uow
        self._storage = git_storage

    async def execute(self, command: GetBranchesCommand) -> Any:
        """:raises RepositoryNotFoundException:"""

        logger.bind(use_case=self.__class__.__name__, command=command)
        async with self._uow:
            user_reader = UserReadRepository(session=self._uow.session)
            user = await user_reader.get_by_username(username=command.username)

            repository_reader = RepositoryReader(session=self._uow.session)
            result = await repository_reader.get_all(
                RepositoryFilter(username=command.username, repository_name=command.repository_name),
            )

            if not result:
                logger.debug("Repository not found")
                raise RepositoryNotFoundException(username=command.username, repository_name=command.repository_name)
            repository = result[0]
            logger.bind(repository_id=repository.id).debug("Repository found")

            repository_service = RepositoryService(reader=repository_reader)
            repository_path = repository_service.get_repository_path(user_id=user.id, repository_id=repository.id)

            branches = await self._storage.get_branches(repo_path=repository_path)
            logger.bind(repository_path=repository_path).debug(f"Found {len(branches)} branches")

            return branches
