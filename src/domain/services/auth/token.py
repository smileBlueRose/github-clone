from datetime import UTC, datetime
from uuid import uuid4

import jwt
from loguru import logger

from config import settings
from domain.entities.user import User
from domain.exceptions.auth import InvalidTokenException, TokenExpiredException
from domain.ports.service import BaseService
from domain.value_objects.token import AccessToken, AccessTokenPayload, RefreshToken, RefreshTokenPayload


class TokenService(BaseService):
    def __init__(
        self,
        private_key: str,
        public_key: str,
        access_token_lifetime: int = settings.auth.jwt.access_token_lifetime,
        refresh_token_lifetime: int = settings.auth.jwt.refresh_token_lifetime,
    ) -> None:
        self.__private_key = private_key
        self.public_key = public_key
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime

    # ================
    # ==== ACCESS ====
    # ================
    def generate_access(self, user: User) -> AccessToken:
        """Generate a new access token for a user."""
        issued_at = int(datetime.now(UTC).timestamp())
        expires_at = issued_at + self.access_token_lifetime

        payload = AccessTokenPayload(
            sub=user.id,
            email=user.email,
            iat=issued_at,
            exp=expires_at,
        )
        token: str = jwt.encode(
            payload.model_dump(mode="json"),
            key=self.__private_key,
            algorithm=settings.auth.jwt.algorithm,
        )
        return AccessToken(value=token)

    def _verify_access(self, token: AccessToken) -> AccessTokenPayload:
        """
        Verify access token and return its payload.

        :raises ExpiredSignatureError: If the token has expired.
        :raises PyJWTError: If the token is invalid for any other reason
                            (e.g., malformed, invalid signature, or missing required claims).
        :raises ValueError: If payload['type'] is not TokenTypeEnum.ACCESS
        """

        payload = jwt.decode(
            token.value,
            key=self.public_key,
            algorithms=[settings.auth.jwt.algorithm],
            options=settings.auth.jwt.access_decode_options,
        )
        return AccessTokenPayload(
            sub=payload["sub"],
            email=payload["email"],
            iat=payload["iat"],
            exp=payload["exp"],
            type=payload["type"],
        )

    def verify_access(self, token: AccessToken) -> AccessTokenPayload:
        """
        Verify access token and return its payload.

        :raises TokenExpiredException:
        :raises InvalidTokenException: If token verification fails.
        """
        try:
            return self._verify_access(token)
        except jwt.ExpiredSignatureError as e:
            logger.exception(e)
            raise TokenExpiredException("Access token has expired.") from e
        except (jwt.PyJWTError, ValueError) as e:
            logger.exception(e)
            raise InvalidTokenException("Invalid access token.") from e

    # =================
    # ==== REFRESH ====
    # =================
    def generate_refresh(self, user: User) -> RefreshToken:
        """Generate a new refresh token for a user."""
        issued_at = int(datetime.now(UTC).timestamp())
        expires_at = issued_at + self.refresh_token_lifetime

        payload = RefreshTokenPayload(
            sub=user.id,
            iat=issued_at,
            exp=expires_at,
            jti=uuid4(),
        )
        token: str = jwt.encode(
            payload.model_dump(mode="json"),
            key=self.__private_key,
            algorithm=settings.auth.jwt.algorithm,
        )
        return RefreshToken(value=token)

    def _verify_refresh(self, token: RefreshToken) -> RefreshTokenPayload:
        """
        Verify refresh token and return its payload.

        :raises ExpiredSignatureError: If the token has expired.
        :raises PyJWTError: If the token is invalid for any other reason
                            (e.g., malformed, invalid signature, or missing required claims).
        :raises ValueError: If payload['type'] is not TokenTypeEnum.REFRESH
        """
        payload = jwt.decode(
            token.value,
            key=self.public_key,
            algorithms=[settings.auth.jwt.algorithm],
            options=settings.auth.jwt.refresh_decode_options,
        )

        return RefreshTokenPayload(
            sub=payload["sub"],
            iat=payload["iat"],
            exp=payload["exp"],
            jti=payload["jti"],
            type=payload["type"],
        )

    def verify_refresh(self, token: RefreshToken) -> RefreshTokenPayload:
        """
        Verify refresh token and return its payload.
        :raises TokenExpiredException:
        :raises InvalidTokenException: If token verification fails.
        """
        try:
            return self._verify_refresh(token)
        except jwt.ExpiredSignatureError as e:
            logger.exception(e)
            raise TokenExpiredException("Refresh token has expired.") from e
        except (jwt.PyJWTError, ValueError) as e:
            logger.exception(e)
            raise InvalidTokenException("Invalid refresh token.") from e
