from abc import abstractmethod
from uuid import UUID

from domain.entities.refresh import RefreshToken
from domain.filters.refresh_token import RefreshTokenFilter
from domain.ports.repository import AbstractReadRepository, AbstractWriteRepository
from domain.schemas.refresh_token import RefreshTokenCreateSchema, RefreshTokenUpdateSchema


class AbstractRefreshTokenReadRepository(AbstractReadRepository[RefreshToken, UUID, RefreshTokenFilter]):
    @abstractmethod
    async def get_by_identity(self, identity: UUID) -> RefreshToken:
        """:raises RefreshTokenNotFoundException:"""
        pass

    @abstractmethod
    async def get_all(self, filter_: RefreshTokenFilter) -> list[RefreshToken]:
        pass

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> RefreshToken:
        """:raises RefreshTokenNotFoundException:"""
        pass


class AbstractRefreshTokenWriteRepository(
    AbstractWriteRepository[RefreshToken, RefreshTokenCreateSchema, RefreshTokenUpdateSchema, UUID]
):
    @abstractmethod
    async def create(self, schema: RefreshTokenCreateSchema) -> RefreshToken:
        pass

    @abstractmethod
    async def update(self, identity: UUID, schema: RefreshTokenUpdateSchema) -> RefreshToken:
        pass

    @abstractmethod
    async def delete_by_identity(self, identity: UUID) -> bool:
        pass

    @abstractmethod
    async def revoke_by_identity(self, identity: UUID) -> bool:
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> None:
        pass
