from loguru import logger

from application.commands.git import GetTreeCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.exceptions.git import RepositoryNotFoundException
from domain.filters.git import RepositoryFilter
from domain.schemas.repository_storage import GetTreeSchema, TreeNode
from domain.services.repository import RepositoryService
from infrastructure.repositories.repository import RepositoryReader
from infrastructure.storage.git_storage import GitPythonStorage


class GetTreeUseCase(AbstractUseCase[GetTreeCommand]):
    def __init__(self, uow: AbstractUnitOfWork, git_storage: GitPythonStorage) -> None:
        self._uow = uow
        self._git_storage = git_storage

    async def execute(self, command: GetTreeCommand) -> list[TreeNode]:
        logger.bind(use_case=self.__class__.__name__).info("Starting fetching a tree")

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

            tree = await self._git_storage.get_tree(
                GetTreeSchema(repo_path=repository_path, branch_name=command.ref, path=command.path)
            )

            logger.info("Successfully fetched tree for ref: {ref}", ref=command.ref)

            return tree
