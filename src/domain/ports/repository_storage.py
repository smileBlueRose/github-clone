from abc import ABC, abstractmethod

from domain.schemas.repository_storage import CommitResult, CommitSchema, CreateBranchSchema, InitRepositorySchema


class AbstractRepositoryStorage(ABC):
    @abstractmethod
    async def init_repository(self, schema: InitRepositorySchema) -> None:
        pass

    @abstractmethod
    async def commit(self, schema: CommitSchema) -> CommitResult:
        pass

    @abstractmethod
    async def create_branch(self, schema: CreateBranchSchema) -> None:
        pass
