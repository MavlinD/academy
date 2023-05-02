from typing import Callable

import pytest
from fastapi import FastAPI, HTTPException
from logrich.logger_ import log  # noqa

from src.auth.tests.app.test_tools import create_ad, create_image
from src.django_space.ads.models import Ads, Image


@pytest.fixture
async def add_test_ad(app: FastAPI) -> Ads | HTTPException:
    """Добавляет тестовое объявление в БД"""
    ad = await create_ad()
    return ad


@pytest.fixture
async def add_test_image(app: FastAPI, add_test_ad: Callable) -> Image | HTTPException:
    """Добавляет тестовое изображение в БД"""
    image = await create_image()
    return image
