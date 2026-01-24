from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.refresh import RefreshToken
from domain.exceptions.refresh_token import RefreshTokenNotFoundException
from domain.filters.refresh_token import RefreshTokenFilter
from domain.ports.repositories.refresh_token import (
    AbstractRefreshTokenReadRepository,
    AbstractRefreshTokenWriteRepository,
)
from domain.schemas.refresh_token import (
    RefreshTokenCreateSchema,
    RefreshTokenUpdateSchema,
)
from infrastructure.database.models.refresh_token import RefreshTokenModel


class RefreshTokenWriteRepository(AbstractRefreshTokenWriteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, schema: RefreshTokenCreateSchema) -> RefreshToken:
        model = RefreshTokenModel(
            id=schema.id,
            user_id=schema.user_id,
            token_hash=schema.token_hash,
            expires_at=schema.expires_at,
            user_agent=schema.user_agent,
            ip_address=schema.ip_address,
        )
        self._session.add(model)
        await self._session.flush()

        return model.to_entity()

    async def update(self, identity: UUID, schema: RefreshTokenUpdateSchema) -> RefreshToken:
        model = await self._session.get(RefreshTokenModel, identity)
        if model is None:
            raise RefreshTokenNotFoundException(token_id=identity)

        if schema.is_revoked is not None:
            model.is_revoked = schema.is_revoked

        await self._session.flush()

        return model.to_entity()

    async def delete_by_identity(self, identity: UUID) -> bool:
        model = await self._session.get(RefreshTokenModel, identity)
        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()

        return True

    async def revoke_by_identity(self, identity: UUID) -> bool:
        model = await self._session.get(RefreshTokenModel, identity)
        if model is None:
            return False

        model.is_revoked = True
        await self._session.flush()
        return True

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.is_revoked == False,  # noqa: E712
            )
            .values(is_revoked=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()


class RefreshTokenReadRepository(AbstractRefreshTokenReadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_identity(self, identity: UUID) -> RefreshToken:
        model = await self._session.get(RefreshTokenModel, identity)
        if model is None:
            raise RefreshTokenNotFoundException(token_id=identity)

        return model.to_entity()

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise RefreshTokenNotFoundException(token_hash=token_hash)

        return model.to_entity()

    async def get_all(self, filter_: RefreshTokenFilter) -> list[RefreshToken]:
        stmt = select(RefreshTokenModel)
        result = await self._session.execute(stmt)

        return [m.to_entity() for m in result.scalars().all()]
