from marshmallow import fields, validate
from .base_schema import BaseSchema

class UpdateUserSchema(BaseSchema):
    """Update user profile schema"""
    username = fields.Str(validate=validate.Length(min=3, max=50))
    email = fields.Email()
    phone_number = fields.Str(validate=validate.Regexp(r'^\d+$', error='Phone number must contain only digits'))

class ChangePasswordSchema(BaseSchema):
    """Change password schema"""
    old_password = fields.Str(
        required=True,
        error_messages={'required': 'Current password is required'}
    )
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={'required': 'New password is required'}
    )