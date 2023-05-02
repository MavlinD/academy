from datetime import timedelta

from src.auth.config import config
from src.auth.users.ads_manager import AdManager
from src.auth.users.group_manager import GroupManager
from src.auth.users.image_manager import ImageManager
from src.auth.users.security.jwt_actions import JWTStrategy
from src.auth.users.user_manager import UserManager


async def get_user_manager() -> UserManager:
    """user manager object"""
    return UserManager()


async def get_group_manager() -> GroupManager:
    """group manager object"""
    return GroupManager()


async def get_ads_manager() -> AdManager:
    """group manager object"""
    return AdManager()


async def get_image_manager() -> ImageManager:
    """group manager object"""
    return ImageManager()


def get_jwt_strategy() -> JWTStrategy:
    """main JWT strategy"""
    return JWTStrategy(
        token_audience=config.TOKEN_AUDIENCE,
        secret=config.PRIVATE_KEY,
        algorithm=config.JWT_ALGORITHM,
        lifetime=timedelta(minutes=config.JWT_ACCESS_KEY_EXPIRES_TIME_MINUTES),
        public_key=config.PUBLIC_KEY,
    )
