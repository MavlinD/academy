import pytest
from faker import Faker
from fastapi import FastAPI, HTTPException
from logrich.logger_ import log  # noqa

from src.auth.tests.app.test_tools import create_ad
from src.django_space.ads.models import Ads


@pytest.fixture
async def add_test_ad(app: FastAPI) -> Ads | HTTPException:
    """Добавляет тестовое объявление в БД"""
    ad = await create_ad()
    return ad
