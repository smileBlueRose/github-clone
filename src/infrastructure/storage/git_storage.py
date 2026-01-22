import asyncio
from pathlib import Path

from git import Actor, Repo

from domain.ports.repository_storage import AbstractRepositoryStorage
from domain.schemas.repository_storage import CommitResult, CommitSchema, InitRepositorySchema


class GitPythonStorage(AbstractRepositoryStorage):
    def __init__(self, repo_path: Path) -> None:
        self.base_path = repo_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def init_repository(self, schema: InitRepositorySchema) -> None:
        await asyncio.to_thread(
            Repo.init,
            self.base_path / schema.repo_path,
            bare=schema.bare,
        )

    async def commit(self, schema: CommitSchema) -> CommitResult:
        def _commit() -> CommitResult:
            repo = Repo(self.base_path / schema.repo_path)
            repo.index.add(schema.files)
            author = Actor(name=schema.author_email, email=schema.author_email)
            commit = repo.index.commit(message=schema.message, author=author)

            return CommitResult(
                commit_hash=commit.hexsha,
                author=str(author),
                message=str(commit.message),
                timestamp=str(commit.committed_date),
            )

        return await asyncio.to_thread(_commit)
