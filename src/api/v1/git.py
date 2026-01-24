from flask import Blueprint

from config import settings
from infrastructure.middleware.auth import require_auth

git_router = Blueprint("git", __name__, url_prefix=settings.api.git.prefix)


@git_router.route("/", methods=["GET"])
@require_auth()
def hello_from_git() -> str:
    return "Hello from git!"
