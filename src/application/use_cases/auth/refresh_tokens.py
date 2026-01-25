from datetime import datetime
from typing import Any, NamedTuple

from loguru import logger

from application.commands.auth import RefreshTokensCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.use_case import AbstractUseCase
from config import settings
from domain.exceptions.refresh_token import RefreshTokenAlreadyRevokedException
from domain.exceptions.user import UserInactiveException
from domain.schemas.refresh_token import RefreshTokenCreateSchema
from domain.services.auth.token import TokenService
from domain.value_objects.token import RefreshTokenVo
from infrastructure.repositories.refresh_token import (
    RefreshTokenReadRepository,
    RefreshTokenWriteRepository,
)
from infrastructure.repositories.user import UserReadRepository


class _Repositories(NamedTuple):
    """Repositories container for RefreshTokensUseCase."""

    refresh_read: RefreshTokenReadRepository
    refresh_write: RefreshTokenWriteRepository
    user_read: UserReadRepository


class RefreshTokensUseCase(AbstractUseCase[RefreshTokensCommand]):
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        token_service: TokenService,
    ) -> None:
        self._uow = uow
        self.token_service = token_service

    def _init_repositories(self) -> _Repositories:
        return _Repositories(
            refresh_read=RefreshTokenReadRepository(session=self._uow.session),
            refresh_write=RefreshTokenWriteRepository(session=self._uow.session),
            user_read=UserReadRepository(session=self._uow.session),
        )

    async def execute(self, command: RefreshTokensCommand) -> Any:
        logger.bind(
            use_case=self.__class__.__name__,
            ip_address=command.ip_address,
            user_agent=command.user_agent,
        ).info("Starting token refresh process")

        async with self._uow:
            repos = self._init_repositories()

            payload = self.token_service.verify_refresh(token=RefreshTokenVo(value=command.refresh_token))
            logger.bind(sub=payload.sub, jti=payload.jti).debug("Refresh token verified and parsed")

            old_refresh_entity = await repos.refresh_read.get_by_identity(identity=payload.jti)
            if old_refresh_entity.is_revoked:
                logger.warning("Revoked token reuse detected!")
                raise RefreshTokenAlreadyRevokedException()

            self.token_service.verify_token_hash(
                token=RefreshTokenVo(value=command.refresh_token),
                expected_hash=old_refresh_entity.token_hash,
            )

            await repos.refresh_write.revoke_by_identity(payload.jti)
            logger.debug("Old refresh token revoked in DB")

            user = await repos.user_read.get_by_identity(identity=old_refresh_entity.user_id)
            if not user.is_active:
                logger.bind(user_id=user.id).error("Inactive user attempted refresh!")
                raise UserInactiveException()

            new_access = self.token_service.generate_access(user=user)
            new_refresh = self.token_service.generate_refresh(user=user)

            new_refresh_payload = self.token_service.parse_refresh_without_verification(new_refresh)
            refresh_schema = RefreshTokenCreateSchema(
                user_id=user.id,
                id=new_refresh_payload.jti,
                token_hash=self.token_service.hash_token(new_refresh.value),
                expires_at=datetime.fromtimestamp(new_refresh_payload.exp, tz=settings.time.default_tz),
                ip_address=str(command.ip_address),
                user_agent=command.user_agent,
            )

            await repos.refresh_write.create(schema=refresh_schema)
            await self._uow.commit()
            logger.info("Token rotation successful, transaction committed")

            return new_access, new_refresh
