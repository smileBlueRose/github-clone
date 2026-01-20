from datetime import datetime
from config import settings
from uuid import UUID, uuid4
from domain.ports.entity import BaseEntity
from pydantic import Field
from domain.value_objects.origin import IpAddress, UserAgent


class RefreshToken(BaseEntity):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=settings.time.default_tz))
    is_revoked: bool = False
    user_agent: UserAgent | None = None
    ip_address: IpAddress | None = None
