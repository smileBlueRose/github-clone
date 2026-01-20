from dependency_injector import containers, providers

from config import settings
from domain.services.auth.token import TokenService


class ServiceContainer(containers.DeclarativeContainer):
    token_service = providers.Singleton(
        TokenService,
        private_key=settings.auth.jwt.private_key,
        public_key=settings.auth.jwt.public_key,
    )
