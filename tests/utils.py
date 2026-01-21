from typing import Any

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import UserModel


async def create_user_model(session: AsyncSession, **kwargs: Any) -> UserModel:
    if "password" in kwargs:
        password = kwargs.pop("password")
        kwargs["password_hash"] = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    defaults = {
        "email": "test@example.com",
        "username": "ScarletScarf",
        "password_hash": "$2b$12$6rEUV1t6EHbC.HnelrKE9OntR1MUITbOJqteguORQ0un0CIRu/EzS",
    }
    defaults.update(kwargs)
    user = UserModel(**defaults)
    session.add(user)
    await session.flush()

    return user
