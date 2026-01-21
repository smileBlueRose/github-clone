from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from config import settings
from domain.entities.refresh import RefreshToken
from domain.value_objects.session import IpAddress, UserAgent
from infrastructure.database.mixins.timestamp import CreatedAtMixin
from infrastructure.database.mixins.uuid import UUIDMixin

from .base import Base
from .user import UserModel


class RefreshTokenModel(Base[RefreshToken], UUIDMixin, CreatedAtMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[UUID] = mapped_column(ForeignKey(UserModel.id, ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(
        String(length=settings.auth.token_hash.length), unique=True, index=True, nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(default=False)

    user_agent: Mapped[str] = mapped_column(String(length=settings.session.ua_max_length), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(length=settings.session.ip_max_length), nullable=False)

    def to_entity(self) -> RefreshToken:
        return RefreshToken(
            id=self.id,
            user_id=self.user_id,
            token_hash=self.token_hash,
            created_at=self.created_at,
            expires_at=self.expires_at,
            is_revoked=self.is_revoked,
            user_agent=UserAgent(value=self.user_agent) if self.user_agent else None,
            ip_address=IpAddress(value=self.ip_address) if self.ip_address else None,
        )
