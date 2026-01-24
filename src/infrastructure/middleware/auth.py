from functools import wraps
from typing import Any, Callable

from dependency_injector.wiring import Provide, inject
from flask import g, jsonify, request
from flask.typing import ResponseReturnValue

from domain.services.auth.token import TokenService
from domain.value_objects.token import AccessTokenVo
from infrastructure.di.container import Container


@inject
def require_auth(
    token_service: TokenService = Provide[Container.services.token_service],
) -> Callable[[Callable[..., ResponseReturnValue]], Callable[..., ResponseReturnValue]]:

    def decorator(
        func: Callable[..., ResponseReturnValue],
    ) -> Callable[..., ResponseReturnValue]:

        @wraps(func)
        def decorated(*args: Any, **kwargs: Any) -> ResponseReturnValue:
            g.access_payload = None
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Unauthorized"}), 401

            access_token = auth_header.split(" ")[1]
            payload = token_service.verify_access(AccessTokenVo(value=access_token))
            g.access_payload = payload
            return func(*args, **kwargs)

        return decorated

    return decorator
