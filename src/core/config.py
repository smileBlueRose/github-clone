from pathlib import Path
from urllib.parse import quote_plus

from pydantic import BaseModel, PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5000
    reload: bool = True


class ApiConfig(BaseModel):
    prefix: str = "/api"


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str
    name: str
    password_file: str

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    def read_db_password(self) -> str:
        try:
            return Path(self.password_file).read_text().strip()
        except FileNotFoundError as e:
            raise ValueError(f"Password file not found at {self.password_file}") from e

    @property
    def url(self) -> PostgresDsn:
        password = quote_plus(self.read_db_password())
        return PostgresDsn(
            MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.user,
                password=password,
                host=self.host,
                port=self.port,
                path=self.name,
            )
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    run: RunConfig = RunConfig()
    api: ApiConfig = ApiConfig()
    db: DatabaseConfig


settings = Settings()  # type: ignore
