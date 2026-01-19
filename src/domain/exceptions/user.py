from typing import Self
from uuid import UUID

from pydantic import EmailStr

from domain.exceptions import CustomException
from domain.exceptions.common import AlreadyExistsException, NotFoundException


class UserException(CustomException):
    pass


class UserNotFoundException(UserException, NotFoundException):
    def __init__(
        self, *, user_id: UUID | None = None, email: EmailStr | None = None, username: str | None = None
    ) -> None:
        self.user_id = user_id
        self.email = email
        self.username = username


class UserAlreadyExistsException(UserException, AlreadyExistsException):
    def __init__(self, *, email: EmailStr | None = None, username: str | None = None) -> None:
        self.email = email
        self.username = username

        if email:
            self.message = f"User with email '{email}' already exists"
        elif username:
            self.message = f"User with username '{username}' already exists"
        else:
            self.message = "User already exists"

        super().__init__(self.message)


class InvalidUsernameException(UserException):
    @classmethod
    def too_short(cls, min_len: int) -> Self:
        return cls(f"Username must be at least {min_len} characters long.")

    @classmethod
    def too_long(cls, max_len: int) -> Self:
        return cls(f"Username must not exceed {max_len} characters.")
