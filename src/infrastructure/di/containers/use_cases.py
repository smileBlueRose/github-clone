from dependency_injector import containers, providers

from application.use_cases.login_user import LoginUserUseCase
from application.use_cases.register_user import RegisterUserUseCase


class UseCaseContainer(containers.DeclarativeContainer):
    database = providers.DependenciesContainer()
    services = providers.DependenciesContainer()

    register_user = providers.Factory(
        RegisterUserUseCase,
        uow=database.uow,
    )
    login_user = providers.Factory(
        LoginUserUseCase,
        uow=database.uow,
        token_service=services.token_service,
    )
