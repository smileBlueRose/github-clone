from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from config import settings
from domain.ports.entity import BaseEntity
from domain.value_objects.session import IpAddress, UserAgent


class RefreshToken(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    token_hash: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=settings.time.default_tz))
    is_revoked: bool = False
    user_agent: UserAgent | None = None
    ip_address: IpAddress | None = None
