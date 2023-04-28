from typing import Generic

from fastapi_pagination import Page, Params
from fastapi_pagination.bases import RawParams, T


class ParamsForPost:
    """Параметры пагинации для пост запросов"""

    def to_raw_params(self) -> RawParams:
        return Params.to_raw_params(self)  # type: ignore


class PageForPost(Page[T], Generic[T]):
    __params_type__ = ParamsForPost  # type: ignore
