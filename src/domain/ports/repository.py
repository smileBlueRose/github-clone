from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from domain.ports.entity import BaseEntity
from domain.ports.filter import BaseFilter

E = TypeVar("E", bound=BaseEntity)
F = TypeVar("F", bound=BaseFilter)
K = TypeVar("K")


class AbstractReadRepository(ABC, Generic[K, F, E]):
    @abstractmethod
    async def get_by_identity(self, identity: K) -> E:
        """:raises domain.exception.NotFoundException:"""
        pass

    @abstractmethod
    async def get_all(self, fiter_: F) -> list[E]:
        pass
