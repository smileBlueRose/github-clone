from pydantic import BaseModel


class InitRepositorySchema(BaseModel):
    repo_path: str
    bare: bool = True


class CommitSchema(BaseModel):
    repo_path: str
    files: list[str]
    message: str
    author_name: str
    author_email: str


class CreateBranchSchema(BaseModel):
    repo_path: str
    branch_name: str
    from_branch: str | None = None


class CommitResult(BaseModel):
    commit_hash: str
    author: str
    message: str
    timestamp: str
