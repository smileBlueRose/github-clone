import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from utils import create_user_model

from domain.exceptions.refresh_token import RefreshTokenNotFoundException
from domain.filters.refresh_token import RefreshTokenFilter
from domain.schemas.refresh_token import RefreshTokenCreateSchema
from infrastructure.repositories.refresh_token import (
    RefreshTokenReadRepository,
    RefreshTokenWriteRepository,
)


class TestRefreshTokenReadRepository:
    @dataclass
    class TestData:
        __test__ = False
        user_id: uuid.UUID
        token_id: uuid.UUID = field(default_factory=uuid.uuid4)
        token_hash: str = "read_repo_hash"
        expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=1))

        def to_create_schema(self) -> RefreshTokenCreateSchema:
            return RefreshTokenCreateSchema(
                id=self.token_id,
                user_id=self.user_id,
                token_hash=self.token_hash,
                expires_at=self.expires_at,
            )

    async def _setup_token(self, session: AsyncSession) -> TestData:
        user = await create_user_model(session)
        data = self.TestData(user_id=user.id)

        write_repo = RefreshTokenWriteRepository(session=session)
        await write_repo.create(data.to_create_schema())
        return data

    def _get_repo(self, session: AsyncSession) -> RefreshTokenReadRepository:
        return RefreshTokenReadRepository(session=session)

    async def test_get_by_identity_success(self, session: AsyncSession) -> None:
        data = await self._setup_token(session)

        token = await self._get_repo(session).get_by_identity(data.token_id)

        assert token.id == data.token_id
        assert token.token_hash == data.token_hash

    async def test_get_by_identity_not_found(self, session: AsyncSession) -> None:
        with pytest.raises(RefreshTokenNotFoundException):
            await self._get_repo(session).get_by_identity(uuid.uuid4())

    async def test_get_by_token_hash_success(self, session: AsyncSession) -> None:
        data = await self._setup_token(session)

        token = await self._get_repo(session).get_by_token_hash(data.token_hash)

        assert token.token_hash == data.token_hash
        assert token.id == data.token_id

    async def test_get_by_token_hash_not_found(self, session: AsyncSession) -> None:
        with pytest.raises(RefreshTokenNotFoundException):
            await self._get_repo(session).get_by_token_hash("non_existent_hash")

    async def test_get_all(self, session: AsyncSession) -> None:
        user = await create_user_model(session)
        write_repo = RefreshTokenWriteRepository(session=session)

        for i in range(3):
            data = self.TestData(user_id=user.id, token_id=uuid.uuid4(), token_hash=f"hash_{i}")
            await write_repo.create(data.to_create_schema())

        tokens = await self._get_repo(session).get_all(RefreshTokenFilter())

        assert len(tokens) == 3
