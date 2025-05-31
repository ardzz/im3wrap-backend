from services.user_service import UserService
from schemas.user_schemas import UpdateUserSchema, ChangePasswordSchema
from core.response import SuccessResponse
from .base_controller import validate_json, get_current_user_id


class UserController:
    """User management controller"""

    def __init__(self):
        self.user_service = UserService()

    def get_me(self):
        """Get current user profile"""
        user_id = get_current_user_id()
        profile = self.user_service.get_user_profile(user_id)

        return SuccessResponse(
            data=profile,
            message="Profile retrieved successfully"
        ).to_response()

    @validate_json(UpdateUserSchema)
    def update_me(self, validated_data: dict):
        """Update current user profile"""
        user_id = get_current_user_id()
        updated_profile = self.user_service.update_user_profile(user_id, **validated_data)

        return SuccessResponse(
            data=updated_profile,
            message="Profile updated successfully"
        ).to_response()

    @validate_json(ChangePasswordSchema)
    def change_password(self, validated_data: dict):
        """Change user password"""
        user_id = get_current_user_id()
        result = self.user_service.change_password(
            user_id=user_id,
            old_password=validated_data['old_password'],
            new_password=validated_data['new_password']
        )

        return SuccessResponse(
            data=result,
            message="Password changed successfully"
        ).to_response()