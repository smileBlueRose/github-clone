from dependency_injector import containers, providers

from infrastructure.di.containers.database import DatabaseContainer
from infrastructure.di.containers.services import ServiceContainer
from infrastructure.di.containers.storages import StorageContainer
from infrastructure.di.containers.use_cases import UseCaseContainer


class Container(containers.DeclarativeContainer):
    database = providers.Container(DatabaseContainer)
    services = providers.Container(ServiceContainer)
    storages = providers.Container(StorageContainer)

    use_cases = providers.Container(
        UseCaseContainer,
        database=database,
        services=services,
        storages=storages,
    )
