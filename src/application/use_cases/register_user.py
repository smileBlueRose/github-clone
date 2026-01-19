from loguru import logger

from application.commands.auth import UserRegisterCommand
from application.ports.uow import AbstractUnitOfWork
from application.ports.user_case import AbstractUseCase
from domain.entities.user import User
from domain.services.auth.registration import RegistrationService
from infrastructure.repositories.user import UserReadRepository, UserWriteRepository


class RegisterUserUseCase(AbstractUseCase[UserRegisterCommand]):
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: UserRegisterCommand) -> User:
        with logger.contextualize(email=command.email):
            logger.bind(use_case=self.__class__.__name__, username=command.username).info("Starting user registration")

            async with self._uow:

                read_repo = UserReadRepository(session=self._uow.session)
                write_repo = UserWriteRepository(session=self._uow.session)
                registration_service = RegistrationService(read_repository=read_repo)

                await registration_service.validate_registration(
                    email=command.email,
                    username=command.username,
                    password=command.password,
                )
                logger.debug("Registration validation passed")

                create_schema = registration_service.prepare_user_create_schema(
                    email=command.email,
                    username=command.username,
                    password=command.password,
                )
                logger.debug("User schema prepared")

                user = await write_repo.create(schema=create_schema)

                logger.bind(user_id=user.id).info("User entity created")

                await self._uow.commit()
                logger.info("Transaction committed successfully")

                return user
