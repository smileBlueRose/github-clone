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

# TODO: add context
class UserAlreadyExistsException(UserException, AlreadyExistsException):
    pass

# TODO: add context
class InvalidUsernameException(UserException):
    pass
