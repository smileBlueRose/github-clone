from pydantic import EmailStr

from domain.ports.schemas import BaseCreateSchema, BaseUpdateSchema


class UserCreateSchema(BaseCreateSchema):
    email: EmailStr
    username: str
    password_hash: str


class UserUpdateSchema(BaseUpdateSchema):
    username: str | None = None
    password_hash: str | None = None
