from core.response import SuccessResponse
from schemas.auth_schemas import RegistrationSchema, LoginSchema
from services.auth_service import AuthService
from .base_controller import validate_json


class AuthController:
    """Authentication controller - thin layer over AuthService"""

    def __init__(self):
        self.auth_service = AuthService()

    @validate_json(RegistrationSchema)
    def register(self, validated_data: dict):
        """Register a new user"""
        result = self.auth_service.register(
            username=validated_data['username'],
            password=validated_data['password']
        )

        return SuccessResponse(
            data=result,
            message="User registered successfully"
        ).to_response(201)

    @validate_json(LoginSchema)
    def login(self, validated_data: dict):
        """Login user"""
        result = self.auth_service.login(
            username=validated_data['username'],
            password=validated_data['password']
        )

        return SuccessResponse(
            data=result,
            message="Login successful"
        ).to_response()