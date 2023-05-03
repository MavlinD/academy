from enum import Enum

from fastapi_users.openapi import OpenAPIResponseType
from starlette import status

none_message_response: OpenAPIResponseType = {
    status.HTTP_202_ACCEPTED: {"content": None},
}


class ErrorCodeLocal(str, Enum):
    REFRESH_USER_BAD_TOKEN = "REFRESH_USER_BAD_TOKEN"
    USER_WITH_EMAIL_NOT_EXIST = "USER_WITH_EMAIL_NOT_EXIST"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    OVER_LIMIT_IMAGE_COUNT = "Достигнут лимит кол-ва прикреплённых изображений."
