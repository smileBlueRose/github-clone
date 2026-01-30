from domain.ports.session import AsyncSessionP
from domain.services.repository import RepositoryService
from infrastructure.factories.repositories import create_repository_reader


def create_repository_service(session: AsyncSessionP) -> RepositoryService:
    return RepositoryService(reader=create_repository_reader(session=session))
