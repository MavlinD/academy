from enum import Enum

from fastapi_users.openapi import OpenAPIResponseType
from starlette import status

from src.auth.users.exceptions import FastAPIUsersException

none_message_response: OpenAPIResponseType = {
    status.HTTP_202_ACCEPTED: {"content": None},
}


class ErrorCodeLocal(str, Enum):
    REFRESH_USER_BAD_TOKEN = "REFRESH_USER_BAD_TOKEN"
    USER_WITH_EMAIL_NOT_EXIST = "USER_WITH_EMAIL_NOT_EXIST"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    GROUP_ALREADY_EXISTS = "GROUP_ALREADY_EXISTS"
    GROUP_NOT_FOUND = "GROUP_NOT_FOUND"


class GroupAlreadyExists(FastAPIUsersException):
    pass
