from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from config import settings


class CreatedAtMixin:
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(tz=settings.time.db_tz),
            nullable=False,
        )


class UpdatedAtMixin:
    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=True,
            onupdate=lambda: datetime.now(tz=settings.time.db_tz),
        )
