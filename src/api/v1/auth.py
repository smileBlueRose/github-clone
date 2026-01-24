from typing import cast

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, Response, jsonify, make_response, request
from pydantic import IPvAnyAddress

from api.exceptions.api import MissingCookiesException
from application.commands.auth import (
    RefreshTokensCommand,
    UserLoginCommand,
    UserRegisterCommand,
)
from application.use_cases.auth.login_user import LoginUserUseCase
from application.use_cases.auth.refresh_tokens import RefreshTokensUseCase
from application.use_cases.auth.register_user import RegisterUserUseCase
from config import settings
from infrastructure.di.container import Container

auth_router = Blueprint("auth", __name__, url_prefix=settings.api.auth.prefix)


@auth_router.route(settings.api.auth.register_prefix, methods=settings.api.auth.register_methods)
@inject
async def register(
    use_case: RegisterUserUseCase = Provide[Container.use_cases.register_user],
) -> tuple[Response, int]:
    data = request.get_json()
    command = UserRegisterCommand(**data)

    user = await use_case.execute(command)

    return (
        jsonify(
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            }
        ),
        201,
    )


@auth_router.route(settings.api.auth.login_prefix, methods=settings.api.auth.login_methods)
@inject
async def login(
    use_case: LoginUserUseCase = Provide[Container.use_cases.login_user],
) -> tuple[Response, int]:
    data = request.get_json()
    command = UserLoginCommand(
        email=data["email"],
        password=data["password"],
        ip_address=cast(IPvAnyAddress | None, request.remote_addr),
        user_agent=request.headers.get("User-Agent", "Unkown"),
    )
    access, refresh = await use_case.execute(command=command)

    response = make_response(jsonify({"access": access.value}))
    response.set_cookie(
        "refresh_token",
        value=refresh.value,
        httponly=settings.auth.cookies.refresh.httponly,
        secure=settings.auth.cookies.refresh.secure,
        samesite=settings.auth.cookies.refresh.samesite,
    )
    return response, 200


@auth_router.route(settings.api.auth.refresh_prefix, methods=settings.api.auth.refresh_methods)
@inject
async def refresh(
    use_case: RefreshTokensUseCase = Provide[Container.use_cases.refresh_tokens],
) -> tuple[Response, int]:
    token: str | None = request.cookies.get("refresh_token")
    if not token:
        raise MissingCookiesException("Refresh token not found in cookies")

    command = RefreshTokensCommand(
        refresh_token=token,
        ip_address=cast(IPvAnyAddress | None, request.remote_addr),
        user_agent=request.headers.get("User-Agent", "Unkown"),
    )
    access, refresh = await use_case.execute(command)

    response = make_response(jsonify({"access": access.value}))
    response.set_cookie(
        "refresh_token",
        value=refresh.value,
        httponly=settings.auth.cookies.refresh.httponly,
        secure=settings.auth.cookies.refresh.secure,
        samesite=settings.auth.cookies.refresh.samesite,
    )
    return response, 200
