from flask import Blueprint

from config import settings

users_router = Blueprint("users", __name__, url_prefix=settings.api.users.prefix)


@users_router.route("/")
def hello_from_users() -> str:
    return "Hello from users!"
