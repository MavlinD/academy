import typing
from datetime import timedelta
from typing import Dict, Optional

from logrich.logger_ import log  # noqa

from src.auth.config import config
from src.auth.schemas.token import TokenModelForGenerate, UserScheme
from src.auth.users.security.jwt_tools import SecretType, generate_jwt


class JWTStrategy:
    token_audience: list[str] | str | None = ["fastapi-users:auth"]

    def __init__(
        self,
        secret: SecretType,
        lifetime: timedelta | None,
        token_audience: list[str] | str | None,
        algorithm: str = config.JWT_ALGORITHM,
        public_key: Optional[SecretType] = None,
    ):
        self.secret = secret
        self.lifetime = lifetime
        self.token_audience = token_audience
        self.algorithm = algorithm
        self.public_key = public_key

    @property
    def encode_key(self) -> SecretType:
        return self.secret

    @property
    def decode_key(self) -> SecretType:
        return self.public_key or self.secret

    @typing.no_type_check
    async def write_token(
        self,
        user: UserScheme,
        token_type: str,
        aud: None | str | list[str] = config.TOKEN_AUDIENCE,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
    ) -> str:
        data = TokenModelForGenerate(
            **{
                "uid": str(user.id),
                "username": str(user.username),
                "email": str(user.email),
                "first_name": str(user.first_name),
                "last_name": str(user.last_name),
                "is_superuser": bool(user.is_superuser),
                "is_active": bool(user.is_active),
                "is_staff": bool(user.is_staff),
                "type": token_type,
                "aud": aud,
                "days": days,
                "hours": hours,
                "minutes": minutes,
            }
        )
        lifetime = timedelta(days=days, hours=hours, minutes=minutes)
        # log.debug("", o=data)
        return generate_jwt(
            data=data.dict(),
            secret=self.encode_key,
            lifetime=lifetime,
            algorithm=self.algorithm,
        )
