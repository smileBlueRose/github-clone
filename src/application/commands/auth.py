from pydantic import EmailStr, Field, IPvAnyAddress

from application.ports.command import BaseCommand
from config import settings


# TODO: Add base sanitization to commands
class UserRegisterCommand(BaseCommand):
    email: EmailStr
    username: str
    password: str


class UserLoginCommand(BaseCommand):
    email: EmailStr
    password: str

    ip_address: IPvAnyAddress
    user_agent: str = Field(max_length=settings.session.ua_max_length)
