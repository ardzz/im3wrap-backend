from functools import wraps
from flask import request
from marshmallow import Schema
from core.response import SuccessResponse, ErrorResponse
from core.exceptions import ValidationError

def validate_json(schema_class: Schema):
    """Decorator to validate JSON input using marshmallow schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                schema = schema_class()
                validated_data = schema.load(request.get_json() or {})
                return f(validated_data, *args, **kwargs)
            except ValidationError as e:
                return ErrorResponse(
                    error_code=e.error_code,
                    message=e.message,
                    details=e.details,
                    status_code=e.status_code
                ).to_response()
        return decorated_function
    return decorator

def get_current_user_id() -> int:
    """Get current authenticated user ID from request context"""
    return int(request.user_id)