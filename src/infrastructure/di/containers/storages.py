from dependency_injector import containers, providers

from config import settings
from infrastructure.storage.git_storage import GitPythonStorage


class StorageContainer(containers.DeclarativeContainer):
    git_storage = providers.Singleton(
        GitPythonStorage,
        repositories_dir=settings.git.storage_base_path,
    )
