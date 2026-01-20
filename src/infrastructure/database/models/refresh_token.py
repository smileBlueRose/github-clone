from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from config import settings
from infrastructure.database.mixins.timestamp import CreatedAtMixin
from infrastructure.database.mixins.uuid import UUIDMixin

from .base import Base
from .user import UserModel


class RefreshTokenModel(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[UUID] = mapped_column(ForeignKey(UserModel.id, ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(
        String(length=settings.auth.token_hash.length), unique=True, index=True, nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(index=True, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(default=False)

    user_agent: Mapped[str] = mapped_column(String(length=settings.session.ua_max_length), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(length=settings.session.ip_max_length), nullable=False)
