from marshmallow import Schema, ValidationError as MarshmallowValidationError
from core.exceptions import ValidationError


class BaseSchema(Schema):
    """Base schema with custom error handling"""

    def handle_error(self, error: MarshmallowValidationError, data, **kwargs):
        """Convert marshmallow validation errors to our custom format"""
        raise ValidationError("Validation failed", details=error.messages)