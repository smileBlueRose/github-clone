from abc import abstractmethod
from uuid import UUID

from domain.entities.git import Repository
from domain.filters.git import RepositoryFilter
from domain.ports.repository import AbstractReadRepository, AbstractWriteRepository
from domain.schemas.repository_storage import RepositoryCreateSchema, RepositoryUpdateSchema


class AbstractRepositoryReader(AbstractReadRepository[Repository, UUID, RepositoryFilter]):
    @abstractmethod
    async def get_by_identity(self, identity: UUID) -> Repository:
        """:raises GitRepositoryNotFoundException:"""

    @abstractmethod
    async def get_all(self, filter_: RepositoryFilter) -> list[Repository]:
        pass


class AbstractRepositoryWriter(
    AbstractWriteRepository[Repository, RepositoryCreateSchema, RepositoryUpdateSchema, UUID]
):
    @abstractmethod
    async def create(self, schema: RepositoryCreateSchema) -> Repository:
        pass

    @abstractmethod
    async def update(self, identity: UUID, schema: RepositoryUpdateSchema) -> Repository:
        """:raises RepositoryNotFoundException:"""

        pass

    @abstractmethod
    async def delete_by_identity(self, identity: UUID) -> bool:
        pass
