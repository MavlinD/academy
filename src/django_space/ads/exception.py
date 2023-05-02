from fastapi import HTTPException
from logrich.logger_ import log  # noqa
from starlette import status

from src.django_space.ads.models import Ads


class FastAPIAdsException(HTTPException):
    def __init__(self) -> None:
        self.detail: str = "Некорректный запрос"
        self.status_code: int = status.HTTP_400_BAD_REQUEST


class OverLimitAmountImages(FastAPIAdsException):
    def __init__(self, ad: Ads = None) -> None:
        if ad:
            self.detail = f'Объявление "{ad}" уже содержит максимально возможное кол-во изображений'
        else:
            self.detail = str(self)
        self.status_code = status.HTTP_400_BAD_REQUEST
