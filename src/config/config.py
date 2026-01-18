from datetime import UTC, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from pydantic import BaseModel, PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_DIR = Path(__file__).parent.parent


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5000
    reload: bool = True


class ApiV1Confg(BaseModel):
    prefix: str = "/v1"
    users_prefix: str = "/users"


class ApiConfig(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Confg = ApiV1Confg()


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

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

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


class UserConfig(BaseModel):
    class Username(BaseModel):
        min_length: int = 3
        max_length: int = 255

    class Password(BaseModel):
        min_length: int = 8
        max_length: int = 72  # limit for brcypt algorithm

    class HashedPassword(BaseModel):
        max_length: int = 60  # brypt algorithm always gives a string of length 60

    class Email(BaseModel):
        max_length: int = 255

    username: Username = Username()
    password: Password = Password()
    hashed_password: HashedPassword = HashedPassword()
    email: Email = Email()


class TimeConfig(BaseModel):
    default_tz: timezone = UTC
    db_tz: timezone = UTC

    model_config = {"arbitrary_types_allowed": True}


class AuthConfig(BaseModel):
    class JWT(BaseModel):
        algorithm: str = "RS256"

        access_token_lifetime: int = 15 * 60  # 15 minutes
        refresh_token_lifetime: int = 30 * 24 * 3600  # 30 days

        access_decode_options: dict[str, Any] = {
            "verify_signature": True,
            "require": ("sub", "email", "iat", "exp", "type"),
        }
        refresh_decode_options: dict[str, Any] = {
            "verify_signature": True,
            "require": ("sub", "iat", "exp", "jti", "type"),
        }

    jwt: JWT = JWT()


class Logger(BaseModel):
    log_level: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(SRC_DIR / ".env.template", SRC_DIR / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    run: RunConfig = RunConfig()
    api: ApiConfig = ApiConfig()
    db: DatabaseConfig
    time: TimeConfig = TimeConfig()
    auth: AuthConfig = AuthConfig()
    logger: Logger

    user: UserConfig = UserConfig()


settings = Settings()  # type: ignore
