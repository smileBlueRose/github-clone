from loguru import logger

from application.commands.auth import UserRegisterCommand
from application.ports.user_case import AbstractUseCase
from domain.entities.user import User
from domain.ports.repositories.user import AbstractUserWriteRepository
from domain.services.auth.registration import RegistrationService


class RegisterUserUseCase(AbstractUseCase[UserRegisterCommand]):
    def __init__(
        self,
        registration_service: RegistrationService,
        write_repository: AbstractUserWriteRepository,
    ) -> None:
        self.registration_service = registration_service
        self.write_repository = write_repository

    async def execute(self, command: UserRegisterCommand) -> User:
        """
        Register a new user.

        :raises UserAlreadyExistsException: if email or username already exists
        :raises WeakPasswordException: if password doesn't meet requirements
        :raises InvalidUsernameException: if username doesn't meet requirements
        """

        logger.info(f"Starting user registration: email={command.email}, username={command.username}")

        await self.registration_service.validate_registration(
            email=command.email,
            username=command.username,
            password=command.password,
        )
        logger.debug(f"Validation passed for user: {command.email}")

        create_schema = self.registration_service.prepare_user_create_schema(
            email=command.email,
            username=command.username,
            password=command.password,
        )
        logger.debug(f"User schema prepared for: {command.email}")

        user = await self.write_repository.create(schema=create_schema)
        logger.info(f"User registered successfully: id={user.id}, email={user.email}")

        return user
