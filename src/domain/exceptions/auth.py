from typing import Self

from domain.exceptions import CustomException


class AuthException(CustomException):
    pass


class InvalidTokenException(AuthException):
    @classmethod
    def invalid_access(cls) -> Self:
        return cls("Invalid access token")

    @classmethod
    def invalid_refresh(cls) -> Self:
        return cls("Invalid refresh token")

    @classmethod
    def hash_mismatch(cls) -> Self:
        return cls("Token hash mismatch")


class TokenExpiredException(InvalidTokenException):
    @classmethod
    def access_expired(cls) -> Self:
        return cls("Access token has expired")

    @classmethod
    def refresh_expired(cls) -> Self:
        return cls("Refresh token has expired")


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


class InvalidCredentialsException(AuthException):
    def __init__(self, *, fields: list[str] | None = None) -> None:
        if fields is None:
            fields = ["email", "password"]
        super().__init__(f"Invalid {' or '.join(fields)}")
