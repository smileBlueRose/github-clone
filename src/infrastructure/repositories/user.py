from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.exceptions.user import UserNotFoundException
from domain.filters.user import UserFilter
from domain.ports.repositories.user import AbstractUserReadRepository, AbstractUserWriteRepository
from domain.schemas.user import UserCreateSchema, UserUpdateSchema
from infrastructure.database.models.user import UserModel


class UserWriteRepository(AbstractUserWriteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, schema: UserCreateSchema) -> User:
        user_model = UserModel(
            email=schema.email,
            username=schema.username,
            hashed_password=schema.hashed_password,
        )
        self._session.add(user_model)
        await self._session.flush()

        return user_model.to_entity()

    async def update(self, identity: UUID, schema: UserUpdateSchema) -> User:
        user_model: UserModel | None = await self._session.get(UserModel, identity)

        if user_model is None:
            raise UserNotFoundException(user_id=identity)

        if schema.username is not None:
            user_model.username = schema.username

        if schema.password_hash is not None:
            user_model.hashed_password = schema.password_hash

        await self._session.flush()

        return user_model.to_entity()

    async def delete_by_identity(self, identity: UUID) -> bool:
        user_model = await self._session.get(UserModel, identity)

        if user_model is None:
            return False

        await self._session.delete(user_model)
        await self._session.flush()

        return True


class UserReadRepository(AbstractUserReadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_identity(self, identity: UUID) -> User:
        user_model = await self._session.get(UserModel, identity)
        if user_model is None:
            raise UserNotFoundException(user_id=identity)
        return user_model.to_entity()

    async def get_by_email(self, email: EmailStr) -> User:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        user_model = result.scalar_one_or_none()

        if user_model is None:
            raise UserNotFoundException(email=email)

        return user_model.to_entity()

    async def get_by_username(self, username: str) -> User:
        result = await self._session.execute(select(UserModel).where(UserModel.username == username))
        user_model = result.scalar_one_or_none()

        if user_model is None:
            raise UserNotFoundException(username=username)

        return user_model.to_entity()

    async def get_all(self, filter_: UserFilter) -> list[User]:
        stmt = select(UserModel)
        result = await self._session.execute(stmt)
        return [i.to_entity() for i in result.scalars().all()]
