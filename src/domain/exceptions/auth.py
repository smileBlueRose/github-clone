from typing import Self

from domain.exceptions import CustomException


class AuthException(CustomException):
    pass


class InvalidTokenException(AuthException):
    pass


class TokenExpiredException(InvalidTokenException):
    pass


class WeakPasswordException(AuthException):
    @classmethod
    def too_short(cls, min_len: int) -> Self:
        return cls(f"Password must be at least {min_len} characters long")

    @classmethod
    def too_long(cls, max_len: int) -> Self:
        return cls(f"Password must not exceed {max_len} characters")

    @classmethod
    def weak_pattern(cls) -> Self:
        return cls("Password must contain at least one digit, upper and lower case letters")
