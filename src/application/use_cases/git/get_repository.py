from loguru import logger

from application.commands.git import GetRepositoryCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.entities.git import Repository
from domain.filters.git import RepositoryFilter
from infrastructure.repositories.repository import RepositoryReader


class GetRepositoryUseCase(AbstractUseCase[GetRepositoryCommand]):
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: GetRepositoryCommand) -> list[Repository]:
        logger.bind(use_case=self.__class__.__name__, command=command).info("Starting fetching a repository")

        async with self._uow:
            reader = RepositoryReader(session=self._uow.session)

            result = await reader.get_all(
                filter_=RepositoryFilter(
                    username=command.username,
                    repository_name=command.repository_name,
                    user_id=command.user_id,
                ),
                pagination=command.pagination,
            )
            logger.debug(f"Found {len(result)} repositories")

            return result
