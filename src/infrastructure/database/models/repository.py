from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities.git import Repository
from infrastructure.database.mixins.timestamp import CreatedAtMixin, UpdatedAtMixin
from infrastructure.database.mixins.uuid import UUIDMixin
from infrastructure.database.models.base import Base
from infrastructure.database.models.user import UserModel


class RepositoryModel(Base[Repository], UUIDMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "repositories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey(UserModel.id), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_entity(self) -> Repository:
        return Repository(
            id=self.id,
            name=self.name,
            owner_id=self.owner_id,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
