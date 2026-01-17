from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.mixins.timestamp import CreatedAtMixin

from .base import Base
from .user import UserModel


class RefreshTokenModel(Base, CreatedAtMixin):
    __tablename__ = "refresh_tokens"

    jti: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(UserModel.id, ondelete="CASCADE"), nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(index=True, nullable=False)
