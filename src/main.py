import asyncio
import atexit

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask

from api import router as api_router
from config import settings
from infrastructure.database.db_helper import check_connection, db_helper
from infrastructure.di.container import Container

def create_app() -> Flask:
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.register_blueprint(api_router)

    container = Container()
    container.wire(modules=["api.v1.auth"])

    return app
app: Flask = create_app()
asgi_app = WsgiToAsgi(app)  # type: ignore


async def run_server() -> None:
    await check_connection()

    config = uvicorn.Config(
        "main:asgi_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
    server = uvicorn.Server(config)

    try:
        await server.serve()
    finally:
        await db_helper.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass
