from marshmallow import Schema, fields, validate


class RegistrationSchema(Schema):
    """Schema for user registration"""
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=80),
            validate.Regexp(
                r'^[a-zA-Z0-9_]+$',
                error="Username can only contain letters, numbers, and underscores"
            )
        ]
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128)
    )
    email = fields.Email(required=False, allow_none=True)
    phone_number = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Regexp(
            r'^[0-9+\-\s()]+$',
            error="Invalid phone number format"
        )
    )


class LoginSchema(Schema):
    """Schema for user login"""
    username = fields.Str(required=True)
    password = fields.Str(required=True)