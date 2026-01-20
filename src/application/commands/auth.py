from pydantic import EmailStr

from application.ports.command import BaseCommand


class UserRegisterCommand(BaseCommand):
    email: EmailStr
    username: str
    password: str


class UserLoginCommand(BaseCommand):
    email: EmailStr
    password: str
