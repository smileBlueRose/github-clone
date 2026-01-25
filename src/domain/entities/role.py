from uuid import UUID

from domain.ports.entity import BaseEntity


class Role(BaseEntity):
    id: UUID
    name: str
