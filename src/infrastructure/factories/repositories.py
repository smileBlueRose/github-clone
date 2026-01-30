from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.session import AsyncSessionP
from infrastructure.repositories.repository import RepositoryReader, RepositoryWriter
from infrastructure.repositories.user import UserReadRepository


def create_repository_reader(session: AsyncSessionP) -> RepositoryReader:
    return RepositoryReader(cast(AsyncSession, session))


def create_repository_writer(session: AsyncSessionP) -> RepositoryWriter:
    return RepositoryWriter(cast(AsyncSession, session))


def create_user_reader(session: AsyncSessionP) -> UserReadRepository:
    return UserReadRepository(cast(AsyncSession, session))
