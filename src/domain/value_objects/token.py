from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr

from domain.enums.token_type import TokenTypeEnum


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


class AccessTokenVo(BaseModel):
    value: str


class RefreshTokenVo(BaseModel):
    value: str
