from dependency_injector import containers, providers

from config import settings
from config.config import BASE_DIR
from domain.services.auth.token import TokenService
from infrastructure.policy_loader import PolicyLoader


class ServiceContainer(containers.DeclarativeContainer):
    token_service = providers.Singleton(
        TokenService,
        private_key=settings.auth.jwt.private_key,
        public_key=settings.auth.jwt.public_key,
    )
    policy_service = providers.Singleton(PolicyLoader.load_from_yaml, file_path=BASE_DIR / settings.policies_file_path)
