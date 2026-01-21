from dataclasses import dataclass
from unittest.mock import MagicMock

import bcrypt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from utils import create_user_model

from domain.exceptions.auth import InvalidCredentialsException
from domain.services.auth.authentication import AuthenticationService
from domain.services.auth.token import TokenService
from domain.value_objects.auth import LoginCredentials
from domain.value_objects.token import AccessTokenVo, RefreshTokenVo
from infrastructure.repositories.user import UserReadRepository


class TestAuthenticationService:
    @dataclass
    class TestData:
        __test__ = False

        email: str = "test@example.com"
        username: str = "test_user"
        password: str = "Password123!"

    data = TestData()

    def service(self, session: AsyncSession) -> AuthenticationService:
        token_service = MagicMock(spec=TokenService)
        token_service.generate_access.return_value = MagicMock(spec=AccessTokenVo)
        token_service.generate_refresh.return_value = MagicMock(spec=RefreshTokenVo)

        return AuthenticationService(
            token_service=token_service,
            user_read_repository=UserReadRepository(session=session),
        )

    async def test_login_success(self, session: AsyncSession) -> None:
        await create_user_model(
            session=session,
            email=self.data.email,
            username=self.data.username,
            password=self.data.password,
        )

        credentials = LoginCredentials(email=self.data.email, password=self.data.password)
        access, refresh = await self.service(session).login(credentials)

        assert isinstance(access, AccessTokenVo)
        assert isinstance(refresh, RefreshTokenVo)

    async def test_login_not_existing_email(self, session: AsyncSession) -> None:
        credentials = LoginCredentials(email="not_existing_email@example.com", password=self.data.password)
        with pytest.raises(InvalidCredentialsException):
            await self.service(session).login(credentials)

    async def test_login_invalid_password(self, session: AsyncSession) -> None:
        await create_user_model(session=session, email=self.data.email)
        credentials = LoginCredentials(email=self.data.email, password="wrong_password")
        with pytest.raises(InvalidCredentialsException):
            await self.service(session).login(credentials)

    async def test_authenticate_user_success(self, session: AsyncSession) -> None:
        await create_user_model(
            session=session,
            email=self.data.email,
            password=self.data.password,
        )
        credentials = LoginCredentials(email=self.data.email, password=self.data.password)
        user = await self.service(session)._authenticate_user(credentials)
        assert user.email == self.data.email

    def test_check_password_logic(self, session: AsyncSession) -> None:
        password = "test_password"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        assert self.service(session).check_password(password, hashed) is True
        assert self.service(session).check_password("wrong", hashed) is False
