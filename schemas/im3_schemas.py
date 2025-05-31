from marshmallow import fields, validate
from .base_schema import BaseSchema

class VerifyOTPSchema(BaseSchema):
    """Verify OTP schema"""
    code = fields.Str(
        required=True,
        validate=validate.Regexp(r'^\d{4,6}$', error='OTP code must be 4-6 digits'),
        error_messages={'required': 'OTP code is required'}
    )