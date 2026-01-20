from pydantic import BaseModel, EmailStr


class LoginCredentials(BaseModel):
    email: EmailStr
    password: str
