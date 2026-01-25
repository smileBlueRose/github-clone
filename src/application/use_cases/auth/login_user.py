from datetime import datetime

from loguru import logger

from application.commands.auth import UserLoginCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from config import settings
from domain.schemas.refresh_token import RefreshTokenCreateSchema
from domain.services.auth.authentication import AuthenticationService
from domain.services.auth.token import TokenService
from domain.value_objects.auth import LoginCredentials
from domain.value_objects.token import AccessTokenVo, RefreshTokenVo
from infrastructure.repositories.refresh_token import RefreshTokenWriteRepository
from infrastructure.repositories.user import UserReadRepository


class LoginUserUseCase(AbstractUseCase[UserLoginCommand]):
    def __init__(self, uow: AbstractUnitOfWork, token_service: TokenService) -> None:
        self._uow = uow
        self.token_service = token_service

    async def execute(self, command: UserLoginCommand) -> tuple[AccessTokenVo, RefreshTokenVo]:
        logger.bind(
            use_case=self.__class__.__name__,
            email=command.email,
            ip_address=command.ip_address,
            user_agent=command.user_agent,
        ).info("Starting user login")

        async with self._uow:
            user_read_repository = UserReadRepository(session=self._uow.session)
            refresh_token_write_repository = RefreshTokenWriteRepository(session=self._uow.session)

            logger.debug("Repositories initialized")

            auth_service = AuthenticationService(
                token_service=self.token_service,
                user_read_repository=user_read_repository,
            )

            credentials = LoginCredentials(email=command.email, password=command.password)
            logger.debug("Authenticating user")

            access, refresh = await auth_service.login(credentials=credentials)
            refresh_payload = self.token_service.verify_refresh(token=refresh)
            logger.bind(user_id=refresh_payload.sub).info("Authentication successful, tokens generated")

            refresh_token_schema = RefreshTokenCreateSchema(
                user_id=refresh_payload.sub,
                id=refresh_payload.jti,
                token_hash=self.token_service.hash_token(refresh.value),
                expires_at=datetime.fromtimestamp(refresh_payload.exp, tz=settings.time.default_tz),
                ip_address=str(command.ip_address),
                user_agent=command.user_agent,
            )
            logger.bind(refresh_id=refresh_token_schema.id).debug("Refresh token schema prepared")

            await refresh_token_write_repository.create(schema=refresh_token_schema)

            await self._uow.commit()
            logger.info("Transaction committed successfully, user logged in")

            return access, refresh
