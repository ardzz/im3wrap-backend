from typing import Dict, Any

from core.exceptions import ValidationError
from models.user import User
from repositories.user_repository import UserRepository
from .base_service import BaseService


class UserService(BaseService[User]):
    """User management service"""

    def __init__(self):
        super().__init__(UserRepository())

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile information"""
        user = self.repository.get_or_raise(user_id)

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

    def update_user_profile(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Update user profile"""
        user = self.repository.get_or_raise(user_id)

        # Validate email format if provided
        email = kwargs.get('email')
        if email and '@' not in email:
            raise ValidationError("Invalid email format")

        # Validate phone number format if provided
        phone_number = kwargs.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise ValidationError("Phone number must contain only digits")

        # Update allowed fields
        allowed_fields = ['username', 'email', 'phone_number']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not update_data:
            raise ValidationError("No valid fields provided for update")

        # Check username uniqueness if updating username
        if 'username' in update_data:
            new_username = update_data['username']
            if new_username != user.username and self.repository.username_exists(new_username):
                raise ValidationError("Username already exists")

        updated_user = self.repository.update(user, **update_data)

        self.logger.info(f"User profile updated for user ID: {user_id}")

        return self.get_user_profile(updated_user.id)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, str]:
        """Change user password"""
        user = self.repository.get_or_raise(user_id)

        # Validate old password
        if not user.check_password(old_password):
            raise ValidationError("Current password is incorrect")

        # Validate new password
        if len(new_password) < 8:
            raise ValidationError("New password must be at least 8 characters long")

        if old_password == new_password:
            raise ValidationError("New password must be different from current password")

        # Update password
        user.hash_password(new_password)
        self.repository.update(user, password_hash=user.password_hash)

        self.logger.info(f"Password changed for user ID: {user_id}")

        return {"message": "Password updated successfully"}