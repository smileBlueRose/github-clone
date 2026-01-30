from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import EmailStr, Field

from config import settings
from domain.exceptions.user import UserInactiveException
from domain.ports.entity import BaseEntity


class User(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    username: str = Field(
        min_length=settings.user.username.min_length,
        max_length=settings.user.username.max_length,
    )
    password_hash: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=settings.time.default_tz))
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}

    # TODO: add last_login
    def to_policy_context(self) -> dict[str, Any]:
        return {"id": self.id}

    def ensure_active(self) -> None:
        """:raises UserInactiveException:"""

        if not self.is_active:
            raise UserInactiveException()
