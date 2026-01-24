import logging
import uuid
from typing import TYPE_CHECKING

from flask import Flask, Response, g, has_app_context, request
from loguru import logger

if TYPE_CHECKING:
    from loguru import Record


def setup_logging_middleware(app: Flask) -> None:
    def patch_record(record: "Record") -> None:
        if has_app_context():
            request_id = getattr(g, "request_id", None)
            if request_id:
                record["extra"]["request_id"] = request_id

    logger.configure(patcher=patch_record)

    logging.getLogger("uvicorn.access").level = logging.WARNING
    logging.getLogger("werkzeug").level = logging.WARNING

    @app.before_request
    def add_request_id() -> None:
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    @app.after_request
    def log_request(response: Response) -> Response:
        logger.info(f'{request.remote_addr} - "{request.method} {request.path}" {response.status_code}')

        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id
        return response
