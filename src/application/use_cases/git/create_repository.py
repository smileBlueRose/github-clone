from typing import Callable

from loguru import logger

from application.commands.git import CreateRepositoryCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from domain.entities.git import Repository
from domain.ports.session import AsyncSessionP
from domain.schemas.repository_storage import InitRepositorySchema, RepositoryCreateSchema
from domain.services.repository import RepositoryService
from infrastructure.repositories.repository import RepositoryWriter
from infrastructure.storage.git_storage import GitPythonStorage


class CreateRepositoryUseCase(AbstractUseCase[CreateRepositoryCommand]):
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        git_storage: GitPythonStorage,
        writer_factory: Callable[[AsyncSessionP], RepositoryWriter],
        repository_service_factory: Callable[[AsyncSessionP], RepositoryService],
    ) -> None:
        self._uow = uow
        self._git_storage = git_storage
        self._writer_factory = writer_factory
        self._repository_service_factory = repository_service_factory

    async def execute(self, command: CreateRepositoryCommand) -> Repository:
        logger.bind(use_case=self.__class__.__name__).info("Starting repository creation")

        async with self._uow:
            service = self._repository_service_factory(self._uow.session)

            await service.check_repository_name(command.user_id, command.repository_name)
            logger.debug("Name has been checked")

            writer = self._writer_factory(self._uow.session)
            repository_entity = await writer.create(
                RepositoryCreateSchema(
                    name=command.repository_name, owner_id=command.user_id, description=command.description
                )
            )
            logger.bind(repository_id=repository_entity.id).debug("Repository entity created")

            repository_path = service.get_repository_path(user_id=command.user_id, repository_id=repository_entity.id)
            await self._git_storage.init_repository(schema=InitRepositorySchema(repo_path=repository_path))
            logger.bind(repository_path=repository_path).debug("Repository initialized in the file system")

            await self._uow.commit()

            logger.info("Repository created successfully")
            return repository_entity
