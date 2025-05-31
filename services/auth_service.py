from typing import Dict, Any
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from .base_service import BaseService
from repositories.user_repository import UserRepository
from models.user import User
from core.exceptions import (
    ValidationError,
    UsernameExistsError,
    InvalidCredentialsError
)


class AuthService(BaseService[User]):
    """Authentication service"""

    def __init__(self):
        super().__init__(UserRepository())

    def register(self, username: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        self.logger.info(f"Attempting to register user: {username}")

        # Validate input
        if not username or len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long")

        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        # Check if username exists
        if self.repository.username_exists(username):
            raise UsernameExistsError(f"Username '{username}' already exists")

        # Create user
        user = User(username=username)
        user.hash_password(password)

        created_user = self.repository.create(
            username=user.username,
            password_hash=user.password_hash
        )

        self.logger.info(f"User registered successfully: {username} (ID: {created_user.id})")

        return {
            "user_id": created_user.id,
            "username": created_user.username,
            "message": "User registered successfully"
        }

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return access token"""
        self.logger.info(f"Login attempt for user: {username}")

        # Validate input
        if not username or not password:
            raise ValidationError("Username and password are required")

        # Get user
        user = self.repository.get_by_username(username)
        if not user:
            self.logger.warning(f"Login failed - user not found: {username}")
            raise InvalidCredentialsError("Invalid username or password")

        # Check password
        if not user.check_password(password):
            self.logger.warning(f"Login failed - invalid password for user: {username}")
            raise InvalidCredentialsError("Invalid username or password")

        # Create access token
        access_token = create_access_token(identity=str(user.id), expires_delta=False)

        self.logger.info(f"Login successful for user: {username} (ID: {user.id})")

        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "message": "Login successful"
        }