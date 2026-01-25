from uuid import UUID

from domain.ports.filter import BaseFilter


class RepositoryFilter(BaseFilter):
    user_id: UUID | None = None
    repository_name: str | None = None
