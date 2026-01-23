import base64
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import pytest

from domain.exceptions.git import (
    BranchAlreadyExistsException,
    BranchNotFoundException,
    CommitNotFoundException,
    CurrentHeadDeletionException,
    FileNotFoundException,
    IsDirectoryException,
    UnmergedBranchDeletionException,
)
from domain.schemas.repository_storage import (
    CreateBranchSchema,
    CreateInitialCommitSchema,
    DeleteBranchSchema,
    DeleteFileSchema,
    GetCommitsSchema,
    GetFileSchema,
    GetRefsSchema,
    InitRepositorySchema,
    UpdateFileSchema,
)
from domain.value_objects.git import Author
from infrastructure.storage.git_storage import GitPythonStorage


@pytest.fixture
def temp_storage_path() -> Generator[Path, None, None]:
    with TemporaryDirectory(prefix="test_") as tmp:
        yield Path(tmp)


@pytest.fixture
def git_storage(temp_storage_path: Path) -> GitPythonStorage:
    return GitPythonStorage(repo_path=temp_storage_path)


@pytest.fixture
def author() -> Author:
    return Author(name="test-user", email="test@example.com")


class TestGitPythonStorage:
    init_schema = InitRepositorySchema(repo_path="test-repo")
    default_branch = "master"

    @staticmethod
    def git_run(repo_dir: Path, *args: str) -> str:
        """Helper for executing git commands."""
        result = subprocess.run(
            ["git", *args],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    async def test_create_repository(
        self,
        git_storage: GitPythonStorage,
        temp_storage_path: Path,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        repo_dir = temp_storage_path / self.init_schema.repo_path
        assert (repo_dir / "HEAD").exists()
        assert (repo_dir / "refs").exists()

    async def test_delete_repository(
        self,
        git_storage: GitPythonStorage,
        temp_storage_path: Path,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        await git_storage.delete_repository(repo_path=self.init_schema.repo_path)

        assert not (temp_storage_path / self.init_schema.repo_path).exists()
