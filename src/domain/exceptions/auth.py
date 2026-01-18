from domain.exceptions import CustomException


class AuthException(CustomException):
    pass


class InvalidTokenException(AuthException):
    pass


class TokenExpiredException(InvalidTokenException):
    pass
