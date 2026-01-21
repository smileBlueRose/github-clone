from dataclasses import asdict, dataclass

import bcrypt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from utils import create_user_model

from domain.exceptions.auth import WeakPasswordException
from domain.exceptions.user import InvalidUsernameException, UserAlreadyExistsException
from domain.services.auth.registration import RegistrationService
from infrastructure.repositories.user import UserReadRepository


class TestRegistrationService:
    @dataclass
    class TestData:
        __test__ = False

        email: str
        username: str
        password: str

    data = TestData(
        email="test@example.com",
        username="valid_user",
        password="SafePassword123!",
    )

    def service(self, session: AsyncSession) -> RegistrationService:
        return RegistrationService(read_repository=UserReadRepository(session=session))

    async def test_validate_registration_success(self, session: AsyncSession) -> None:
        await self.service(session).validate_registration(**asdict(self.data))

    async def test_validate_registration_email_exists(self, session: AsyncSession) -> None:
        await create_user_model(session, email=self.data.email, username="another")
        with pytest.raises(UserAlreadyExistsException):
            await self.service(session).validate_registration(**asdict(self.data))

    async def test_validate_registration_username_exists(self, session: AsyncSession) -> None:
        await create_user_model(session, email="another@example.com", username=self.data.username)
        with pytest.raises(UserAlreadyExistsException):
            await self.service(session).validate_registration(**asdict(self.data))

    @pytest.mark.parametrize("password", ["short", "a" * 100, "nopatterndigits"])
    async def test_password_policy_violations(self, session: AsyncSession, password: str) -> None:
        with pytest.raises(WeakPasswordException):
            self.service(session)._check_password_policy(password)

    @pytest.mark.parametrize("username", ["u", "a" * 500])
    async def test_username_policy_violations(self, session: AsyncSession, username: str) -> None:
        with pytest.raises(InvalidUsernameException):
            self.service(session)._check_username_policy(username)

    async def test_prepare_user_create_schema_mapping(self, session: AsyncSession) -> None:
        schema = self.service(session).prepare_user_create_schema(**asdict(self.data))
        assert schema.email == self.data.email
        assert schema.username == self.data.username
        assert bcrypt.checkpw(self.data.password.encode(), schema.hashed_password.encode())

    async def test_email_exists(self, session: AsyncSession) -> None:
        await create_user_model(session=session, email=self.data.email)
        assert await self.service(session)._email_exists(self.data.email) is True
        assert await self.service(session)._email_exists("non-existent@test.com") is False

    async def test_username_exists_helper(self, session: AsyncSession) -> None:
        await create_user_model(session=session, username=self.data.username)
        assert await self.service(session)._username_exists(self.data.username) is True
        assert await self.service(session)._username_exists("unknown_user") is False
