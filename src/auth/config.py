from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from logrich.logger_ import log  # noqa
from pydantic import BaseSettings, EmailStr, Field, SecretStr, validator
from starlette.templating import Jinja2Templates

from src.auth.assets import get_key
from src.auth.schemas.user import limit_of_password, uniq_attribute

load_dotenv()

templates = Jinja2Templates(directory="src/auth/static")


@lru_cache()
class Settings(BaseSettings):
    """
    Server config settings
    """

    class Config:
        env_file_encoding = "utf-8"

    # Security settings
    DJANGO_SECRET_KEY: str

    VERIFICATION_TOKEN_LIFETIME_SECONDS: int = 0
    RESET_PASSWORD_TOKEN_LIFETIME_SECONDS: int = 7200

    JWT_ALGORITHM: str = "ES256"
    PRIVATE_KEY: str
    PUBLIC_KEY: str

    @validator("PRIVATE_KEY")
    def private_key_validator(cls, v: str) -> str:
        return get_key(key=v)

    @validator("PUBLIC_KEY")
    def public_key_validator(cls, v: str) -> str:
        return get_key(key=v)

    JWT_ACCESS_KEY_EXPIRES_TIME_MINUTES: int = 120
    JWT_REFRESH_KEY_EXPIRES_TIME_DAYS: int = 30
    TOKEN_ISS: str
    TOKEN_AUDIENCE: str | List[str] | None
    # TOKEN_AUDIENCE_VERIFY: str = "fastapi-users:verify"
    TOKEN_SUB: str | List[str] | None = "auth"

    # FastMail SMTP server settings
    MAIL_CONSOLE: bool = True
    SUPPRESS_SEND: bool = True
    MAIL_SERVER: str = "smtp.users.io"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: SecretStr = Field("")
    MAIL_SENDER: str = "noreply@users.io"
    ROOT_API_URL: str = ""
    PASSWORD_RESET_URL: str = ""
    VERIFICATION_URL: str = ""
    API_PORT_INTERNAL: int
    API_HOSTNAME: str = "0.0.0.0"

    API_VERSION: str = "v2"
    API_PATH_PREFIX: str = "/api/"

    DEBUG: bool = False
    TESTING: bool = False
    RELOAD: bool = False
    LOG_LEVEL: int = 0

    TEST_USER_EMAIL: EmailStr = Field("test_sec@loc.loc")
    TEST_USER_USERNAME: str | None
    TEST_USER_PASSWORD: limit_of_password | None
    TEST_USER_FIRST_NAME: str | None

    DBS_ENGINE: str

    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOSTNAME: str = "0.0.0.0"
    PG_PORT_EXTERNAL: int = 5432
    POSTGRES_DB: str

    FIRST_USER_EMAIL: EmailStr | None
    FIRST_USER_USERNAME: uniq_attribute | None
    FIRST_USER_PASSWORD: limit_of_password | None

    USERNAME_ATTR_MIN_LENGTH: int = 3
    USERNAME_ATTR_MAX_LENGTH: int = 150


config = Settings()
