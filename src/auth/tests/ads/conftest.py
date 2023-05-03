from typing import Callable

import pytest
from faker import Faker
from fastapi import FastAPI, HTTPException
from logrich.logger_ import log  # noqa

from src.auth.tests.app.test_tools import create_ad, create_image
from src.django_space.ads.config import config
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
    """fill db with fake data - Ads"""
    fake = Faker("ru_RU")
    for i in range(amount_ads):
        await create_ad(
            price=fake.pydecimal(left_digits=7, right_digits=2, positive=True),
            name=fake.texts(nb_texts=1, max_nb_chars=100)[0],
            desc=fake.texts(nb_texts=1, max_nb_chars=500)[0],
        )


async def insert_fake_images(amount_ads: int) -> None:
    """fill db with fake data - Images"""
    fake = Faker()
    for i in range(1, amount_ads + 2):
        for image in range(config.AD_IMAGE_MAX_AMOUNT):
            path = fake.file_path(depth=3, category="image")
            is_main = False
            if image == 1:
                is_main = True
            # log.debug(path)
            await create_image(
                path=path,
                ads_id=i,
                is_main=is_main
                # is_main=fake.pybool()
            )
