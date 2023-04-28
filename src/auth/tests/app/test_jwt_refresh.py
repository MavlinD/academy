import time
from datetime import datetime, timedelta

import jwt
import pytest
from httpx import AsyncClient
from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.conftest import Routs

skip = False
# skip = True
reason = "Temporary off!!"


pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


@pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, routes: Routs) -> None:
    """Тест запроса на обновление пары токенов"""
    # сначала проверяем время истечения для рефреш
    user = {
        "username": config.FIRST_USER_EMAIL,
        "password": config.FIRST_USER_PASSWORD,
    }
    resp = await client.post(routes.token_obtain, data=user)
    data = resp.json()
    # log.debug("", o=data)
    payload = {"token": data.get("refresh_token")}
    resp = await client.post(routes.token_refresh, json=payload)
    data = resp.json()
    # log.debug("", o=data)
    # return
    decoded_payload = jwt.decode(
        jwt=data.get("refresh_token"),
        audience=config.TOKEN_AUDIENCE,
        key=config.PRIVATE_KEY,
        algorithms=[str(config.JWT_ALGORITHM)],
    )
    # log.debug("", o=decoded_payload)
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
    # log.debug(decoded_dtm.day)
    # log.debug(decoded_dtm.year)
    decoded_str = datetime.strftime(decoded_dtm, "%d %b %Y %H:%M")
    # return
    exp_td = timedelta(
        days=config.JWT_REFRESH_KEY_EXPIRES_TIME_DAYS,
        hours=0,
        minutes=0,
    )
    # время истечения токена
    # log.debug(decoded_str)
    # время истечения полученное из переданной нагрузки
    computed_str = datetime.strftime(now + exp_td, "%d %b %Y %H:%M")
    # log.debug(computed_str)
    assert decoded_str == computed_str
    assert resp.status_code == 200

    # проверяем время истечения для access
    decoded_payload = jwt.decode(
        jwt=data.get("access_token"),
        audience=config.TOKEN_AUDIENCE,
        key=config.PRIVATE_KEY,
        algorithms=[str(config.JWT_ALGORITHM)],
    )
    # log.debug("", o=decoded_payload)
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
    log.debug(decoded_str)
    # время истечения полученное из переданной нагрузки
    computed_str = datetime.strftime(now + exp_td, "%d %b %Y %H:%M")
    assert decoded_str == computed_str
    log.debug(resp.headers)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_refresh_fake_token(client: AsyncClient, routes: Routs) -> None:
    """Тест запроса на обновление пары токенов с некорректной нагрузкой"""
    payload = {"token": "fake-token"}
    resp = await client.post(routes.token_refresh, json=payload)
    log.debug(resp)
    log.debug(resp.text)
    log.debug(resp.headers)
    assert resp.headers.get("access-control-allow-credentials")
    assert resp.headers.get("access-control-allow-origin", "*")
    assert resp.status_code == 422
