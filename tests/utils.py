from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import UserModel


async def create_user_model(session: AsyncSession, **kwargs: Any) -> UserModel:
    defaults = {
        "email": "test@example.com",
        "username": "ScarletScarf",
        "hashed_password": "$2b$12$6rEUV1t6EHbC.HnelrKE9OntR1MUITbOJqteguORQ0un0CIRu/EzS",
    }
    defaults.update(kwargs)
    user = UserModel(**defaults)
    session.add(user)
    await session.flush()

    return user
