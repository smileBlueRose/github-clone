from abc import ABC, abstractmethod

from domain.schemas.repository_storage import (
    CreateBranchSchema,
    DeleteBranchSchema,
    DeleteFileSchema,
    FileContent,
    GetCommitsSchema,
    GetFileSchema,
    GetRefsSchema,
    InitRepositorySchema,
    UpdateFileSchema,
)
from domain.value_objects.git import BranchInfo, CommitInfo, Repository


class AbstractRepositoryStorage(ABC):
    @abstractmethod
    async def init_repository(self, schema: InitRepositorySchema) -> Repository:
        pass

    @abstractmethod
    async def delete_repository(self, repo_path: str) -> None:
        pass

    @abstractmethod
    async def repository_exists(self, repo_path: str) -> bool:
        pass

    @abstractmethod
    async def create_branch(self, schema: CreateBranchSchema) -> None:
        pass

    @abstractmethod
    async def delete_branch(self, schema: DeleteBranchSchema) -> None:
        pass

    @abstractmethod
    async def get_branches(self, repo_path: str) -> list[BranchInfo]:
        pass

    @abstractmethod
    async def get_commits(self, schema: GetCommitsSchema) -> list[CommitInfo]:
        pass

    @abstractmethod
    async def get_commit(self, repo_path: str, commit_sha: str) -> CommitInfo:
        pass

    @abstractmethod
    async def get_file(self, schema: GetFileSchema) -> FileContent:
        pass

    @abstractmethod
    async def update_file(self, schema: UpdateFileSchema) -> CommitInfo:
        pass

    @abstractmethod
    async def delete_file(self, schema: DeleteFileSchema) -> CommitInfo:
        pass

    @abstractmethod
    async def get_refs(self, schema: GetRefsSchema) -> dict[str, str]:
        pass

    @abstractmethod
    async def get_pack_data(self, repo_path: str) -> bytes:
        pass
