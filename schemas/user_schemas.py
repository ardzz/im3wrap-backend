from marshmallow import Schema, fields, validate


class UpdateUserSchema(Schema):
    """Schema for updating user profile"""
    username = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Regexp(
            r'^[a-zA-Z0-9_.-]+$',
            error="Username can only contain letters, numbers, underscores, dots and hyphens"
        )
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


class ChangePasswordSchema(Schema):
    """Schema for changing user password"""
    old_password = fields.Str(required=True)
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128)
    )