from flask import Flask, Response, jsonify
from loguru import logger
from pydantic import ValidationError

from api.exceptions.api import ApiException
from domain.exceptions import CustomException
from domain.exceptions.auth import InvalidCredentialsException, WeakPasswordException
from domain.exceptions.refresh_token import RefreshTokenAlreadyRevokedException
from domain.exceptions.user import InvalidUsernameException, UserAlreadyExistsException

ERROR_MAP: dict[type, tuple[str, int]] = {
    UserAlreadyExistsException: ("User with this data already exists", 409),
    WeakPasswordException: ("Password is too weak", 400),
    InvalidUsernameException: ("Invalid username format", 400),
    InvalidCredentialsException: ("Invalid credentials", 401),
    RefreshTokenAlreadyRevokedException: ("Refresh token is already revoked", 400),
}


def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(ApiException)
    def handle_api_error(exc: ApiException) -> tuple[Response, int]:
        logger.info(f"API error: {exc.message}")
        return jsonify({"error": exc.message}), exc.status_code

    @app.errorhandler(CustomException)
    def handle_custom_error(exc: CustomException) -> tuple[Response, int]:
        exc_type = type(exc)
        error_message = str(exc)

        if exc_type in ERROR_MAP:
            _, status_code = ERROR_MAP[exc_type]
            logger.info(f"Handled error: {error_message}")
            return jsonify({"error": error_message}), status_code

        logger.warning(f"Unmapped custom error: {exc_type.__name__} | {error_message}")
        return jsonify({"error": error_message}), 500

    @app.errorhandler(ValidationError)
    def handle_validation_error(exc: ValidationError) -> tuple[Response, int]:

        error_details = []
        for err in exc.errors():
            field = err["loc"][-1]
            msg = err["msg"]

            error_details.append(f"[{field}] -> {msg}")

        formatted_msg = "\n".join(error_details)

        logger.info(f"Validation failed: {formatted_msg}")
        return jsonify({"error": "Invalid input data", "details": formatted_msg}), 400

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> tuple[Response, int]:
        logger.exception(f"Unexpected system error: {error}")
        return jsonify({"error": "Internal Server Error"}), 500
