from functools import lru_cache

from dotenv import load_dotenv
from logrich.logger_ import log  # noqa
from pydantic import BaseSettings, EmailStr, Field, SecretStr, validator
from starlette.templating import Jinja2Templates

load_dotenv()


@lru_cache()
class Settings(BaseSettings):
    # Security settings
    DJANGO_SECRET_KEY: str

    DEBUG: bool = False
    MOUNT_DJANGO_APP: bool = True

    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOSTNAME: str = "0.0.0.0"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str


config = Settings()
