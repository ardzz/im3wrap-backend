import logging
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from .exceptions import BaseAPIException
from .response import ErrorResponse

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers"""

    @app.errorhandler(BaseAPIException)
    def handle_api_exception(error: BaseAPIException):
        """Handle custom API exceptions"""
        logger.error(f"API Exception: {error.error_code} - {error.message}",
                     extra={
                         'error_code': error.error_code,
                         'status_code': error.status_code,
                         'details': error.details,
                         'endpoint': request.endpoint,
                         'method': request.method,
                         'url': request.url
                     })

        return ErrorResponse(
            error_code=error.error_code,
            message=error.message,
            details=error.details,
            status_code=error.status_code
        ).to_response()

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP Exception: {error.code} - {error.description}")

        return ErrorResponse(
            error_code=f"HTTP_{error.code}",
            message=error.description,
            status_code=error.code
        ).to_response()

    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        """Handle unexpected exceptions"""
        logger.exception("Unexpected error occurred")

        return ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An internal error occurred",
            status_code=500
        ).to_response()