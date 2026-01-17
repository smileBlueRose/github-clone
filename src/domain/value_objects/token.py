from uuid import UUID

from pydantic import BaseModel

from domain.enums.token_type import TokenTypeEnum


class AccessTokenPayload(BaseModel):
    sub: UUID

    exp: int
    iat: int

    type: TokenTypeEnum = TokenTypeEnum.ACCESS


class RefreshTokenPayload(BaseModel):
    sub: UUID

    exp: int
    iat: int

    jti: UUID

    type: TokenTypeEnum = TokenTypeEnum.REFRESH


class AccessToken(BaseModel):
    value: str


class RefreshToken(BaseModel):
    value: str


class TokensPair(BaseModel):
    access: AccessToken
    refresh: RefreshToken
