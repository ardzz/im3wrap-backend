from marshmallow import fields
from .base_schema import BaseSchema

class PurchasePackageSchema(BaseSchema):
    """Purchase package schema"""
    package_id = fields.Int(
        required=True,
        error_messages={'required': 'Package ID is required'}
    )