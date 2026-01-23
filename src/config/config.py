import os
import re
from datetime import UTC, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from loguru import logger
from pydantic import BaseModel, PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_DIR = Path(__file__).parent.parent
BASE_DIR = SRC_DIR.parent
TEMPLATE_ENV = BASE_DIR / ".env.template"

environment = os.getenv("ENV", None)

if environment == "default":
    env_file = BASE_DIR / ".env"
elif environment:
    env_file = BASE_DIR / f".env.{environment}"
else:
    raise ValueError("ENV environment variable is not set. Use 'default', 'dev', 'test', etc.")


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5000
    reload: bool = True


class ApiConfig(BaseModel):
    class ApiV1Confg(BaseModel):
        prefix: str = "/v1"
        users_prefix: str = "/users"

    # TODO: It's not a good structure. Late it will grow fast and become really big & complicated. Refactor it
    class AuthConfig(BaseModel):
        prefix: str = "/auth"
        register_prefix: str = "/register"
        register_methods: list[str] = ["POST"]

        login_prefix: str = "/login"
        login_methods: list[str] = ["POST"]

        refresh_prefix: str = "/refresh"
        refresh_methods: list[str] = ["POST"]

    prefix: str = "/api"
    v1: ApiV1Confg = ApiV1Confg()
    auth: AuthConfig = AuthConfig()


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
        if not self.password_file:
            logger.warning("Password file not provided")
            return ""

        try:
            return Path(self.password_file).read_text().strip()
        except FileNotFoundError:
            logger.warning(f"Password file not found at {self.password_file}")
            return ""

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

    class HashedPassword(BaseModel):
        max_length: int = 60  # brypt algorithm always gives a string of length 60

    class Email(BaseModel):
        max_length: int = 255

    username: Username = Username()
    hashed_password: HashedPassword = HashedPassword()
    email: Email = Email()


class TimeConfig(BaseModel):
    default_tz: timezone = UTC

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

        private_key_file_path: str
        public_key_file_path: str

        @property
        def private_key(self) -> str:
            return Path(self.private_key_file_path).read_text()

        @property
        def public_key(self) -> str:
            return Path(self.public_key_file_path).read_text()

    class TokenHash(BaseModel):
        algorithm: str = "sha256"
        length: int = 64

    class Password(BaseModel):
        min_length: int = 8
        max_length: int = 72  # limit for brcypt algorithm

        # Passwords contains at least one: lowercase letter, uppercase letter and digit
        pattern: re.Pattern[str] = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$")

    jwt: JWT
    token_hash: TokenHash = TokenHash()
    password: Password = Password()


class Logger(BaseModel):
    log_level: str


class SessionConfig(BaseModel):
    ip_max_length: int = 45
    ua_max_length: int = 512


class GitConfig(BaseModel):
    git_storage_base_path: Path = (
        Path(os.getenv("LOCALAPPDATA", "C:/Temp")) / "github-clone" / "repos" if os.name == "nt" else Path("/var/repos")
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(TEMPLATE_ENV, env_file),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    run: RunConfig = RunConfig()
    api: ApiConfig = ApiConfig()
    db: DatabaseConfig
    time: TimeConfig = TimeConfig()
    auth: AuthConfig
    logger: Logger
    session: SessionConfig = SessionConfig()

    user: UserConfig = UserConfig()


logger.info(f"Using {env_file}")
settings = Settings()  # type: ignore
