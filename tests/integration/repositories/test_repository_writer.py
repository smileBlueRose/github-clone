import uuid
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.git import Repository
from domain.exceptions.git import RepositoryNotFoundException
from domain.schemas.repository_storage import RepositoryCreateSchema, RepositoryUpdateSchema
from infrastructure.repositories.repository import RepositoryReader, RepositoryWriter
from tests.utils import create_user_model
from dataclasses import asdict


@pytest.fixture
def writer(session: AsyncSession) -> RepositoryWriter:
    return RepositoryWriter(session)


class TestRepositoryWriter:
    @dataclass
    class TestData:
        __test__ = False

        owner_id: uuid.UUID
        name: str = "test-repo"
        description: str = "description"

        def to_create_schema(self) -> RepositoryCreateSchema:
            return RepositoryCreateSchema(**asdict(self))

        def to_update_schema(self) -> RepositoryUpdateSchema:
            return RepositoryUpdateSchema(**asdict(self))

    async def test_create_success(self, session: AsyncSession, writer: RepositoryWriter) -> None:
        user = await create_user_model(session)
        schema = self.TestData(owner_id=user.id).to_create_schema()

        result = await writer.create(schema)

        assert result.name == schema.name
        assert result.owner_id == schema.owner_id
        assert result.description == schema.description
        assert result.id is not None

    async def test_update_success(self, session: AsyncSession, writer: RepositoryWriter) -> None:
        user = await create_user_model(session)
        repository_entity = await writer.create(self.TestData(owner_id=user.id).to_create_schema())

        update_schema = self.TestData(
            owner_id=user.id, name="updated-name", description="updated description"
        ).to_update_schema()
        result = await writer.update(identity=repository_entity.id, schema=update_schema)

        assert result.id == repository_entity.id
        assert result.name == update_schema.name
        assert result.description == update_schema.description

    async def test_update_not_found(self, writer: RepositoryWriter) -> None:
        update_schema = self.TestData(owner_id=uuid.uuid4(), name="new-name").to_update_schema()

        with pytest.raises(RepositoryNotFoundException):
            await writer.update(identity=uuid.uuid4(), schema=update_schema)

    async def test_delete_by_identity_success(self, session: AsyncSession, writer: RepositoryWriter) -> None:
        user = await create_user_model(session)
        repository_entity = await writer.create(self.TestData(owner_id=user.id).to_create_schema())

        assert await writer.delete_by_identity(repository_entity.id) is True
        assert await writer.delete_by_identity(repository_entity.id) is False
