# type: ignore
import time
from datetime import datetime, timedelta

import jwt
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from httpx import AsyncClient
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.conftest import Routs
from src.auth.users.security.jwt_tools import decode_jwt

skip = False
# skip = True
reason = "Temporary off!!"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_token_obtain(client: AsyncClient, routes: Routs, create_group_fixture) -> None:
    """Тест запроса JWT токена"""
    # определяем модель пользователя
    user_model = get_user_model()
    # получаем перового пользователя
    first_user = get_object_or_404(user_model, username=config.FIRST_USER_USERNAME)
    # log.debug(first_user)
    # получаем тестовую группу
    test_group = get_object_or_404(Group, name=config.TEST_GROUP)
    # log.debug(test_group)
    # добавляем первого п-ля в тестовую группу
    test_group.user_set.add(first_user)

    user = {
        "username": config.FIRST_USER_USERNAME,
        "password": config.FIRST_USER_PASSWORD,
    }
    resp = await client.post(routes.token_obtain, data=user)
    assert resp.status_code == 200
    # log.trace(resp)
    data = resp.json()
    # log.debug("", o=data)
    # return
    access_token = decode_jwt(data.get("access_token"))
    # log.debug("-", o=access_token)
    # log.debug(resp.text)
    # log.debug("", o=access_token)
    # log.debug(resp.headers)
    # assert resp.headers.get("access-control-allow-credentials")
    # assert resp.headers.get("access-control-allow-origin", "*")
    assert access_token.get("sub") == config.TOKEN_SUB
    assert access_token.get("username") == config.FIRST_USER_USERNAME
    assert access_token.get("aud") == config.TOKEN_AUDIENCE

    # сначала проверяем время истечения для рефреш
    decoded_payload = jwt.decode(
        jwt=data.get("refresh_token"),
        audience=config.TOKEN_AUDIENCE,
        key=config.PRIVATE_KEY,
        algorithms=[str(config.JWT_ALGORITHM)],
    )
    # log.debug("", o=decoded_payload)
    # return
    now = datetime.now()
    exp = time.localtime(decoded_payload["exp"])
    decoded_dtm = datetime(
        year=exp.tm_year,
        month=exp.tm_mon,
        day=exp.tm_mday,
        hour=exp.tm_hour,
        minute=exp.tm_min,
        second=exp.tm_sec,
    )
    decoded_str = datetime.strftime(decoded_dtm, "%d %b %Y %H:%M")
    exp_td = timedelta(
        days=config.JWT_REFRESH_KEY_EXPIRES_TIME_DAYS,
        hours=0,
        minutes=0,
    )
    # время истечения токена
    # log.debug(decoded_str)
    # время истечения полученное из переданной нагрузки
    computed_str = datetime.strftime(now + exp_td, "%d %b %Y %H:%M")
    assert decoded_str == computed_str

    # проверяем время истечения для access
    decoded_payload = jwt.decode(
        jwt=data.get("access_token"),
        audience=config.TOKEN_AUDIENCE,
        key=config.PRIVATE_KEY,
        algorithms=[str(config.JWT_ALGORITHM)],
    )
    # log.debug("-", o=decoded_payload)
    now = datetime.now()
    exp = time.localtime(decoded_payload["exp"])
    decoded_dtm = datetime(
        year=exp.tm_year,
        month=exp.tm_mon,
        day=exp.tm_mday,
        hour=exp.tm_hour,
        minute=exp.tm_min,
        second=exp.tm_sec,
    )
    decoded_str = datetime.strftime(decoded_dtm, "%d %b %Y %H:%M")
    exp_td = timedelta(
        days=0,
        hours=0,
        minutes=config.JWT_ACCESS_KEY_EXPIRES_TIME_MINUTES,
    )
    # время истечения токена
    # log.debug(decoded_str)
    # время истечения полученное из переданной нагрузки
    computed_str = datetime.strftime(now + exp_td, "%d %b %Y %H:%M")
    assert decoded_str == computed_str
    # проверим вхождение группы в нагрузку токена
    assert access_token["groups"][0]["name"] == config.TEST_GROUP


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_token_obtain_by_email(client: AsyncClient, routes: Routs) -> None:
    """Тест запроса токена по email"""
    user = {
        "username": config.FIRST_USER_EMAIL,
        "password": config.FIRST_USER_PASSWORD,
    }
    resp = await client.post(routes.token_obtain, data=user)
    assert resp.status_code == 200
    data = resp.json()
    # log.debug("", o=data)
    # return
    access_token = decode_jwt(data.get("access_token"))
    # log.debug(resp.headers)
    assert access_token.get("sub") == config.TOKEN_SUB
    assert access_token.get("username") == config.FIRST_USER_USERNAME
    assert access_token.get("aud") == config.TOKEN_AUDIENCE


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_token_obtain_by_invalid_cred(client: AsyncClient, routes: Routs) -> None:
    """Тест запроса токена с не валидными кредами"""
    user = {
        "username": config.FIRST_USER_USERNAME,
        "password": "fake pass",
    }
    resp = await client.post(routes.token_obtain, data=user)
    assert resp.status_code == 400
    data = resp.json()
    log.debug("", o=data)

    user = {
        "username": "fake user",
        "password": "fake pass",
    }
    resp = await client.post(routes.token_obtain, data=user)
    assert resp.status_code == 404
    data = resp.json()
    log.debug("", o=data)
