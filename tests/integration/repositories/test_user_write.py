import uuid
from dataclasses import dataclass

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions.user import UserNotFoundException
from domain.schemas.user import UserCreateSchema, UserUpdateSchema
from infrastructure.database.models.user import UserModel
from infrastructure.repositories.user import UserWriteRepository


class TestUserWriteRepository:
    @dataclass
    class TestData:
        __test__ = False
        email: str = "write@example.com"
        username: str = "write_user"
        password_hash: str = "hashed_pass"

        def to_create_schema(self) -> UserCreateSchema:
            return UserCreateSchema(
                email=self.email,
                username=self.username,
                password_hash=self.password_hash,
            )

    def _get_repo(self, session: AsyncSession) -> UserWriteRepository:
        return UserWriteRepository(session=session)

    async def test_create_user_success(self, session: AsyncSession) -> None:
        data = self.TestData()

        user = await self._get_repo(session).create(data.to_create_schema())

        assert user.email == data.email
        assert user.username == data.username

        stmt = select(UserModel).where(UserModel.id == user.id)
        db_user = (await session.execute(stmt)).scalar_one()

        assert db_user.id == user.id

    @pytest.mark.parametrize(
        "update_data",
        [
            {"username": "only_name"},
            {"password_hash": "only_hash"},
            {"username": "both", "password_hash": "both_hash"},
        ],
    )
    async def test_update_user_fields(self, session: AsyncSession, update_data: dict[str, str]) -> None:
        repo = self._get_repo(session)
        user = await repo.create(self.TestData().to_create_schema())

        update_schema = UserUpdateSchema(**update_data)
        await repo.update(user.id, update_schema)

        stmt = select(UserModel).where(UserModel.id == user.id)
        db_user = (await session.execute(stmt)).scalar_one()

        for key, value in update_data.items():
            assert getattr(db_user, key) == value

    async def test_update_user_not_found(self, session: AsyncSession) -> None:
        with pytest.raises(UserNotFoundException):
            await self._get_repo(session).update(uuid.uuid4(), UserUpdateSchema(username="any"))

    async def test_delete_user_success(self, session: AsyncSession) -> None:
        repo = self._get_repo(session)
        user = await repo.create(self.TestData().to_create_schema())

        assert await repo.delete_by_identity(user.id) is True

        stmt = select(UserModel).where(UserModel.id == user.id)
        db_user = (await session.execute(stmt)).scalar_one_or_none()
        assert db_user is None

    async def test_delete_user_not_found(self, session: AsyncSession) -> None:
        repo = self._get_repo(session)
        assert await repo.delete_by_identity(uuid.uuid4()) is False
