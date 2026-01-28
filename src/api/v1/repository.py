from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, Response, g, jsonify, request

from api.utils.require_field import get_required_field
from application.commands.git import (
    CreateBranchCommand,
    CreateInitialCommitCommand,
    CreateRepositoryCommand,
    DeleteRepositoryCommand,
    GetBranchesCommand,
    GetRepositoryCommand,
    UpdateFileCommand,
)
from application.use_cases.git.branches.create_branch import CreateBranchUseCase
from application.use_cases.git.branches.get_branches import GetBranchesUseCase
from application.use_cases.git.commits.create_initial_commit import CreateInitialCommitUseCase
from application.use_cases.git.commits.update_file import UpdateFileUseCase
from application.use_cases.git.create_repository import CreateRepositoryUseCase
from application.use_cases.git.delete_repository import DeleteRepositoryUseCase
from application.use_cases.git.get_repository import GetRepositoryUseCase
from config import settings
from domain.value_objects.common import Pagination
from infrastructure.di.container import Container
from infrastructure.middleware.auth import require_auth
from infrastructure.utils.security import get_sanitized_data, sanitize_html_input

repositories_router = Blueprint("repositories", __name__, url_prefix=settings.api.repositories.prefix)


@repositories_router.route("", methods=["POST"])
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


@repositories_router.route("/<username>/<repository_name>", methods=["DELETE"])
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


@repositories_router.route("", methods=["GET"])
@repositories_router.route("/<username>", methods=["GET"])
@repositories_router.route("/<username>/<repository_name>", methods=["GET"])
@inject
async def get_repositories(
    username: str | None = None,
    repository_name: str | None = None,
    use_case: GetRepositoryUseCase = Provide[Container.use_cases.get_repositories],
) -> tuple[Response, int]:
    query, _ = get_sanitized_data(request)

    command = GetRepositoryCommand(
        username=sanitize_html_input(username) if username else None,
        repository_name=sanitize_html_input(repository_name) if repository_name else None,
        pagination=Pagination(**{k: int(query[k]) for k in query if k in ["limit", "offset"]}),
    )
    result = await use_case.execute(command)
    return jsonify([i.model_dump() for i in result]), 200


@repositories_router.route("/<username>/<repository_name>/branches", methods=["GET"])
@inject
async def get_branches(
    username: str,
    repository_name: str,
    use_case: GetBranchesUseCase = Provide[Container.use_cases.get_branches],
) -> tuple[Response, int]:
    command = GetBranchesCommand(username=username, repository_name=repository_name)
    branches = await use_case.execute(command)

    return jsonify([i.model_dump() for i in branches]), 200


@repositories_router.route("/<username>/<repository_name>/branches", methods=["POST"])
@require_auth()
@inject
async def create_branch(
    username: str,
    repository_name: str,
    use_case: CreateBranchUseCase = Provide[Container.use_cases.create_branch],
) -> tuple[Response, int]:
    _, data = get_sanitized_data(request)

    command = CreateBranchCommand(
        initiator_id=g.access_payload.sub,
        owner_username=username,
        repository_name=repository_name,
        branch_name=get_required_field(data, "branch_name"),
        from_branch=get_required_field(data, "from_branch"),
    )
    await use_case.execute(command)

    return Response(), HTTPStatus.CREATED


@repositories_router.route("/<username>/<repository_name>/contents/<branch_name>/<path:file_path>", methods=["POST"])
@require_auth()
@inject
async def update_file(
    username: str,
    repository_name: str,
    branch_name: str,
    file_path: str,
    use_case: UpdateFileUseCase = Provide[Container.use_cases.update_file],
) -> tuple[Response, int]:

    command = UpdateFileCommand(
        user_id=g.access_payload.sub,
        username=username,
        repo_name=repository_name,
        branch_name=branch_name,
        file_path=file_path,
        data=request.files["file"].read(),
        message=request.form["message"],
    )
    # TODO: Sanitize message
    commit = await use_case.execute(command)

    return jsonify(commit.model_dump()), 200


@repositories_router.route("/<username>/<repository_name>/initial-commit", methods=["POST"])
@require_auth()
@inject
async def create_initial_commit(
    username: str,
    repository_name: str,
    use_case: CreateInitialCommitUseCase = Provide[Container.use_cases.create_initial_commit],
) -> tuple[Response, int]:
    _, data = get_sanitized_data(request)

    command = CreateInitialCommitCommand(
        initiator_id=g.access_payload.sub,
        owner_username=username,
        repository_name=repository_name,
        branch_name=get_required_field(data, "branch_name"),
    )
    commit = await use_case.execute(command)

    return jsonify(commit.model_dump()), 200
