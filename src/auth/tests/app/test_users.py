import pytest
from httpx import AsyncClient, Headers
from logrich.logger_ import log  # noqa

from src.auth.conftest import Routs
from src.auth.helpers.tools import check_resp
from src.auth.schemas.token import UserScheme

skip = False
# skip = True
reason = "Temporary off!"

pytestmark = pytest.mark.django_db(transaction=True, reset_sequences=True)


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_list_users(
    client: AsyncClient,
    routes: Routs,
    regular_user: UserScheme,
    superuser_auth_headers: Headers,
) -> None:
    """Тест списка пользователей"""
    resp = await client.get(routes.list_of_users, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("all users", o=data)
    assert len(data) == 2
    params = {
        "is_superuser": "yes",
    }
    resp = await client.get(routes.list_of_users, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("only superusers", o=data)
    assert len(data) == 1
    # return
    params = {
        "email": "loc.LOC",
    }
    resp = await client.get(routes.list_of_users, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug(f"only {params['email']} emails", o=data)
    assert len(data) == 2

    params = {
        "first_name": "Семён",
    }
    resp = await client.get(routes.list_of_users, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug(f"only {params['first_name']} in first_name", o=data)
    return
    assert len(data) == 1

    params = {
        "first_name": "емЁН",
    }
    resp = await client.get(routes.list_of_users, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug(f"only {params['first_name']} in first_name", o=data)
    assert len(data) == 1

    params = {
        "unknown_attr": "нечто",
    }
    resp = await client.get(routes.list_of_users, params=params, headers=superuser_auth_headers)
    data = resp.json()
    log.debug("запрос с несуществующим атрибутом модели пользователя", o=data)
    assert len(data) == 2


# @pytest.mark.skipif(skip, reason=reason)
@pytest.mark.asyncio
async def test_can_not_list_users_for_nonsuper_user(
    client: AsyncClient, routes: Routs, user_active_auth_headers: Headers
) -> None:
    """Тест отказа в списке пользователей обычному пользователю"""
    resp = await client.get(routes.list_of_users, headers=user_active_auth_headers)
    check_resp(resp, 403)
