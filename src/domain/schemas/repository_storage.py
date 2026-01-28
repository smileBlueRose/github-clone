from typing import Literal, NamedTuple
from uuid import UUID

from pydantic import BaseModel, Field

from domain.ports.schemas import BaseCreateSchema, BaseUpdateSchema
from domain.value_objects.git import Author


class InitRepositorySchema(BaseModel):
    repo_path: str


class CreateInitialCommitSchema(BaseModel):
    repo_path: str
    message: str = "Initial commit"
    branch_name: str = "main"  # TODO: add default_branch_name to config/config.settings
    author: Author


class CreateBranchSchema(BaseModel):
    # TODO: rename `repo_path` to `repo_name`
    repo_path: str
    branch_name: str
    from_branch: str = "main"


class DeleteBranchSchema(BaseModel):
    repo_path: str
    branch_name: str
    force: bool = False
    # TODO: add force: bool


class GetCommitsSchema(BaseModel):
    repo_path: str
    branch_name: str = "main"
    limit: int | None = 50


class GetFileSchema(BaseModel):
    repo_path: str
    file_path: str
    branch_name: str = "main"


class FileContent(BaseModel):
    content: str
    encoding: str = "utf-8"
    sha: str


class UpdateFileSchema(BaseModel):
    repo_path: str
    file_path: str
    content: str
    encoding: str = "utf-8"
    message: str
    branch_name: str
    author: Author


class DeleteFileSchema(BaseModel):
    repo_path: str
    file_path: str
    branch_name: str
    message: str
    author: Author


class GetRefsSchema(BaseModel):
    repo_path: str


class GetTreeSchema(BaseModel):
    repo_path: str
    branch_name: str
    path: str


class TreeNode(NamedTuple):
    name: str
    path: str
    type: Literal["blob", "tree"]  # blob=file, tree=directory
    sha: str
    size: int | None  # None for directory


# ===============
# ==== MODEL ====
# ===============
class RepositoryCreateSchema(BaseCreateSchema):
    name: str = Field(max_length=255)
    owner_id: UUID
    description: str | None = None


class RepositoryUpdateSchema(BaseUpdateSchema):
    name: str | None = None
    description: str | None = None
