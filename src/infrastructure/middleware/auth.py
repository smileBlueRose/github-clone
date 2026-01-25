from functools import wraps
from typing import Any, Awaitable, Callable

from flask import Response, g, jsonify, request
from loguru import logger

from config import settings
from domain.services.auth.token import TokenService
from domain.value_objects.token import AccessTokenVo


def require_auth() -> (
    Callable[[Callable[..., Awaitable[tuple[Response, int]]]], Callable[..., Awaitable[tuple[Response, int]]]]
):
    token_service = TokenService(private_key=settings.auth.jwt.private_key, public_key=settings.auth.jwt.public_key)

    def decorator(
        func: Callable[..., Awaitable[tuple[Response, int]]],
    ) -> Callable[..., Awaitable[tuple[Response, int]]]:

        @wraps(func)
        async def decorated(*args: Any, **kwargs: Any) -> tuple[Response, int]:
            g.access_payload = None
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Unauthorized"}), 401

            access_token = auth_header.split(" ")[1]
            payload = token_service.verify_access(AccessTokenVo(value=access_token))
            logger.bind(user_id=payload.sub)

            g.access_payload = payload

            return await func(*args, **kwargs)

        return decorated

    return decorator
