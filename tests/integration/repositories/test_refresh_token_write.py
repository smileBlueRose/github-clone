import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils import create_user_model

from domain.exceptions.refresh_token import RefreshTokenNotFoundException
from domain.schemas.refresh_token import RefreshTokenCreateSchema, RefreshTokenUpdateSchema
from infrastructure.database.models.refresh_token import RefreshTokenModel
from infrastructure.repositories.refresh_token import RefreshTokenWriteRepository


class TestRefreshTokenWriteRepository:
    @dataclass
    class TestData:
        __test__ = False
        user_id: uuid.UUID
        token_id: uuid.UUID = field(default_factory=uuid.uuid4)
        token_hash: str = "write_repo_hash"
        expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=1))

        def to_create_schema(self) -> RefreshTokenCreateSchema:
            return RefreshTokenCreateSchema(
                id=self.token_id,
                user_id=self.user_id,
                token_hash=self.token_hash,
                expires_at=self.expires_at,
            )

    async def _get_test_data(self, session: AsyncSession) -> TestData:
        user = await create_user_model(session)
        return self.TestData(user_id=user.id)

    def _get_repo(self, session: AsyncSession) -> RefreshTokenWriteRepository:
        return RefreshTokenWriteRepository(session=session)

    async def test_create_success(self, session: AsyncSession) -> None:
        data = await self._get_test_data(session)
        repo = self._get_repo(session)

        token = await repo.create(data.to_create_schema())

        assert token.id == data.token_id
        assert token.user_id == data.user_id
        assert token.token_hash == data.token_hash
        assert token.expires_at == data.expires_at

        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == data.token_id)
        db_token = (await session.execute(stmt)).scalar_one()
        assert db_token.id == data.token_id

    async def test_update_success(self, session: AsyncSession) -> None:
        data = await self._get_test_data(session)
        repo = self._get_repo(session)
        await repo.create(data.to_create_schema())

        updated = await repo.update(data.token_id, RefreshTokenUpdateSchema(is_revoked=True))

        assert updated.is_revoked is True
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == data.token_id)
        db_token = (await session.execute(stmt)).scalar_one()
        assert db_token.is_revoked is True

    async def test_update_not_found(self, session: AsyncSession) -> None:
        repo = self._get_repo(session)
        with pytest.raises(RefreshTokenNotFoundException):
            await repo.update(uuid.uuid4(), RefreshTokenUpdateSchema(is_revoked=True))

    async def test_delete_by_identity(self, session: AsyncSession) -> None:
        data = await self._get_test_data(session)
        repo = self._get_repo(session)
        await repo.create(data.to_create_schema())

        assert await repo.delete_by_identity(data.token_id) is True
        assert await repo.delete_by_identity(data.token_id) is False

    async def test_revoke_by_identity(self, session: AsyncSession) -> None:
        data = await self._get_test_data(session)
        repo = self._get_repo(session)
        await repo.create(data.to_create_schema())

        assert await repo.revoke_by_identity(data.token_id) is True

        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == data.token_id)
        db_token = (await session.execute(stmt)).scalar_one()
        assert db_token.is_revoked is True

    async def test_revoke_all_for_user(self, session: AsyncSession) -> None:
        data = await self._get_test_data(session)
        repo = self._get_repo(session)

        for i in range(3):
            schema = data.to_create_schema()
            schema.id = uuid.uuid4()
            schema.token_hash = f"h_{i}"
            await repo.create(schema)

        await repo.revoke_all_for_user(data.user_id)

        stmt = select(RefreshTokenModel).where(RefreshTokenModel.user_id == data.user_id)
        tokens = (await session.execute(stmt)).scalars().all()
        assert all(t.is_revoked for t in tokens)
