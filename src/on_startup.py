from logrich.logger_ import errlog, log  # noqa
from logrich.logger_assets import console  # noqa

from src.auth.config import config


def print_modes() -> None:
    """печатает моды апи"""
    if not config.TESTING:
        log.warning(f"DEBUG: {config.DEBUG}")
        log.warning(f"RELOAD: {config.RELOAD}")
        log.warning(f"TESTING: {config.TESTING}")
