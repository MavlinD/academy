from datetime import datetime, timedelta
from typing import Any, Dict, List, Union

import jwt
from jwt import DecodeError
from logrich.logger_ import errlog, log  # noqa
from pydantic import BaseModel, SecretStr

from src.auth.config import config
from src.auth.schemas.token import AccessTokenModelForWrite, RefreshTokenModelForWrite
from src.auth.users.exceptions import InvalidVerifyToken

SecretType = Union[str, SecretStr]


def get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def generate_jwt(
    data: Dict[str, object],
    lifetime: timedelta,
    secret: SecretType = config.PRIVATE_KEY,
    algorithm: str = config.JWT_ALGORITHM,
) -> str:
    if not lifetime:
        lifetime = timedelta(minutes=config.JWT_ACCESS_KEY_EXPIRES_TIME_MINUTES)

    data["exp"] = datetime.utcnow() + lifetime
    payload = BaseModel()
    if data["type"] == "access":
        payload = AccessTokenModelForWrite(**data)
    if data["type"] == "refresh":
        payload = RefreshTokenModelForWrite(**data)
    return jwt.encode(
        payload=payload.dict(exclude_none=True),
        key=get_secret_value(secret),
        algorithm=algorithm,
    )


def decode_jwt(
    encoded_jwt: str,
    secret: SecretType = config.PRIVATE_KEY,
    audience: List[str] | str | None = config.TOKEN_AUDIENCE,
    algorithms: list[str] = None,
) -> Dict[str, Any]:
    if algorithms is None:
        algorithms = [config.JWT_ALGORITHM]
    try:
        token = jwt.decode(
            encoded_jwt,
            get_secret_value(secret),
            audience=audience,
            algorithms=algorithms,
        )
        return token
    except (DecodeError, Exception) as err:
        raise InvalidVerifyToken(msg=err)
