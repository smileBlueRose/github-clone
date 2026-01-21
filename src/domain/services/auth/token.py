import hashlib
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import jwt

from config import settings
from domain.entities.user import User
from domain.exceptions.auth import InvalidTokenException, TokenExpiredException
from domain.ports.service import BaseService
from domain.value_objects.token import AccessTokenPayload, AccessTokenVo, RefreshTokenPayload, RefreshTokenVo


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
    def generate_access(self, user: User) -> AccessTokenVo:
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
        return AccessTokenVo(value=token)

    def _verify_access(self, token: AccessTokenVo) -> AccessTokenPayload:
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

    def verify_access(self, token: AccessTokenVo) -> AccessTokenPayload:
        """
        Verify access token and return its payload.

        :raises TokenExpiredException:
        :raises InvalidTokenException: If token verification fails.
        """
        try:
            return self._verify_access(token)
        except jwt.ExpiredSignatureError as e:
            raise TokenExpiredException.access_expired() from e
        except (jwt.PyJWTError, ValueError) as e:
            raise InvalidTokenException.invalid_access() from e

    # =================
    # ==== REFRESH ====
    # =================
    def generate_refresh(self, user: User) -> RefreshTokenVo:
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
        return RefreshTokenVo(value=token)

    def _verify_refresh(self, token: RefreshTokenVo) -> RefreshTokenPayload:
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

        return self._payload_dict_to_refresh_payload(payload)

    def verify_refresh(self, token: RefreshTokenVo) -> RefreshTokenPayload:
        """
        Verify refresh token and return its payload.
        :raises TokenExpiredException:
        :raises InvalidTokenException: If token verification fails.
        """
        try:
            return self._verify_refresh(token)
        except jwt.ExpiredSignatureError as e:
            raise TokenExpiredException.refresh_expired() from e
        except (jwt.PyJWTError, ValueError) as e:
            raise InvalidTokenException.invalid_refresh() from e

    def parse_refresh_without_verification(self, token: RefreshTokenVo) -> RefreshTokenPayload:
        """
        Parse refresh token payload WITHOUT cryptographic verification.

        WARNING: This method skips signature verification for performance reasons.
        Use ONLY when you are 100% certain the token is valid.

        Valid use cases:
        1. You need the payload from a token you just generated (e.g., after generate_refresh()
        to extract jti, iat, exp for database storage)
        2. Token comes from a trusted internal source where verification is unnecessary

        NEVER use this method on tokens from untrusted sources or user input.

        This method assumes the token is well-formed. Errors like PyJWTError or KeyError
        are NOT handled and will propagate, as they indicate programmer error.
        """
        payload = jwt.decode(
            token.value,
            key=self.public_key,
            algorithms=[settings.auth.jwt.algorithm],
            options={**settings.auth.jwt.refresh_decode_options, "verify_signature": False},
        )
        return self._payload_dict_to_refresh_payload(payload)

    @staticmethod
    def _payload_dict_to_refresh_payload(payload: dict[str, Any]) -> RefreshTokenPayload:
        """Convert JWT payload dictionary to RefreshTokenPayload object."""
        return RefreshTokenPayload(
            sub=payload["sub"],
            iat=payload["iat"],
            exp=payload["exp"],
            jti=payload["jti"],
            type=payload["type"],
        )
    # ================
    # ==== COMMON ====
    # ================
    @staticmethod
    def hash_token(token: str) -> str:
        """:raises ValueError:"""

        algorithm: str = settings.auth.token_hash.algorithm

        if algorithm == "sha256":
            return hashlib.sha256(token.encode("utf-8")).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(token.encode("utf-8")).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}. Use 'sha256' or 'sha512'")
