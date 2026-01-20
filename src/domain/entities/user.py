from datetime import datetime
from uuid import UUID, uuid4

from pydantic import EmailStr, Field

from config import settings
from domain.ports.entity import BaseEntity


class User(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    username: str = Field(
        min_length=settings.user.username.min_length,
        max_length=settings.user.username.max_length,
    )
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=settings.time.default_tz))
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
