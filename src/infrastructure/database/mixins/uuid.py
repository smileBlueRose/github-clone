from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class UUIDMixin:
    @declared_attr
    def id(cls) -> Mapped[UUID]:
        return mapped_column(
            PostgresUUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
        )
