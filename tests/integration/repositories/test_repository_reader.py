import uuid
from dataclasses import asdict, dataclass
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.git import Repository
from domain.exceptions.git import RepositoryNotFoundException
from domain.filters.git import RepositoryFilter
from domain.schemas.repository_storage import RepositoryCreateSchema
from infrastructure.repositories.repository import RepositoryReader, RepositoryWriter
from tests.utils import create_user_model


@pytest.fixture
def reader(session: AsyncSession) -> RepositoryReader:
    return RepositoryReader(session)


class TestRepositoryReader:
    @dataclass
    class TestData:
        __test__ = False

        owner_id: uuid.UUID
        name: str = "test-repo"
        description: str = "description"

        def to_create_schema(self) -> RepositoryCreateSchema:
            return RepositoryCreateSchema(**asdict(self))

    async def _create_repo(self, session: AsyncSession, owner_id: UUID, **kwargs: Any) -> Repository:
        schema = self.TestData(owner_id=owner_id, **kwargs).to_create_schema()
        repository = RepositoryWriter(session=session)
        return await repository.create(schema)

    async def test_get_by_identity_success(self, session: AsyncSession, reader: RepositoryReader) -> None:
        user = await create_user_model(session)
        repository_entity: Repository = await self._create_repo(session=session, owner_id=user.id)
        result = await reader.get_by_identity(identity=repository_entity.id)

        assert result.id == repository_entity.id

    async def test_get_by_identity_not_found(self, reader: RepositoryReader) -> None:
        with pytest.raises(RepositoryNotFoundException):
            await reader.get_by_identity(uuid.uuid4())

    async def test_get_all_repositories(self, session: AsyncSession, reader: RepositoryReader) -> None:
        user = await create_user_model(session, email="owner@test.me", username="owner")
        repo_count = 3
        for i in range(repo_count):
            await self._create_repo(session, owner_id=user.id, name=f"name_{i}")

        result = await reader.get_all(RepositoryFilter())

        assert len(result) == repo_count
