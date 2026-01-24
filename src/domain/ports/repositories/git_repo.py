from abc import abstractmethod
from uuid import UUID

from domain.entities.git import Repository
from domain.filters.git import GitRepoFilter
from domain.ports.repository import AbstractReadRepository, AbstractWriteRepository
from domain.schemas.repository_storage import GitRepoCreateSchema, GitRepoUpdateSchema


class AbstractGitRepoReadRepository(AbstractReadRepository[Repository, UUID, GitRepoFilter]):
    @abstractmethod
    async def get_by_identity(self, identity: UUID) -> Repository:
        """:raises GitRepositoryNotFoundException:"""

    @abstractmethod
    async def get_all(self, filter_: GitRepoFilter) -> list[Repository]:
        pass


class AbstractGitRepoWriteRepository(
    AbstractWriteRepository[Repository, GitRepoCreateSchema, GitRepoUpdateSchema, UUID]
):
    @abstractmethod
    async def create(self, schema: GitRepoCreateSchema) -> Repository:
        pass

    @abstractmethod
    async def update(self, identity: UUID, schema: GitRepoUpdateSchema) -> Repository:
        """:raises RepositoryNotFoundException:"""

        pass

    @abstractmethod
    async def delete_by_identity(self, identity: UUID) -> bool:
        pass
