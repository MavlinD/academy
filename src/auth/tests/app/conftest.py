from faker import Faker
from logrich.logger_ import log  # noqa

from src.auth.tests.app.test_tools import create_user


async def insert_fake_data_to_db(amount_users: int) -> None:
    """fill db with fake data"""
    fake = Faker("ru_RU")
    for i in range(amount_users):
        username = str(f"{i}-") + fake.simple_profile().get("username")
        password = fake.password(length=7, special_chars=False) + "%"
        email = fake.unique.email()
        # log.debug(f"{username}: {email}")
        await create_user(username=username, password=password, email=email)
