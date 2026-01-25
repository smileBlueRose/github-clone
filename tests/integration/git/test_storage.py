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
    return GitPythonStorage(repositories_dir=temp_storage_path)


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

    async def test_repository_exists_success(
        self,
        git_storage: GitPythonStorage,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        assert await git_storage.repository_exists(self.init_schema.repo_path)

    async def test_repository_exists_with_invalid_repo(
        self,
        git_storage: GitPythonStorage,
        temp_storage_path: Path,
    ) -> None:
        empty_dir_name = "empty-dir"
        (temp_storage_path / empty_dir_name).mkdir()

        assert not await git_storage.repository_exists(empty_dir_name)

    async def test_repository_exists_with_non_existing_dir(
        self,
        git_storage: GitPythonStorage,
    ) -> None:
        assert not await git_storage.repository_exists("non-existing-repo")

    async def test_update_file_lifecycle_with_text_file(
        self,
        git_storage: GitPythonStorage,
        temp_storage_path: Path,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        repo_dir = temp_storage_path / self.init_schema.repo_path
        branch = "master"
        file_path = "docs/readme.md"

        first_schema = UpdateFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path=file_path,
            content="first content",
            branch_name=branch,
            message="initial commit",
            author=author,
        )
        first_commit = await git_storage.update_file(first_schema)
        assert self.git_run(repo_dir, "cat-file", "-p", f"{branch}:{file_path}") == first_schema.content
        assert self.git_run(repo_dir, "rev-parse", branch) == first_commit.commit_hash
        assert first_commit.author == author
        assert first_commit.message == first_schema.message

        second_scheme = UpdateFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path=file_path,
            content="updated content",
            branch_name=branch,
            message="second commit",
            author=author,
        )
        second_commit = await git_storage.update_file(second_scheme)

        assert self.git_run(repo_dir, "cat-file", "-p", f"{branch}:{file_path}") == second_scheme.content

        commits = self.git_run(repo_dir, "log", branch, "--format=%H").split("\n")
        assert len(commits) == 2
        assert commits[0] == second_commit.commit_hash

    async def test_upload_image(
        self,
        git_storage: GitPythonStorage,
        author: Author,
        test_images_dir: Path,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        image_path = "image.jpg"
        image_full_path = test_images_dir / image_path
        with open(image_full_path, "rb") as f:
            image_bytes = f.read()

        image_base64 = base64.b64encode(image_bytes).decode("ascii")

        update_schema = UpdateFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path=image_path,
            content=image_base64,
            encoding="base64",
            branch_name=self.default_branch,
            message="add image",
            author=author,
        )
        await git_storage.update_file(update_schema)

        get_schema = GetFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path=image_path,
            branch_name=self.default_branch,
        )
        file_content = await git_storage.get_file(get_schema)

        assert file_content.encoding == "base64"
        assert file_content.content == image_base64

    async def test_upload_unknown_encoding_file(
        self,
        git_storage: GitPythonStorage,
        author: Author,
        test_images_dir: Path,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        schema = UpdateFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="file.txt",
            content="first content",
            branch_name=self.default_branch,
            encoding="unknown",
            message="initial commit",
            author=author,
        )
        with pytest.raises(ValueError):
            await git_storage.update_file(schema)

    async def test_delete_file_success(
        self,
        git_storage: GitPythonStorage,
        temp_storage_path: Path,
        author: Author,
    ) -> None:
        branch = "master"

        await git_storage.init_repository(self.init_schema)
        schemas: list[UpdateFileSchema] = []
        for i in range(2):
            schema = UpdateFileSchema(
                repo_path=self.init_schema.repo_path,
                file_path=f"file_{i}.txt",
                content=f"content_{i}",
                branch_name=branch,
                message=f"add file_{i}",
                author=author,
            )
            await git_storage.update_file(schema)
            schemas.append(schema)
        delete_schema = DeleteFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path=schemas[0].file_path,
            branch_name=branch,
            message="delete file 0",
            author=author,
        )
        delete_commit = await git_storage.delete_file(delete_schema)
        assert delete_commit.message == delete_schema.message

        files = self.git_run(
            temp_storage_path / self.init_schema.repo_path,
            "ls-tree",
            "-r",
            branch,
            "--name-only",
        )

        assert schemas[0].file_path not in files
        assert schemas[1].file_path in files

    async def test_delete_non_existing_file_without_exception(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        await git_storage.update_file(
            schema=UpdateFileSchema(
                repo_path=self.init_schema.repo_path,
                file_path="file.txt",
                content="content",
                message="add file",
                branch_name=self.default_branch,
                author=author,
            )
        )

        delete_schema = DeleteFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="non-existing-file.txt",
            branch_name=self.default_branch,
            message="delete file",
            author=author,
        )
        await git_storage.delete_file(delete_schema)

    async def test_dele_file_from_non_existing_branch_raises_exception(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        delete_schema = DeleteFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="non-existing-file.txt",
            branch_name=self.default_branch,
            message="delete file",
            author=author,
        )
        with pytest.raises(BranchNotFoundException):
            await git_storage.delete_file(delete_schema)

    async def test_create_initial_commit_success(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        repo = await git_storage.init_repository(self.init_schema)
        schema = CreateInitialCommitSchema(repo_path=self.init_schema.repo_path, author=author)
        await git_storage.create_initial_commit(schema)
        assert schema.branch_name in self.git_run(repo.full_path, "branch")

    async def test_create_initial_commit_with_existing_branch_name(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        schema = CreateInitialCommitSchema(repo_path=self.init_schema.repo_path, author=author)
        await git_storage.create_initial_commit(schema)
        with pytest.raises(BranchAlreadyExistsException):
            await git_storage.create_initial_commit(schema)

    async def test_create_branch_success(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        repo = await git_storage.init_repository(self.init_schema)
        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                author=author,
                branch_name=self.default_branch,
            )
        )

        branch_schema = CreateBranchSchema(
            repo_path=self.init_schema.repo_path,
            branch_name="develop",
            from_branch=self.default_branch,
        )
        await git_storage.create_branch(branch_schema)

        assert branch_schema.branch_name in self.git_run(repo.full_path, "branch")

        main_commit = self.git_run(repo.full_path, "rev-parse", self.default_branch)
        develop_commit = self.git_run(repo.full_path, "rev-parse", branch_schema.branch_name)

        assert main_commit == develop_commit

    async def test_create_branch_with_existing_branch_name(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                author=author,
                branch_name=self.default_branch,
            )
        )

        branch_schema = CreateBranchSchema(
            repo_path=self.init_schema.repo_path,
            branch_name="develop",
            from_branch=self.default_branch,
        )
        await git_storage.create_branch(branch_schema)

        with pytest.raises(BranchAlreadyExistsException):
            await git_storage.create_branch(branch_schema)

    async def test_create_branch_from_non_existing_branch(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                author=author,
                branch_name=self.default_branch,
            )
        )
        branch_schema = CreateBranchSchema(
            repo_path=self.init_schema.repo_path,
            branch_name="develop",
            from_branch="non-existing-branch",
        )
        with pytest.raises(BranchNotFoundException):
            await git_storage.create_branch(branch_schema)

    async def test_delete_branch_success(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        repo = await git_storage.init_repository(self.init_schema)
        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                author=author,
                branch_name=self.default_branch,
            )
        )
        schema = CreateBranchSchema(
            repo_path=self.init_schema.repo_path,
            branch_name="feature",
            from_branch=self.default_branch,
        )
        await git_storage.create_branch(schema)

        delete_schema = DeleteBranchSchema(repo_path=self.init_schema.repo_path, branch_name=schema.branch_name)
        await git_storage.delete_branch(delete_schema)

        assert delete_schema.branch_name not in self.git_run(repo.full_path, "branch")

    async def test_delete_not_existing_branch_raises_exception(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        delete_schema = DeleteBranchSchema(repo_path=self.init_schema.repo_path, branch_name="not-exists")
        with pytest.raises(BranchNotFoundException):
            await git_storage.delete_branch(delete_schema)

    async def test_delete_head_branch_raises_exception(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                branch_name=self.default_branch,
                author=author,
            )
        )

        delete_schema = DeleteBranchSchema(repo_path=self.init_schema.repo_path, branch_name=self.default_branch)
        with pytest.raises(CurrentHeadDeletionException):
            await git_storage.delete_branch(delete_schema)

    async def test_delete_not_merged_commits_branch(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        print()
        await git_storage.init_repository(self.init_schema)
        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                branch_name=self.default_branch,
                author=author,
            )
        )
        second_scheme = UpdateFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="file.txt",
            content="updated content",
            branch_name="feature",
            message="feature commit",
            author=author,
        )
        await git_storage.update_file(second_scheme)

        delete_schema = DeleteBranchSchema(repo_path=self.init_schema.repo_path, branch_name=second_scheme.branch_name)
        with pytest.raises(UnmergedBranchDeletionException):
            await git_storage.delete_branch(delete_schema)

    async def test_get_branches(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                branch_name=self.default_branch,
                author=author,
            )
        )
        for i in range(10):
            schema = CreateBranchSchema(
                repo_path=self.init_schema.repo_path,
                branch_name=f"feature_{i}",
                from_branch=self.default_branch,
            )
            await git_storage.create_branch(schema)

        branches = await git_storage.get_branches(self.init_schema.repo_path)
        assert set(["master"] + [f"feature_{i}" for i in range(10)]) == set([i.name for i in branches])

    async def test_get_commit_success(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        schema = UpdateFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="test.txt",
            content="hello",
            branch_name=self.default_branch,
            message="unique message",
            author=author,
        )
        created_commit = await git_storage.update_file(schema)

        fetched_commit = await git_storage.get_commit(
            repo_path=self.init_schema.repo_path, commit_sha=created_commit.commit_hash
        )

        assert fetched_commit.commit_hash == created_commit.commit_hash
        assert fetched_commit.message == "unique message"
        assert fetched_commit.author == author

    async def test_get_commit_by_branch_name(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                branch_name=self.default_branch,
                author=author,
            )
        )
        fetched_commit = await git_storage.get_commit(
            repo_path=self.init_schema.repo_path, commit_sha=self.default_branch
        )
        assert bool(fetched_commit)

    async def test_get_commits_list_and_limit(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        commit_hashes = []
        schemas: list[UpdateFileSchema] = []
        for i in range(5):
            schema = UpdateFileSchema(
                repo_path=self.init_schema.repo_path,
                file_path="file.txt",
                content=f"content {i}",
                branch_name=self.default_branch,
                message=f"commit {i}",
                author=author,
            )
            schemas.append(schema)
            commit_hashes.append((await git_storage.update_file(schema)).commit_hash)

        all_commits = await git_storage.get_commits(
            GetCommitsSchema(
                repo_path=self.init_schema.repo_path,
                branch_name=self.default_branch,
                limit=10,
            )
        )
        assert len(all_commits) == len(schemas)
        assert all_commits[0].message == schemas[-1].message

        limited_commits = await git_storage.get_commits(
            GetCommitsSchema(
                repo_path=self.init_schema.repo_path,
                branch_name=self.default_branch,
                limit=2,
            )
        )
        assert len(limited_commits) == 2
        assert limited_commits[0].message == schemas[-1].message
        assert limited_commits[1].message == schemas[-2].message

    async def test_get_commit_invalid_sha_raises_exception(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        with pytest.raises(CommitNotFoundException):
            await git_storage.get_commit(
                self.init_schema.repo_path, "abc123de456f7890abc123de456f7890abc123de"
            )  # non existing commit

        with pytest.raises(CommitNotFoundException):
            await git_storage.get_commit(self.init_schema.repo_path, "invalid")  # invalid sha and non-existing branch

    async def test_get_commits_non_existing_branch_raises_exception(
        self,
        git_storage: GitPythonStorage,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        with pytest.raises(BranchNotFoundException):
            await git_storage.get_commits(
                GetCommitsSchema(repo_path=self.init_schema.repo_path, branch_name="ghost-branch")
            )

    async def test_get_refs_success(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        repo_dir = git_storage.base_path / self.init_schema.repo_path

        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                author=author,
                branch_name=self.default_branch,
            )
        )

        self.git_run(repo_dir, "branch", "develop")
        self.git_run(repo_dir, "tag", "v1.0")

        master_sha = self.git_run(repo_dir, "rev-parse", "master")

        refs = await git_storage.get_refs(GetRefsSchema(repo_path=self.init_schema.repo_path))

        assert (
            refs["refs/heads/master"]
            == refs["refs/heads/develop"]
            == refs["refs/tags/v1.0"]
            == refs["HEAD"]
            == master_sha
        )

        assert len(refs) == 4

    async def test_get_refs_empty_repo(
        self,
        git_storage: GitPythonStorage,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        refs = await git_storage.get_refs(GetRefsSchema(repo_path=self.init_schema.repo_path))

        assert refs == {}

    async def test_get_file_success_with_text_content(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        update_schema = UpdateFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="file.txt",
            content="Hello World",
            branch_name=self.default_branch,
            message="add file",
            author=author,
        )
        await git_storage.update_file(update_schema)

        get_schema = GetFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path=update_schema.file_path,
            branch_name=self.default_branch,
        )
        file_content = await git_storage.get_file(get_schema)

        assert file_content.content == update_schema.content
        assert file_content.encoding == "utf-8"
        assert file_content.sha is not None

    async def test_get_file_with_binary_content(
        self,
        git_storage: GitPythonStorage,
        author: Author,
        test_images_dir: Path,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        image_path = "image.jpg"
        image_full_path = test_images_dir / image_path
        with open(image_full_path, "rb") as f:
            image_bytes = f.read()

        image_base64 = base64.b64encode(image_bytes).decode("ascii")

        update_schema = UpdateFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path=image_path,
            content=image_base64,
            encoding="base64",
            branch_name=self.default_branch,
            message="add image",
            author=author,
        )
        await git_storage.update_file(update_schema)

        get_schema = GetFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path=image_path,
            branch_name=self.default_branch,
        )
        file_content = await git_storage.get_file(get_schema)

        assert file_content.encoding == "base64"
        assert file_content.content == image_base64

    async def test_get_file_from_non_existing_branch_raises_exception(
        self,
        git_storage: GitPythonStorage,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        schema = GetFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="file.txt",
            branch_name="non-existing",
        )

        with pytest.raises(BranchNotFoundException):
            await git_storage.get_file(schema)

    async def test_get_file_non_existing_file_raises_exception(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)
        await git_storage.create_initial_commit(
            CreateInitialCommitSchema(
                repo_path=self.init_schema.repo_path,
                author=author,
                branch_name=self.default_branch,
            )
        )

        schema = GetFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="non-existing.txt",
            branch_name=self.default_branch,
        )

        with pytest.raises(FileNotFoundException):
            await git_storage.get_file(schema)

    async def test_get_file_directory_raises_exception(
        self,
        git_storage: GitPythonStorage,
        author: Author,
    ) -> None:
        await git_storage.init_repository(self.init_schema)

        update_schema = UpdateFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="docs/readme.md",
            content="content",
            encoding="utf-8",
            branch_name=self.default_branch,
            message="add file",
            author=author,
        )
        await git_storage.update_file(update_schema)

        schema = GetFileSchema(
            repo_path=self.init_schema.repo_path,
            file_path="docs",
            branch_name=self.default_branch,
        )

        with pytest.raises(IsDirectoryException):
            await git_storage.get_file(schema)
