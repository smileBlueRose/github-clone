from dependency_injector import containers, providers

from infrastructure.di.containers.database import DatabaseContainer
from infrastructure.di.containers.use_cases import UseCaseContainer


class Container(containers.DeclarativeContainer):
    database = providers.Container(DatabaseContainer)

    use_cases = providers.Container(
        UseCaseContainer,
        database=database,
    )
