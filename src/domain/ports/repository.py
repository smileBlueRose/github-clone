from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from domain.ports.entity import BaseEntity
from domain.ports.filter import BaseFilter
from domain.ports.schemas import BaseCreateSchema, BaseUpdateSchema

E = TypeVar("E", bound=BaseEntity)
F = TypeVar("F", bound=BaseFilter)
U = TypeVar("U", bound=BaseUpdateSchema)
C = TypeVar("C", bound=BaseCreateSchema)
Identity = TypeVar("Identity")


class AbstractReadRepository(ABC, Generic[E, Identity, F]):
    @abstractmethod
    async def get_by_identity(self, identity: Identity) -> E:
        """:raises domain.exception.NotFoundException:"""
        pass

    @abstractmethod
    async def get_all(self, filter_: F) -> list[E]:
        pass


class AbstractWriteRepository(ABC, Generic[E, C, U, Identity]):
    @abstractmethod
    async def create(self, schema: C) -> E:
        pass

    @abstractmethod
    async def update(self, identity: Identity, schema: U) -> E:
        pass

    @abstractmethod
    async def delete_by_identity(self, identity: Identity) -> bool:
        """Returns True if a record was deleted, False if record was not found."""
        pass
