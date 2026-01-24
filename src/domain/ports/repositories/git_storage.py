from abc import abstractmethod
from pathlib import Path

from domain.entities.git import Repository
from domain.filters.git import GitRepoFilter
from domain.ports.repository import AbstractReadRepository, AbstractWriteRepository
from domain.schemas.repository_storage import GitRepoCreateSchema, GitRepoUpdateSchema


class AbstractGitRepoReadRepository(AbstractReadRepository[Repository, Path, GitRepoFilter]):
    @abstractmethod
    async def get_by_identity(self, identity: Path) -> Repository:
        return await super().get_by_identity(identity)

    @abstractmethod
    async def get_all(self, filter_: GitRepoFilter) -> list[Repository]:
        return await super().get_all(filter_)


class AbstractGitRepoWriteRepository(
    AbstractWriteRepository[Repository, GitRepoCreateSchema, GitRepoUpdateSchema, Path]
):
    @abstractmethod
    async def create(self, schema: GitRepoCreateSchema) -> Repository:
        pass

    @abstractmethod
    async def update(self, identity: Path, schema: GitRepoUpdateSchema) -> Repository:
        pass

    @abstractmethod
    async def delete_by_identity(self, identity: Path) -> bool:
        pass
