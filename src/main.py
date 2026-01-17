import asyncio
import atexit

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask

from api import router as api_router
from config import settings
from infrastructure.database.db_helper import check_connection, db_helper

app = Flask(__name__)
app.register_blueprint(api_router, url_prefix=settings.api.prefix)

asgi_app = WsgiToAsgi(app)  # type: ignore


def shutdown() -> None:
    asyncio.run(db_helper.dispose())


atexit.register(shutdown)


if __name__ == "__main__":
    asyncio.run(check_connection())
    uvicorn.run(
        "main:asgi_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
