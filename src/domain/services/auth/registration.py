import re

import bcrypt
from pydantic import EmailStr

from config import settings
from domain.exceptions.auth import WeakPasswordException
from domain.exceptions.user import InvalidUsernameException, UserAlreadyExistsException, UserNotFoundException
from domain.ports.repositories.user import AbstractUserReadRepository
from domain.ports.service import BaseService
from domain.schemas.user import UserCreateSchema


class RegistrationService(BaseService):
    def __init__(
        self,
        read_repository: AbstractUserReadRepository,
    ) -> None:
        super().__init__()
        self.read_repository = read_repository

    async def validate_registration(
        self,
        email: EmailStr,
        username: str,
        password: str,
    ) -> None:
        """
        Validate user registration data against business rules and existing records.

        :raises UserAlreadyExistsException:
        :raises WeakPasswordException:
        :raises InvalidUsernameException:
        """

        if await self._email_exists(email=email):
            raise UserAlreadyExistsException(email=email)

        if await self._username_exists(username=username):
            raise UserAlreadyExistsException(username=username)

        self._check_username_policy(username=username)
        self._check_password_policy(password=password)

    def prepare_user_create_schema(self, email: EmailStr, username: str, password: str) -> UserCreateSchema:
        hashed_password = self._hash_password(password=password)
        return UserCreateSchema(email=email, username=username, password_hash=hashed_password)

    async def _email_exists(self, email: EmailStr) -> bool:
        """Check if a user exists by their email address."""
        try:
            await self.read_repository.get_by_email(email=email)
            return True
        except UserNotFoundException:
            return False

    async def _username_exists(self, username: str) -> bool:
        """Check if a user exists by their username."""
        try:
            await self.read_repository.get_by_username(username=username)
            return True
        except UserNotFoundException:
            return False

    def _check_password_policy(self, password: str) -> None:
        """
        Checks password for compliance with business rules.

        :raises WeakPasswordException:
        """

        if len(password) < settings.auth.password.min_length:
            raise WeakPasswordException.too_short(settings.auth.password.min_length)
        if len(password) > settings.auth.password.max_length:
            raise WeakPasswordException.too_long(settings.auth.password.max_length)
        if not re.match(settings.auth.password.pattern, password):
            raise WeakPasswordException.weak_pattern()

    def _check_username_policy(self, username: str) -> None:
        """
        Checks username for compliance with business rules.

        :raises InvalidUsernameException:
        """
        if len(username) < settings.user.username.min_length:
            raise InvalidUsernameException.too_short(settings.user.username.min_length)
        if len(username) > settings.user.username.max_length:
            raise InvalidUsernameException.too_long(settings.user.username.max_length)

    def _hash_password(self, password: str) -> str:
        salt: bytes = bcrypt.gensalt()
        hashed_password: bytes = bcrypt.hashpw(password.encode(), salt)
        return hashed_password.decode()
