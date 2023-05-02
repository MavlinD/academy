from typing import Callable

import pytest
from faker import Faker
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


async def insert_fake_ads(amount_ads: int) -> None:
    """fill db with fake data"""
    fake = Faker("ru_RU")
    for i in range(amount_ads):
        await create_ad(
            price=fake.pydecimal(left_digits=7, right_digits=2, positive=True),
            name=fake.texts(max_nb_chars=200),
            desc=fake.texts(max_nb_chars=1000),
        )
