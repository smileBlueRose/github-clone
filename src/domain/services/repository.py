from uuid import UUID

from domain.exceptions.git import RepositoryAlreadyExistsException
from domain.filters.git import RepositoryFilter
from domain.ports.repositories.git_repo import AbstractRepositoryReader
from domain.ports.service import BaseService


class RepositoryService(BaseService):
    def __init__(self, reader: AbstractRepositoryReader) -> None:
        self._reader = reader

    async def check_repository_name(self, user_id: UUID, repository_name: str) -> None:
        """:raises RepositoryAlreadyExistsException:"""

        result = await self._reader.get_all(filter_=RepositoryFilter(user_id=user_id, repository_name=repository_name))
        if result:
            raise RepositoryAlreadyExistsException(repository_name=repository_name)

    def get_repository_path(self, user_id: UUID, repository_id: UUID) -> str:
        return f"user_{user_id}/repository_{repository_id}"
