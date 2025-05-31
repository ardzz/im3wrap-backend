from models.user import User
from database import db
from core.exceptions import ValidationError, NotFoundError, AuthenticationError


class UserService:
    """User management service"""

    def get_user_profile(self, user_id: int):
        """Get user profile by ID"""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "token_id": user.token_id,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

    def update_user_profile(self, user_id: int, **kwargs):
        """Update user profile"""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Check for email conflicts
        if 'email' in kwargs and kwargs['email']:
            existing_user = User.query.filter(
                User.email == kwargs['email'],
                User.id != user_id
            ).first()
            if existing_user:
                raise ValidationError("Email already exists")

        # Check for phone number conflicts
        if 'phone_number' in kwargs and kwargs['phone_number']:
            existing_user = User.query.filter(
                User.phone_number == kwargs['phone_number'],
                User.id != user_id
            ).first()
            if existing_user:
                raise ValidationError("Phone number already exists")

        # Update user fields
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        try:
            db.session.commit()
            return self.get_user_profile(user_id)
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"Failed to update user: {str(e)}")

    def change_password(self, user_id: int, old_password: str, new_password: str):
        """Change user password"""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Verify old password
        if not user.check_password(old_password):
            raise AuthenticationError("Current password is incorrect")

        # Update password
        user.hash_password(new_password)

        try:
            db.session.commit()
            return {"message": "Password changed successfully"}
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"Failed to change password: {str(e)}")