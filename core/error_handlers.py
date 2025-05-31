import logging

from flask_jwt_extended.exceptions import JWTExtendedException
from marshmallow import ValidationError as MarshmallowValidationError

from .exceptions import BaseAPIException
from .response import ErrorResponse

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register error handlers for the Flask app"""

    @app.errorhandler(BaseAPIException)
    def handle_api_exception(e):
        """Handle custom API exceptions"""
        logger.warning(f"API Exception: {e.code} - {e.message}")
        return ErrorResponse(
            code=e.code,
            message=e.message,
            details=getattr(e, 'details', {})
        ).to_response(e.status_code)

    @app.errorhandler(MarshmallowValidationError)
    def handle_validation_error(e):
        """Handle Marshmallow validation errors"""
        logger.warning(f"Validation error: {e.messages}")
        return ErrorResponse(
            code="VALIDATION_ERROR",
            message="Validation failed",
            details=e.messages
        ).to_response(400)

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(e):
        """Handle JWT related errors"""
        logger.warning(f"JWT error: {str(e)}")
        return ErrorResponse(
            code="AUTHENTICATION_ERROR",
            message="Invalid or expired token",
            details={"jwt_error": str(e)}
        ).to_response(401)

    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 errors"""
        return ErrorResponse(
            code="NOT_FOUND",
            message="Endpoint not found",
            details={"path": str(e)}
        ).to_response(404)

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """Handle method not allowed errors"""
        return ErrorResponse(
            code="METHOD_NOT_ALLOWED",
            message="Method not allowed",
            details={"error": str(e)}
        ).to_response(405)

    @app.errorhandler(500)
    def handle_internal_error(e):
        """Handle internal server errors"""
        logger.error(f"Unexpected error occurred", exc_info=True)
        return ErrorResponse(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={}
        ).to_response(500)