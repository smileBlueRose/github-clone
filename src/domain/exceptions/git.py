from uuid import UUID

from domain.exceptions import CustomException
from domain.exceptions.common import AlreadyExistsException, NotFoundException


class GitException(CustomException):
    pass


class BranchException(GitException):
    pass


class BranchNotFoundException(BranchException, NotFoundException):
    def __init__(self, *, branch: str) -> None:
        super().__init__(f"Branch '{branch}' not found in repository")


class BranchAlreadyExistsException(BranchException, AlreadyExistsException):
    def __init__(self, *, branch: str) -> None:
        super().__init__(f"Branch '{branch}' already exists in repository")


class CurrentHeadDeletionException(BranchException):
    pass


class UnmergedBranchDeletionException(BranchException):
    def __init__(self, *, branch: str) -> None:
        super().__init__(f"Cannot delete branch '{branch}' because it is not fully merged")


class CommitException(GitException):
    pass


class CommitNotFoundException(CommitException, NotFoundException):
    def __init__(self, *, commit_sha: str, repo_path: str | None = None) -> None:
        self.repo_path = repo_path
        super().__init__(f"Commit '{commit_sha}' not found in repository")


class FileNotFoundException(GitException):
    def __init__(self, *, file_path: str) -> None:
        self.msg = f"File not found at path: {file_path}"


class IsDirectoryException(GitException):
    def __init__(self, *, file_path: str) -> None:
        self.msg = f"Expected a file, but found a directory at path: {file_path}"


# ====================
# ==== Repository ====
# ====================
class RepositoryException(GitException):
    pass


class RepositoryNotFoundException(NotFoundException, RepositoryException):
    def __init__(self, *, repo_id: UUID) -> None:
        super().__init__(f"Repository with id {repo_id} not found")
