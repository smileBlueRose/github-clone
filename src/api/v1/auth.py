from dependency_injector.wiring import Provide, inject
from flask import Blueprint, Response, jsonify, request

from application.commands.auth import UserRegisterCommand
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
