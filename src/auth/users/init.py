from datetime import timedelta

from fastapi_users.authentication import AuthenticationBackend, BearerTransport

from src.auth.config import config
from src.auth.users.group_manager import GroupManager
from src.auth.users.security.jwt_actions import JWTStrategy
from src.auth.users.user_manager import UserManager


async def get_user_manager() -> UserManager:
    """user manager object"""
    return UserManager()


async def get_group_manager() -> GroupManager:
    """group manager object"""
    return GroupManager()


bearer_transport: BearerTransport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """main JWT strategy"""
    return JWTStrategy(
        token_audience=config.TOKEN_AUDIENCE,
        secret=config.PRIVATE_KEY,
        algorithm=config.JWT_ALGORITHM,
        lifetime=timedelta(minutes=config.JWT_ACCESS_KEY_EXPIRES_TIME_MINUTES),
        public_key=config.PUBLIC_KEY,
    )


def get_jwt_strategy_to_verify_user() -> JWTStrategy:
    """JWT instance for verify email"""
    return JWTStrategy(
        token_audience="fastapi-users:verify",
        secret=config.PRIVATE_KEY,
        algorithm=config.JWT_ALGORITHM,
        lifetime=timedelta(seconds=config.VERIFICATION_TOKEN_LIFETIME_SECONDS),
        public_key=config.PUBLIC_KEY,
    )


auth_backend: AuthenticationBackend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,  # type: ignore
)
