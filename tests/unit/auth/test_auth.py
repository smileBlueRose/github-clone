from unittest.mock import Mock
from uuid import UUID

import jwt
import pytest

from config import settings
from domain.entities.user import User
from domain.enums.token_type import TokenTypeEnum
from domain.exceptions.auth import InvalidTokenException, TokenExpiredException
from domain.services.auth.token import TokenService
from domain.value_objects.token import AccessTokenVo, AccessTokenPayload, RefreshTokenVo

LIFETIME = 3600


@pytest.fixture(scope="function")
def token_service(private_key: str, public_key: str) -> TokenService:
    return TokenService(
        private_key=private_key,
        public_key=public_key,
    )


# ================
# ==== ACCESS ====
# ================
@pytest.fixture(scope="function")
def token_service_with_another_keys(another_private_key: str, another_public_key: str) -> TokenService:
    return TokenService(
        private_key=another_private_key,
        public_key=another_public_key,
    )


def test_generate_and_verify_access_success(token_service: TokenService, user: Mock) -> None:
    token = token_service.generate_access(user)
    payload = token_service.verify_access(token)

    assert payload.sub == user.id
    assert payload.email == user.email
    assert payload.type == TokenTypeEnum.ACCESS


def test_verify_access_expired(token_service: TokenService, user: User) -> None:
    token_service.access_token_lifetime = 0
    token = token_service.generate_access(user)

    with pytest.raises(TokenExpiredException):
        token_service.verify_access(token)


def test_verify_access_with_incorrect_token(token_service: TokenService, user: User) -> None:
    token = token_service.generate_access(user)
    invalid_token = AccessTokenVo(value=token.value + "garbage")

    with pytest.raises(InvalidTokenException):
        token_service.verify_access(invalid_token)


def test_verify_access_another_private_key(
    token_service: TokenService,
    token_service_with_another_keys: TokenService,
    user: User,
) -> None:
    token = token_service_with_another_keys.generate_access(user)

    with pytest.raises(InvalidTokenException):
        token_service.verify_access(token)


def test_verify_access_without_required_field(token_service: TokenService, user: User, private_key: str) -> None:
    payload: AccessTokenPayload = token_service.verify_access(token_service.generate_access(user))

    for field in settings.auth.jwt.access_decode_options["require"]:
        bad_payload = payload.model_dump(mode="json")

        bad_payload.pop(field)  # remove required field

        bad_token_value = jwt.encode(
            bad_payload,
            key=private_key,
            algorithm=settings.auth.jwt.algorithm,
        )
        with pytest.raises(InvalidTokenException):
            token_service.verify_access(AccessTokenVo(value=bad_token_value))


# =================
# ==== REFRESH ====
# =================
def test_generate_and_verify_refresh_success(token_service: TokenService, user: User) -> None:
    token = token_service.generate_refresh(user)
    payload = token_service.verify_refresh(token)

    assert payload.sub == user.id
    assert payload.type == TokenTypeEnum.REFRESH
    assert isinstance(payload.jti, UUID)


def test_verify_refresh_expired(token_service: TokenService, user: User) -> None:
    token_service.refresh_token_lifetime = 0
    token = token_service.generate_refresh(user)

    with pytest.raises(TokenExpiredException):
        token_service.verify_refresh(token)


def test_verify_refresh_with_incorrect_token(token_service: TokenService, user: User) -> None:
    token = token_service.generate_refresh(user)
    invalid_token = RefreshTokenVo(value=token.value + "garbage")

    with pytest.raises(InvalidTokenException):
        token_service.verify_refresh(invalid_token)


def test_verify_refresh_another_private_key(
    token_service: TokenService,
    token_service_with_another_keys: TokenService,
    user: User,
) -> None:
    token = token_service_with_another_keys.generate_refresh(user)

    with pytest.raises(InvalidTokenException):
        token_service.verify_refresh(token)


def test_verify_refresh_without_required_field(token_service: TokenService, user: User, private_key: str) -> None:
    payload = token_service.verify_refresh(token_service.generate_refresh(user))

    for field in settings.auth.jwt.refresh_decode_options["require"]:
        bad_payload = payload.model_dump(mode="json")
        bad_payload.pop(field)

        bad_token_value = jwt.encode(
            bad_payload,
            key=private_key,
            algorithm=settings.auth.jwt.algorithm,
        )
        with pytest.raises(InvalidTokenException):
            token_service.verify_refresh(RefreshTokenVo(value=bad_token_value))


def test_cross_token_verification_fail(token_service: TokenService, user: User) -> None:
    access_token = token_service.generate_access(user)
    refresh_token = token_service.generate_refresh(user)

    # Access should not pass verification as Refresh
    with pytest.raises(InvalidTokenException):
        token_service.verify_refresh(RefreshTokenVo(value=access_token.value))

    # Refresh should not pass verification as Access
    with pytest.raises(InvalidTokenException):
        token_service.verify_access(AccessTokenVo(value=refresh_token.value))
