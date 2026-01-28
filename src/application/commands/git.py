from uuid import UUID

from pydantic import Field, field_validator

from application.ports.command import BaseCommand
from config import settings
from domain.value_objects.common import Pagination


def validate_repository_name(name: str) -> str:
    """:raises ValueError:"""

    if not settings.git.repository_name_pattern.match(name):
        raise ValueError(
            "Repository name must contain only letters, numbers, hyphens, underscores, "
            "and dots (1-100 characters). Cannot start or end with a dot."
        )

    return name


class CreateRepositoryCommand(BaseCommand):
    repository_name: str
    user_id: UUID
    description: str = Field(max_length=settings.git.description_max_length)

    @field_validator("repository_name")
    @classmethod
    def validate_repository_name(cls, v: str) -> str:
        """:raises ValueError:"""
        return validate_repository_name(v)


class DeleteRepositoryCommand(BaseCommand):
    username: str
    repository_name: str
    user_id: UUID

    @field_validator("repository_name")
    @classmethod
    def validate_repository_name(cls, v: str) -> str:
        """:raises ValueError:"""

        return validate_repository_name(v)


class GetRepositoryCommand(BaseCommand):
    user_id: UUID | None = None
    username: str | None = None
    repository_name: str | None = None
    pagination: Pagination = Pagination()


class GetBranchesCommand(BaseCommand):
    username: str
    repository_name: str


class CreateBranchCommand(BaseCommand):
    initiator_id: UUID
    owner_username: str
    repository_name: str
    branch_name: str
    from_branch: str


class UpdateFileCommand(BaseCommand):
    user_id: UUID
    username: str
    repo_name: str
    branch_name: str

    file_path: str
    data: bytes

    message: str


class CreateInitialCommitCommand(BaseCommand):
    initiator_id: UUID
    owner_username: str
    repository_name: str
    branch_name: str
    msg: str = "Initial commit"


class GetCommitsCommand(BaseCommand):
    owner_username: str
    repository_name: str
    branch_name: str

    pagination: Pagination = Pagination()
