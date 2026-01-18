from domain.exceptions import CustomException
from domain.exceptions.common import AlreadyExistsException, NotFoundException


class UserException(CustomException):
    pass


class UserNotFoundException(UserException, NotFoundException):
    pass


class UserAlreadyExistsException(UserException, AlreadyExistsException):
    pass


class InvalidUsernameException(UserException):
    pass
