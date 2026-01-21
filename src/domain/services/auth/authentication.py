import bcrypt

from domain.entities.user import User
from domain.exceptions.auth import InvalidCredentialsException
from domain.exceptions.user import UserNotFoundException
from domain.ports.repositories.user import AbstractUserReadRepository
from domain.ports.service import BaseService
from domain.services.auth.token import TokenService
from domain.value_objects.auth import LoginCredentials
from domain.value_objects.token import AccessTokenVo, RefreshTokenVo


class AuthenticationService(BaseService):
    def __init__(self, token_service: TokenService, user_read_repository: AbstractUserReadRepository) -> None:
        self._token_service = token_service
        self._read_repository = user_read_repository

    # TODO: revoke previous token with the same user_id + user_agent
    async def login(self, credentials: LoginCredentials) -> tuple[AccessTokenVo, RefreshTokenVo]:
        """:raises InvalidCredentialsException:"""

        user = await self._authenticate_user(credentials=credentials)
        access = self._token_service.generate_access(user=user)
        refresh = self._token_service.generate_refresh(user=user)

        return access, refresh

    async def _authenticate_user(self, credentials: LoginCredentials) -> User:
        """:raises InvalidCredentialsException:"""

        try:
            user: User = await self._read_repository.get_by_email(email=credentials.email)
        except UserNotFoundException as e:
            raise InvalidCredentialsException() from e

        if not self.check_password(password=credentials.password, hashed_password=user.password_hash):
            raise InvalidCredentialsException()

        return user

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password=password.encode("utf-8"), hashed_password=hashed_password.encode("utf-8"))
