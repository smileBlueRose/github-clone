from dependency_injector import containers, providers

from application.use_cases.register_user import RegisterUserUseCase


class UseCaseContainer(containers.DeclarativeContainer):
    database = providers.DependenciesContainer()

    register_user = providers.Factory(
        RegisterUserUseCase,
        uow=database.uow,
    )
