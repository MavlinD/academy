from functools import lru_cache

from dotenv import load_dotenv
from logrich.logger_ import log  # noqa
from pydantic import BaseSettings, Field
from pydantic.schema import Decimal

load_dotenv()


@lru_cache()
class Settings(BaseSettings):
    """
    Ad config settings
    """

    # ограничения на имя объявления
    AD_NAME_MIN_LENGTH: int = 3
    AD_NAME_MAX_LENGTH: int = 200

    # ограничения на описание объявления
    AD_DESC_MIN_LENGTH: int = 3
    AD_DESC_MAX_LENGTH: int = 1000

    # тестовое объявление
    TEST_AD_NAME: str = "Продам славянский шкаф"
    TEST_AD_PRICE: Decimal | None = Field(15730.45, decimal_places=2)
    TEST_AD_DESC: str = "Прекрасный шкаф светлого дерева"

    # тестовое изображение
    TEST_IMAGE_PATH: str = "test-image.png"

    class Config:
        env_file_encoding = "utf-8"


config = Settings()
