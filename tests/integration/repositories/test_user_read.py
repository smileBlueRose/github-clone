import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from domain.filters.user import UserFilter
from domain.schemas.user import UserCreateSchema
from infrastructure.repositories.user import UserReadRepository, UserWriteRepository
from tests.utils import create_user_model


class TestUserReadRepository:
    @dataclass
    class TestData:
        __test__ = False
        email: str = "read@example.com"
        username: str = "read_user"
        password_hash: str = "hash"

        def to_create_schema(self) -> UserCreateSchema:
            return UserCreateSchema(
                email=self.email,
                username=self.username,
                password_hash=self.password_hash,
            )

    async def _setup_user(self, session: AsyncSession, data: TestData | None = None) -> uuid.UUID:
        write_repo = UserWriteRepository(session=session)
        test_data = data or self.TestData()
        user = await write_repo.create(test_data.to_create_schema())
        return user.id

    def _get_repo(self, session: AsyncSession) -> UserReadRepository:
        return UserReadRepository(session=session)

    async def test_get_by_identity_success(self, session: AsyncSession) -> None:
        user_id = await self._setup_user(session)

        user = await self._get_repo(session).get_by_identity(user_id)
        assert user.id == user_id

    async def test_get_by_email_success(self, session: AsyncSession) -> None:
        await self._setup_user(session)

        user = await self._get_repo(session).get_by_email(self.TestData.email)
        assert user.email == self.TestData.email

    async def test_get_by_username_success(self, session: AsyncSession) -> None:
        await self._setup_user(session)

        user = await self._get_repo(session).get_by_username(self.TestData.username)
        assert user.username == self.TestData.username

    async def test_get_all_users(self, session: AsyncSession) -> None:
        user_count = 3

        for i in range(user_count):
            await create_user_model(session, email=f"email_{i}@test.me", username=f"username_{i}")

        users = await self._get_repo(session).get_all(UserFilter())

        assert len(users) == user_count
