import asyncio
import os
import typing
from typing import AsyncGenerator, Generator

import pytest
from _pytest.config import ExitCode
from _pytest.main import Session
from _pytest.nodes import Item
from asgi_lifespan import LifespanManager
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from fastapi import FastAPI, HTTPException
from httpx import URL, AsyncClient, Headers
from logrich.logger_ import log  # noqa
from logrich.logger_assets import console
from pydantic import EmailStr

from src.auth.assets import get_test_status_badge
from src.auth.config import config
from src.auth.helpers.tools import print_endpoints, print_request
from src.auth.schemas.token import GroupScheme
from src.auth.tests.app.test_tools import create_first_user, create_user
from src.main import run_app

# os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "True")


@pytest.hookimpl(tryfirst=True)
def pytest_configure() -> None:
    """предотвратить поломку основной БД"""
    if not config.TESTING:
        log.warning("Переведите приложение в режим тестирования:\n" "установите переменную TESTING=True")
        pytest.exit("Условие запуска тестов")


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: Session, exitstatus: int | ExitCode) -> None:
    """получит бейдж для статуса тестов"""
    print()
    if config.LOCAL:
        asyncio.run(get_test_status_badge(status=exitstatus))


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir: str) -> Generator:
    """Fixture to execute asserts before and after a test is run"""
    print()
    yield


@pytest.fixture
async def app() -> AsyncGenerator[FastAPI, None]:
    """create app for test"""
    await create_first_user()

    yield run_app()


def pytest_sessionstart(session: Session) -> None:  # noqa
    """пусть будет"""
    pass


def pytest_runtest_call(item: Item) -> None:
    """печатает заголовок теста"""
    console.rule(f"[green]{item.parent.name}[/]::[yellow bold]{item.name}[/]")  # type: ignore


@pytest.fixture(scope="function", autouse=True)
def django_db_cleanup() -> None:
    """
    https://pytest-django.readthedocs.io/en/latest/database.html#reuse-db-reuse-the-testing-database-between-test-runs
    https://books.agiliq.com/projects/django-orm-cookbook/en/latest/truncate.html
    """
    try:
        user_model = get_user_model()
        user_model.objects.all().delete()
        Group.objects.all().delete()
    except Exception as err:
        log.debug(err)


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, object]:
    """Async server client that handles lifespan and teardown"""
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://test",
            event_hooks={
                "request": [print_request],
            },
        ) as client_:
            try:
                yield client_
            except Exception as exc:
                log.error(exc)
            finally:
                pass


@typing.no_type_check
@pytest.fixture
async def regular_user(app: FastAPI) -> User | HTTPException:
    """добавляет рядового неактивированного пользователя в БД"""

    user = await create_user(
        email=config.TEST_USER_EMAIL,
        username=config.TEST_USER_USERNAME,
        password=config.TEST_USER_PASSWORD,
        first_name=config.TEST_USER_FIRST_NAME,
        is_superuser=False,
        is_staff=False,
        is_active=False,
    )
    return user


@pytest.fixture
async def create_group_fixture(app: FastAPI) -> GroupScheme:
    """добавляет группу"""
    group = await sync_to_async(Group.objects.create)(
        name=config.TEST_GROUP,
    )
    return group


@pytest.fixture
async def regular_user_active(app: FastAPI) -> User | HTTPException:
    """Добавляет рядового активированного пользователя в БД"""
    user = await create_user(
        email=EmailStr(config.TEST_USER_EMAIL),
        username=str(config.TEST_USER_USERNAME),
        password=str(config.TEST_USER_PASSWORD),
        first_name=str(config.TEST_USER_FIRST_NAME),
        is_superuser=False,
        is_active=True,
    )
    return user


class Routs:
    """like path reverse"""

    def __init__(self, app: FastAPI) -> None:
        # JWT
        self.app = app
        self.token_obtain = app.url_path_for("token_obtain")
        self.token_refresh = app.url_path_for("token_refresh")
        self.token_verify = app.url_path_for("token_verify")

        # Users
        self.list_of_users = app.url_path_for("list_of_users")
        self.list_of_users_get = app.url_path_for("list_of_users_get")
        self.list_of_users_post = app.url_path_for("list_of_users_post")

        self.register = app.url_path_for("register")

        self.reset_password = app.url_path_for("reset_password")

        self.read_me = app.url_path_for("read_me")
        self.update_me = app.url_path_for("update_me")

        self.create_user = app.url_path_for("create_user")
        self.create_group = app.url_path_for("create_group")
        self.read_groups = app.url_path_for("read_groups")

        self.stress_test = app.url_path_for("stress_test")

        self.read_home = app.url_path_for("read_home")

        self.read_pub_key = app.url_path_for("read_pub_key")

        self.request_to_update_group = app.url_path_for("rename_group")

    def accept_verify_token(self, token: str) -> URL | str:
        return self.app.url_path_for("accept_verify_token", token=token)

    def request_to_wiki_structure(self, article: str) -> URL | str:
        return self.app.url_path_for("read_wiki_structure", article=article)

    def request_to_reset_password(self, email: EmailStr | str) -> URL | str:
        return self.app.url_path_for("request_to_reset_password", email=email)

    def request_to_verify_email(self, email: EmailStr | str) -> URL | str:
        return self.app.url_path_for("request_to_verify_email", email=email)

    def request_read_user(self, user_attr: str | int) -> URL | str:
        return self.app.url_path_for("read_user", user_attr=str(user_attr))

    def request_move_in_out_group(self, action: str) -> URL | str:
        return self.app.url_path_for("move_in_out_group", action=action)

    def request_read_group(self, group_attr: str) -> URL | str:
        return self.app.url_path_for("read_group", group_attr=group_attr)

    def request_delete_group(self, group_attr: str) -> URL | str:
        return self.app.url_path_for("delete_group", group_attr=group_attr)

    def request_to_update_user(self, user_attr: str | int) -> URL | str:
        return self.app.url_path_for("update_user", user_attr=str(user_attr))

    def request_to_delete_user(self, user_attr: str | int) -> URL | str:
        return self.app.url_path_for("delete_user", user_attr=str(user_attr))

    def print(self) -> None:
        print_endpoints(self.app)


@pytest.fixture
def routes(app: FastAPI) -> Routs:
    """
    https://stackoverflow.com/questions/63682956/fastapi-retrieve-url-from-view-name-route-name
    """
    return Routs(app)


@pytest.fixture
async def superuser_auth_headers(client: AsyncClient, routes: Routs) -> Headers:
    """Returns the authorization headers for first user (superuser)"""
    user = {
        "username": config.FIRST_USER_USERNAME,
        "password": config.FIRST_USER_PASSWORD,
    }
    # запросим администраторский токен
    resp = await client.post(routes.token_obtain, data=user)
    data = resp.json()
    root_access_token = data.get("access_token", "")
    return Headers({"AUTHORIZATION": "Bearer " + root_access_token})


@typing.no_type_check
async def user_auth_header(client: AsyncClient, routes: Routs, is_active: bool = True) -> Headers:
    """get Header for auth"""
    # сначала создаём пол-ля
    await create_user(
        email=config.TEST_USER_EMAIL,
        username=config.TEST_USER_USERNAME,
        password=config.TEST_USER_PASSWORD,
        first_name=config.TEST_USER_FIRST_NAME,
        is_active=is_active,
    )
    user = {
        "username": config.TEST_USER_USERNAME,
        "password": config.TEST_USER_PASSWORD,
    }
    # запросим пользовательский токен
    resp = await client.post(routes.token_obtain, data=user)
    data = resp.json()
    access_token = data.get("access_token")
    if access_token:
        return Headers({"AUTHORIZATION": "Bearer " + access_token})
    return Headers()


@pytest.fixture
async def user_active_auth_headers(client: AsyncClient, routes: Routs) -> Headers:
    """Заголовок активного пользователя"""
    # этот пользователь и ниже могут не создаваться вместе, если username or email совпадают
    header = await user_auth_header(client, routes)
    return header


@pytest.fixture
async def user_unactive_auth_headers(client: AsyncClient, routes: Routs) -> Headers:
    """Заголовок НЕактивного пользователя"""
    header = await user_auth_header(client, routes, is_active=False)
    return header
