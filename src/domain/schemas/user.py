from pydantic import EmailStr

from domain.ports.schemas import BaseCreateSchema, BaseUpdateSchema


class UserCreateSchema(BaseCreateSchema):
    email: EmailStr
    username: str
    hashed_password: str


class UserUpdateSchema(BaseUpdateSchema):
    pass
