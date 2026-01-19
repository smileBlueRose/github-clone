from domain.entities.user import User
from infrastructure.database.models.user import UserModel


def user_model_to_entity(user: UserModel) -> User:
    return User(
        id=user.id,
        email=user.email,
        username=user.username,
        hashed_password=user.hashed_password,
        created_at=user.created_at,
    )
