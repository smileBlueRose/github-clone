from flask import Blueprint

from config import settings

from .users import users_router

router = Blueprint("api_v1", __name__, url_prefix=settings.api.v1.prefix)
router.register_blueprint(users_router)
