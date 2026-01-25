from dependency_injector import containers, providers

from application.use_cases.auth.login_user import LoginUserUseCase
from application.use_cases.auth.refresh_tokens import RefreshTokensUseCase
from application.use_cases.auth.register_user import RegisterUserUseCase
from application.use_cases.git.create_repository import CreateRepositoryUseCase
from application.use_cases.git.delete_repository import DeleteRepositoryUseCase
from application.use_cases.git.get_repository import GetRepositoryUseCase


class UseCaseContainer(containers.DeclarativeContainer):
    database = providers.DependenciesContainer()
    services = providers.DependenciesContainer()
    storages = providers.DependenciesContainer()

    register_user = providers.Factory(
        RegisterUserUseCase,
        uow=database.uow,
    )
    login_user = providers.Factory(
        LoginUserUseCase,
        uow=database.uow,
        token_service=services.token_service,
    )
    refresh_tokens = providers.Factory(
        RefreshTokensUseCase,
        uow=database.uow,
        token_service=services.token_service,
    )
    create_repository = providers.Factory(
        CreateRepositoryUseCase,
        uow=database.uow,
        git_storage=storages.git_storage,
    )
    delete_repository = providers.Factory(
        DeleteRepositoryUseCase,
        uow=database.uow,
        git_storage=storages.git_storage,
        policy_service=services.policy_service,
    )
    get_repositories = providers.Factory(
        GetRepositoryUseCase,
        uow=database.uow,
    )
