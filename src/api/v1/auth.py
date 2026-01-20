from typing import cast

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, Response, jsonify, request
from pydantic import IPvAnyAddress

from application.commands.auth import UserLoginCommand, UserRegisterCommand
from application.use_cases.login_user import LoginUserUseCase
from application.use_cases.register_user import RegisterUserUseCase
from config import settings
from infrastructure.di.container import Container

auth_router = Blueprint("auth", __name__, url_prefix=settings.api.auth.prefix)


@auth_router.route(settings.api.auth.register_prefix, methods=settings.api.auth.register_methods)
@inject
async def register(use_case: RegisterUserUseCase = Provide[Container.use_cases.register_user]) -> tuple[Response, int]:
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
async def login(use_case: LoginUserUseCase = Provide[Container.use_cases.login_user]) -> tuple[Response, int]:
    data = request.get_json()
    command = UserLoginCommand(
        email=data["email"],
        password=data["password"],
        ip_address=cast(IPvAnyAddress | None, request.remote_addr),
        user_agent=request.headers.get("User-Agent", "Unkown"),
    )
    access, refresh = await use_case.execute(command=command)

    return (
        jsonify(
            {
                "access": access.value,
                "refresh": refresh.value,
            }
        ),
        200,
    )
