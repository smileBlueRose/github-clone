from datetime import datetime

from domain.ports.entity import BaseEntity


class Repository(BaseEntity):
    id: int
    name: str
    owner_id: int
    description: str | None
    created_at: datetime
    updated_at: datetime
