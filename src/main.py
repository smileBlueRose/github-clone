import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask

app = Flask(__name__)

@app.get("/")
async def index() -> dict[str, str]:
    return {"message": "Hello World!"}

asgi_app = WsgiToAsgi(app)  # type: ignore

if __name__ == "__main__":
    uvicorn.run("main:asgi_app", host="127.0.0.1", port=5000, reload=True)