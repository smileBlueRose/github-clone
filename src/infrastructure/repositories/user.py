from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.exceptions.user import UserNotFoundException
from domain.ports.repositories.user import AbstractUserWriteRepository
from domain.schemas.user import UserCreateSchema, UserUpdateSchema
from infrastructure.database.models.user import UserModel


class UserWriteRepository(AbstractUserWriteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def create(self, schema: UserCreateSchema) -> User:
        user_model = UserModel(
            email=schema.email,
            username=schema.username,
            hashed_password=schema.hashed_password,
        )
        self.__session.add(user_model)
        await self.__session.flush()

        return self._model_to_entity(user=user_model)

    async def update(self, identity: UUID, schema: UserUpdateSchema) -> User:
        user_model: UserModel | None = await self.__session.get(UserModel, identity)

        if user_model is None:
            raise UserNotFoundException(f"User with identity={identity} not found")

        if schema.username is not None:
            user_model.username = schema.username

        if schema.password_hash is not None:
            user_model.hashed_password = schema.password_hash

        await self.__session.flush()

        return self._model_to_entity(user=user_model)

    async def delete_by_identity(self, identity: UUID) -> bool:
        user_model = await self.__session.get(UserModel, identity)

        if user_model is None:
            return False

        await self.__session.delete(user_model)
        await self.__session.flush()

        return True

    def _model_to_entity(self, user: UserModel) -> User:
        return User(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )
