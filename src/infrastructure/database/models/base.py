from abc import abstractmethod
from typing import Generic, TypeVar

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from config import settings
from domain.ports.entity import BaseEntity

E = TypeVar("E", bound=BaseEntity)


class Base(DeclarativeBase, Generic[E]):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.naming_convention)

    @abstractmethod
    def to_entity(self) -> E:
        pass
