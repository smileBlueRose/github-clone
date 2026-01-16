from pydantic import BaseModel
from pydantic_settings import BaseSettings


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5000
    reload: bool = True

class ApiConfig(BaseModel):
    prefix: str = '/api'

class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiConfig = ApiConfig()

settings = Settings()