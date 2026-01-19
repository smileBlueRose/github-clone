from abc import abstractmethod
from uuid import UUID

from pydantic import EmailStr

from domain.entities.user import User
from domain.filters.user import UserFilter
from domain.ports.repository import AbstractReadRepository, AbstractWriteRepository
from domain.schemas.user import UserCreateSchema, UserUpdateSchema


class AbstractUserReadRepository(AbstractReadRepository[User, UUID, UserFilter]):
    @abstractmethod
    async def get_by_identity(self, identity: UUID) -> User:
        """:raises UserNotFoundException:"""
        pass

    @abstractmethod
    async def get_by_email(self, email: EmailStr) -> User:
        """:raises UserNotFoundException:"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User:
        """:raises UserNotFoundException:"""
        pass

    @abstractmethod
    async def get_all(self, filter_: UserFilter) -> list[User]:
        pass


class AbstractUserWriteRepository(AbstractWriteRepository[User, UserCreateSchema, UserUpdateSchema, UUID]):
    @abstractmethod
    async def create(self, schema: UserCreateSchema) -> User:
        pass

    @abstractmethod
    async def update(self, identity: UUID, schema: UserUpdateSchema) -> User:
        pass

    @abstractmethod
    async def delete_by_identity(self, identity: UUID) -> bool:
        """Returns True if a record was deleted, False if record was not found."""
        pass
