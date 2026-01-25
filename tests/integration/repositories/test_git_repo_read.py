import uuid
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.git import Repository
from domain.exceptions.git import GitRepositoryNotFoundException
from domain.filters.git import GitRepoFilter
from domain.schemas.repository_storage import GitRepoCreateSchema
from infrastructure.repositories.git_repo import GitRepoReadRepository, GitRepoWriteRepository
from tests.utils import create_user_model


@pytest.fixture
def read_repository(session: AsyncSession) -> GitRepoReadRepository:
    return GitRepoReadRepository(session)


class TestGitRepoReadRepository:
    @dataclass
    class TestData:
        __test__ = False

        owner_id: uuid.UUID
        name: str = "test-repo"
        description: str = "description"

        def to_create_schema(self, **kwargs: Any) -> GitRepoCreateSchema:
            data = dict(
                name=self.name,
                owner_id=self.owner_id,
                description=self.description,
            )
            data.update(**kwargs)

            return GitRepoCreateSchema(**data)  # type: ignore

    async def _create_repo(self, session: AsyncSession, owner_id: UUID, **kwargs: Any) -> Repository:
        schema = self.TestData(owner_id=owner_id, **kwargs).to_create_schema()
        repository = GitRepoWriteRepository(session=session)
        return await repository.create(schema)

    async def test_get_by_identity_success(self, session: AsyncSession, read_repository: GitRepoReadRepository) -> None:
        user = await create_user_model(session)
        repository_entity: Repository = await self._create_repo(session=session, owner_id=user.id)
        result = await read_repository.get_by_identity(identity=repository_entity.id)

        assert result.id == repository_entity.id

    async def test_get_by_identity_not_found(self, read_repository: GitRepoReadRepository) -> None:
        with pytest.raises(GitRepositoryNotFoundException):
            await read_repository.get_by_identity(uuid.uuid4())

    async def test_get_all_repositories(self, session: AsyncSession, read_repository: GitRepoReadRepository) -> None:
        user = await create_user_model(session, email="owner@test.me", username="owner")
        repo_count = 3
        for i in range(repo_count):
            await self._create_repo(session, owner_id=user.id, name=f"name_{i}")

        result = await read_repository.get_all(GitRepoFilter())

        assert len(result) == repo_count
