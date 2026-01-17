from flask import Blueprint

from config import settings

from .v1 import router as v1_router

router = Blueprint("api", __name__, url_prefix=settings.api.prefix)
router.register_blueprint(v1_router)
