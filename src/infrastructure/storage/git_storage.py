import asyncio
import base64
import shutil
import tempfile
from pathlib import Path
from typing import NamedTuple

import git
from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from git.objects import Commit

from domain.exceptions.git import (
    BranchAlreadyExistsException,
    BranchNotFoundException,
    CommitNotFoundException,
    CurrentHeadDeletionException,
    FileNotFoundException,
    IsDirectoryException,
    UnmergedBranchDeletionException,
)
from domain.ports.repository_storage import AbstractRepositoryStorage
from domain.schemas.repository_storage import (
    CreateBranchSchema,
    CreateInitialCommitSchema,
    DeleteBranchSchema,
    DeleteFileSchema,
    FileContent,
    GetCommitsSchema,
    GetFileSchema,
    GetRefsSchema,
    InitRepositorySchema,
    UpdateFileSchema,
)
from domain.value_objects.git import Author, BranchInfo, CommitInfo, FsRepo


class GitPythonStorage(AbstractRepositoryStorage):
    FILE_MODE_REGULAR = 0o100644
    INDEX_STAGE_NORMAL = 0

    class IndexEntryData(NamedTuple):
        mode: int
        sha: bytes
        stage: int
        path: str

    def __init__(self, repo_path: Path) -> None:
        self.base_path = repo_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def init_repository(self, schema: InitRepositorySchema) -> FsRepo:
        def _init() -> FsRepo:
            full_path = self.base_path / schema.repo_path
            Repo.init(full_path, bare=True)
            return FsRepo(full_path=full_path)

        return await asyncio.to_thread(_init)

    async def delete_repository(self, repo_path: str) -> None:
        def _delete() -> None:
            full_path = self.base_path / repo_path
            if full_path.exists():
                shutil.rmtree(full_path)

        await asyncio.to_thread(_delete)

    async def create_initial_commit(self, schema: CreateInitialCommitSchema) -> None:
        """:raises BranchAlreadyExistsException:"""
        repo = Repo(self.base_path / schema.repo_path)

        if schema.branch_name in repo.heads:
            raise BranchAlreadyExistsException(branch=schema.branch_name)

        empty_tree_hash = repo.git.hash_object("-t", "tree", "--stdin", istream=b"")
        empty_tree = git.Tree(repo, binsha=bytes.fromhex(empty_tree_hash))

        author = git.Actor(name=schema.author.name, email=schema.author.email)
        commit = git.Commit.create_from_tree(
            repo,
            tree=empty_tree,
            message=schema.message,
            parent_commits=[],
            author=author,
            committer=author,
        )
        repo.create_head(schema.branch_name, commit=commit.hexsha, force=False)

    async def repository_exists(self, repo_path: str) -> bool:
        def _exists() -> bool:
            try:
                Repo(self.base_path / repo_path)
                return True
            except (NoSuchPathError, InvalidGitRepositoryError):
                return False

        return await asyncio.to_thread(_exists)

    async def create_branch(self, schema: CreateBranchSchema) -> None:
        """
        :raises BranchNotFoundException:
        :raises BranchAlreadyExistsException:
        """

        def _create() -> None:
            repo = git.Repo(self.base_path / schema.repo_path)

            if schema.from_branch not in repo.heads:
                raise BranchNotFoundException(branch=schema.from_branch)

            if schema.branch_name in repo.heads:
                raise BranchAlreadyExistsException(branch=schema.branch_name)

            source_commit = repo.heads[schema.from_branch].commit
            repo.create_head(schema.branch_name, commit=source_commit.hexsha, force=False)

        await asyncio.to_thread(_create)

    async def delete_branch(self, schema: DeleteBranchSchema) -> None:
        """
        :raises BranchNotFoundException:
        :raises CurrentHeadDeletionException:
        :raises UnmergedBranchDeletionException:
        """

        def _delete() -> None:
            repo = git.Repo(self.base_path / schema.repo_path)

            if schema.branch_name not in repo.heads:
                raise BranchNotFoundException(branch=schema.branch_name)
            if schema.branch_name == repo.head.reference.name:
                raise CurrentHeadDeletionException

            if not schema.force:
                branch_commit = repo.heads[schema.branch_name].commit
                is_merged = repo.is_ancestor(branch_commit, repo.head.commit)

                if not is_merged:
                    raise UnmergedBranchDeletionException(branch=schema.branch_name)

            repo.delete_head(schema.branch_name, force=schema.force)

        await asyncio.to_thread(_delete)

    async def get_branches(self, repo_path: str) -> list[BranchInfo]:
        def _get() -> list[BranchInfo]:
            repo = Repo(self.base_path / repo_path)
            branches = [BranchInfo(name=head.name, commit_sha=head.commit.hexsha) for head in repo.heads]
            return branches

        return await asyncio.to_thread(_get)

    async def get_commit(self, repo_path: str, commit_sha: str) -> CommitInfo:
        """
        :raises CommitNotFoundException:
        """

        def _get() -> CommitInfo:
            repo = Repo(self.base_path / repo_path)
            try:
                commit = repo.commit(commit_sha)
            except (ValueError, git.BadName) as e:
                raise CommitNotFoundException(commit_sha=commit_sha) from e

            return self._commit_to_info(commit)

        return await asyncio.to_thread(_get)

    async def get_commits(self, schema: GetCommitsSchema) -> list[CommitInfo]:
        """:raises BranchNotFoundException:"""

        def _get() -> list[CommitInfo]:
            repo = Repo(self.base_path / schema.repo_path)

            if schema.branch_name not in repo.heads:
                raise BranchNotFoundException(branch=schema.branch_name)

            branch = repo.heads[schema.branch_name]
            return [self._commit_to_info(commit) for commit in repo.iter_commits(branch, max_count=schema.limit)]

        return await asyncio.to_thread(_get)

    def _commit_to_info(self, commit: Commit) -> CommitInfo:
        message: str = (
            commit.message.decode("utf-8") if isinstance(commit.message, bytes) else commit.message
        )  # pyright: ignore[reportAssignmentType]

        return CommitInfo(
            commit_hash=commit.hexsha,
            author=Author(name=commit.author.name, email=commit.author.email),
            message=message,
            committed_datetime=commit.committed_datetime,
        )

    async def get_file(self, schema: GetFileSchema) -> FileContent:
        """
        :raises FileNotFoundException:
        :raises IsDirectoryException:
        :raises BranchNotFoundException:
        """

        def _get() -> FileContent:
            repo = Repo(self.base_path / schema.repo_path)
            if schema.branch_name not in repo.heads:
                raise BranchNotFoundException(branch=schema.branch_name)

            commit = repo.heads[schema.branch_name].commit

            try:
                blob = commit.tree / schema.file_path
            except KeyError as e:
                raise FileNotFoundException(file_path=schema.file_path) from e

            if not isinstance(blob, git.Blob):
                raise IsDirectoryException(file_path=schema.file_path)

            content: bytes = blob.data_stream.read()
            try:
                text_content = content.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                text_content = base64.b64encode(content).decode("ascii")
                encoding = "base64"

            return FileContent(
                content=text_content,
                encoding=encoding,
                sha=blob.hexsha,
            )

        return await asyncio.to_thread(_get)

    async def update_file(self, schema: UpdateFileSchema) -> CommitInfo:
        def _update_file() -> CommitInfo:
            repo = git.Repo(self.base_path / schema.repo_path)
            author = git.Actor(schema.author.name, schema.author.email)

            if schema.branch_name in repo.heads:
                parent = repo.heads[schema.branch_name].commit
                parents = [parent]
                index = git.IndexFile.from_tree(repo, parent.tree)
            else:
                parents = []
                index = git.IndexFile(repo)

            if schema.encoding == "utf-8":
                content_bytes = schema.content.encode("utf-8")
            elif schema.encoding == "base64":
                content_bytes = base64.b64decode(schema.content)
            else:
                raise ValueError(f"Unsupported encoding: {schema.encoding}")

            with tempfile.NamedTemporaryFile(mode="wb", delete=True, delete_on_close=False) as tmp:
                tmp.write(content_bytes)
                tmp.close()
                blob_sha = bytes.fromhex(repo.git.hash_object("-w", tmp.name))

            entry_data = self.IndexEntryData(
                mode=self.FILE_MODE_REGULAR,
                sha=blob_sha,
                stage=self.INDEX_STAGE_NORMAL,
                path=schema.file_path,
            )
            index.add([git.IndexEntry(entry_data)])

            new_commit = git.Commit.create_from_tree(
                repo,
                index.write_tree(),
                schema.message,
                parents,
                author=author,
                committer=author,
            )

            if schema.branch_name in repo.heads:
                repo.heads[schema.branch_name].commit = new_commit
            else:
                repo.create_head(schema.branch_name, new_commit.hexsha)

            return self._commit_to_info(new_commit)

        return await asyncio.to_thread(_update_file)

    async def delete_file(self, schema: DeleteFileSchema) -> CommitInfo:
        """
        :raises BranchNotFoundException:
        """

        def _delete_file() -> CommitInfo:
            repo = git.Repo(self.base_path / schema.repo_path)
            author = git.Actor(schema.author.name, schema.author.email)

            if schema.branch_name not in repo.heads:
                raise BranchNotFoundException(branch=schema.branch_name)

            parent = repo.heads[schema.branch_name].commit
            index = git.IndexFile.from_tree(repo, parent.tree)

            index.entries.pop((schema.file_path, self.INDEX_STAGE_NORMAL), None)

            commit = git.Commit.create_from_tree(
                repo,
                tree=index.write_tree(),
                message=schema.message,
                parent_commits=[parent],
                author=author,
                committer=author,
            )
            repo.heads[schema.branch_name].commit = commit

            return self._commit_to_info(commit)

        return await asyncio.to_thread(_delete_file)

    async def get_refs(self, schema: GetRefsSchema) -> dict[str, str]:
        def _get_refs() -> dict[str, str]:
            repo = Repo(self.base_path / schema.repo_path)
            refs = {}

            for head in repo.heads:
                refs[f"refs/heads/{head.name}"] = head.commit.hexsha

            for tag in repo.tags:
                refs[f"refs/tags/{tag.name}"] = tag.commit.hexsha

            if repo.head.is_valid():
                refs["HEAD"] = repo.head.commit.hexsha

            return refs

        return await asyncio.to_thread(_get_refs)

    async def get_pack_data(self, repo_path: str) -> bytes:
        def _get_pack_data() -> bytes:
            raise NotImplementedError("Full Git protocol support requires git-upload-pack implementation")

        return await asyncio.to_thread(_get_pack_data)
