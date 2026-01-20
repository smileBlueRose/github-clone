from pydantic import BaseModel
from pydantic import EmailStr


class LoginCredentials(BaseModel):
    email: EmailStr
    password: str
