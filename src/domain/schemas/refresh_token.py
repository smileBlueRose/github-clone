from datetime import datetime
from uuid import UUID

from domain.ports.schemas import BaseCreateSchema, BaseUpdateSchema


class RefreshTokenCreateSchema(BaseCreateSchema):
    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    user_agent: str | None = None
    ip_address: str | None = None


class RefreshTokenUpdateSchema(BaseUpdateSchema):
    is_revoked: bool | None = None
