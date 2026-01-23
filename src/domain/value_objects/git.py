from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, EmailStr


class Author(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class BranchInfo(BaseModel):
    name: str
    commit_sha: str


class CommitInfo(BaseModel):
    commit_hash: str
    author: Author
    message: str
    committed_datetime: datetime


class Repository(BaseModel):
    full_path: Path
