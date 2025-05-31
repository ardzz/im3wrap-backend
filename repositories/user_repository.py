from typing import Optional
from .base_repository import BaseRepository
from models.user import User
from core.exceptions import UserNotFoundError


class UserRepository(BaseRepository[User]):
    """User repository"""

    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.get_by_field('username', username)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.get_by_field('email', email)

    def get_by_phone(self, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        return self.get_by_field('phone_number', phone_number)

    def username_exists(self, username: str) -> bool:
        """Check if username exists"""
        return self.exists(username=username)

    def email_exists(self, email: str) -> bool:
        """Check if email exists"""
        return self.exists(email=email)

    def get_or_raise(self, user_id: int) -> User:
        """Get user by ID or raise exception"""
        user = self.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return user