from pydantic import BaseModel


class UserAgent(BaseModel):
    value: str


class IpAddress(BaseModel):
    value: str
