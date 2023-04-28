from starlette import status

responses: dict[int | str, dict[str, str]] | None = {
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Missing token or inactive user.",
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "Not a superuser.",
    },
}
