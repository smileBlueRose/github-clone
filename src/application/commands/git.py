from uuid import UUID

from pydantic import Field, field_validator

from application.ports.command import BaseCommand
from config import settings


class CreateRepositoryCommand(BaseCommand):
    repository_name: str
    user_id: UUID
    description: str = Field(max_length=settings.git.description_max_length)

    @field_validator("repository_name")
    @classmethod
    def validate_repository_name(cls, v: str) -> str:
        """:raises ValueError:"""

        if not settings.git.repository_name_pattern.match(v):
            raise ValueError(
                "Repository name must contain only letters, numbers, hyphens, underscores, "
                "and dots (1-100 characters). Cannot start or end with a dot."
            )

        return v
