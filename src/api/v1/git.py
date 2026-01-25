from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, Response, g, jsonify, request

from application.commands.git import CreateRepositoryCommand, DeleteRepositoryCommand
from application.use_cases.git.create_repository import CreateRepositoryUseCase
from application.use_cases.git.delete_repository import DeleteRepositoryUseCase
from config import settings
from infrastructure.di.container import Container
from infrastructure.middleware.auth import require_auth
from infrastructure.utils.security import get_sanitized_data

git_router = Blueprint("git", __name__, url_prefix=settings.api.git.prefix)


@git_router.route(settings.api.git.create_prefix, methods=settings.api.git.create_methods)
@require_auth()
@inject
async def create_repository(
    use_case: CreateRepositoryUseCase = Provide[Container.use_cases.create_repository],
) -> tuple[Response, int]:
    _, data = get_sanitized_data(request)
    payload = g.access_payload

    command = CreateRepositoryCommand(
        repository_name=data["repository_name"],
        user_id=payload.sub,
        description=data["description"],
    )
    repository = await use_case.execute(command)
    return jsonify({"repository_id": repository.id}), HTTPStatus.CREATED


@git_router.route("/<username>/<repository_name>", methods=settings.api.git.delete_methods)
@require_auth()
@inject
async def delete_repository(
    username: str,
    repository_name: str,
    use_case: DeleteRepositoryUseCase = Provide[Container.use_cases.delete_repository],
) -> tuple[Response, int]:
    payload = g.access_payload
    command = DeleteRepositoryCommand(username=username, user_id=payload.sub, repository_name=repository_name)

    await use_case.execute(command)

    return Response(), HTTPStatus.NO_CONTENT
