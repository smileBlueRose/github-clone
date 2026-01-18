from uuid import UUID

from pydantic import BaseModel, EmailStr

from domain.enums.token_type import TokenTypeEnum
from typing import Literal


class AccessTokenPayload(BaseModel):
    sub: UUID
    email: EmailStr

    iat: int
    exp: int

    type: Literal[TokenTypeEnum.ACCESS] = TokenTypeEnum.ACCESS


class RefreshTokenPayload(BaseModel):
    sub: UUID

    iat: int
    exp: int

    jti: UUID

    type: Literal[TokenTypeEnum.REFRESH] = TokenTypeEnum.REFRESH


class AccessToken(BaseModel):
    value: str


class RefreshToken(BaseModel):
    value: str


class TokensPair(BaseModel):
    access: AccessToken
    refresh: RefreshToken
