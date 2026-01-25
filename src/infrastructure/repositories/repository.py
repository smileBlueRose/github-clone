from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.git import Repository
from domain.exceptions.git import RepositoryNotFoundException
from domain.filters.git import RepositoryFilter
from domain.ports.repositories.git_repo import (
    AbstractRepositoryReader,
    AbstractRepositoryWriter,
)
from domain.schemas.repository_storage import RepositoryCreateSchema, RepositoryUpdateSchema
from infrastructure.database.models.repository import RepositoryModel


class RepositoryWriter(AbstractRepositoryWriter):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, schema: RepositoryCreateSchema) -> Repository:
        repo_model = RepositoryModel(
            name=schema.name,
            owner_id=schema.owner_id,
            description=schema.description,
        )
        self._session.add(repo_model)
        await self._session.flush()
        return repo_model.to_entity()

    async def update(self, identity: UUID, schema: RepositoryUpdateSchema) -> Repository:
        repo_model = await self._session.get(RepositoryModel, identity)
        if repo_model is None:
            raise RepositoryNotFoundException(repo_id=identity)

        if schema.name is not None:
            repo_model.name = schema.name
        if schema.description is not None:
            repo_model.description = schema.description

        await self._session.flush()
        return repo_model.to_entity()

    async def delete_by_identity(self, identity: UUID) -> bool:
        repo_model = await self._session.get(RepositoryModel, identity)

        if repo_model is None:
            return False

        await self._session.delete(repo_model)
        await self._session.flush()
        return True


class RepositoryReader(AbstractRepositoryReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_identity(self, identity: UUID) -> Repository:
        """:raises GitRepositoryNotFoundException:"""

        repo_model = await self._session.get(RepositoryModel, identity)

        if repo_model is None:
            raise RepositoryNotFoundException(repo_id=identity)

        return repo_model.to_entity()

    async def get_all(self, filter_: RepositoryFilter) -> list[Repository]:
        stmt = select(RepositoryModel)

        result = await self._session.execute(stmt)
        return [i.to_entity() for i in result.scalars().all()]
