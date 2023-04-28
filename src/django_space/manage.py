#!/usr/bin/env python

import os
import sys

from config import config
from django.conf import settings
from logrich.logger_ import log  # noqa

from src.auth.config import config as auth_config
from src.common.tools import create_dbs


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_space.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    second_arg = sys.argv[1]
    if second_arg == "migrate":
        default_db = settings.DATABASES.get("default", dict()).get("ENGINE", "").split(".")[-1]
        if default_db == "postgresql":
            if auth_config.TESTING:
                dbs = config.POSTGRES_DB + "-test"
            else:
                dbs = config.POSTGRES_DB
            db_uri = (
                f"{default_db}://{config.POSTGRES_USER.get_secret_value()}:"
                f"{config.POSTGRES_PASSWORD.get_secret_value()}"
                f"@{config.POSTGRES_HOSTNAME}:{config.POSTGRES_PORT}/{dbs}"
            )
            # создадим БД, если она не существует
            create_dbs(db_uri=db_uri)
    # log.debug(sys.argv)
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
