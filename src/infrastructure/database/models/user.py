from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from config import settings
from domain.entities.user import User
from infrastructure.database.mixins.timestamp import CreatedAtMixin, UpdatedAtMixin
from infrastructure.database.mixins.uuid import UUIDMixin

from .base import Base


class UserModel(Base[User], UUIDMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(length=settings.user.email.max_length), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String(length=settings.user.username.max_length),
        unique=True,
        nullable=False,
    )
    # TODO rename it to password_hash
    hashed_password: Mapped[str] = mapped_column(
        String(length=settings.user.hashed_password.max_length),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def to_entity(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            hashed_password=self.hashed_password,
            created_at=self.created_at,
        )
