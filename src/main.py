import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask

from api import router as api_router
from core.config import settings

app = Flask(__name__)
app.register_blueprint(api_router, url_prefix=settings.api.prefix)


@app.get("/")
async def index() -> dict[str, str]:
    return {"message": "Hello World!"}


asgi_app = WsgiToAsgi(app)  # type: ignore

if __name__ == "__main__":
    uvicorn.run(
        "main:asgi_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
