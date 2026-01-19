import uuid

from flask import Flask, Response, g, has_app_context, request
from loguru import logger


def setup_logging_middleware(app: Flask) -> None:
    logger.configure(
        patcher=lambda record: record["extra"].update(
            request_id=getattr(g, "request_id", "system") if has_app_context() else "system"
        )
    )

    @app.before_request
    def add_request_id() -> None:
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    @app.after_request
    def add_header(response: Response) -> Response:
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = str(g.request_id)
        return response
