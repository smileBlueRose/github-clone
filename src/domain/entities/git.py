from datetime import datetime
from typing import Any
from uuid import UUID

from domain.ports.entity import BaseEntity


class Repository(BaseEntity):
    id: UUID
    name: str
    owner_id: UUID
    description: str | None
    created_at: datetime
    updated_at: datetime | None

    def to_policy_context(self) -> dict[str, Any]:
        return {"owner_id": self.owner_id}
