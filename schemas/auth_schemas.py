from marshmallow import fields, validate
from .base_schema import BaseSchema

class RegistrationSchema(BaseSchema):
    """User registration schema"""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50),
        error_messages={'required': 'Username is required'}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={'required': 'Password is required'}
    )

class LoginSchema(BaseSchema):
    """User login schema"""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50),
        error_messages={'required': 'Username is required'}
    )
    password = fields.Str(
        required=True,
        error_messages={'required': 'Password is required'}
    )