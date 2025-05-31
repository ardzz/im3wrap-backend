from typing import Optional, Dict, Any


class BaseAPIException(Exception):
    """Base exception for all API errors"""
    status_code = 500
    error_code = "INTERNAL_ERROR"
    message = "An internal error occurred"

    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Validation error"""
    status_code = 400
    error_code = "VALIDATION_ERROR"
    message = "Validation failed"


class AuthenticationError(BaseAPIException):
    """Authentication error"""
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"
    message = "Authentication failed"


class AuthorizationError(BaseAPIException):
    """Authorization error"""
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"
    message = "Access denied"


class NotFoundError(BaseAPIException):
    """Resource not found error"""
    status_code = 404
    error_code = "NOT_FOUND"
    message = "Resource not found"


class ConflictError(BaseAPIException):
    """Conflict error"""
    status_code = 409
    error_code = "CONFLICT"
    message = "Resource conflict"


class BusinessLogicError(BaseAPIException):
    """Business logic error"""
    status_code = 422
    error_code = "BUSINESS_LOGIC_ERROR"
    message = "Business logic validation failed"


class ExternalServiceError(BaseAPIException):
    """External service error"""
    status_code = 502
    error_code = "EXTERNAL_SERVICE_ERROR"
    message = "External service unavailable"


# IM3 specific exceptions
class IM3AuthError(ExternalServiceError):
    """IM3 authentication service error"""
    error_code = "IM3_AUTH_ERROR"
    message = "IM3 authentication failed"


class IM3PackageError(ExternalServiceError):
    """IM3 package service error"""
    error_code = "IM3_PACKAGE_ERROR"
    message = "IM3 package operation failed"


# User specific exceptions
class UserNotFoundError(NotFoundError):
    """User not found"""
    error_code = "USER_NOT_FOUND"
    message = "User not found"


class UsernameExistsError(ConflictError):
    """Username already exists"""
    error_code = "USERNAME_EXISTS"
    message = "Username already exists"


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials"""
    error_code = "INVALID_CREDENTIALS"
    message = "Invalid username or password"


# Package specific exceptions
class PackageNotFoundError(NotFoundError):
    """Package not found"""
    error_code = "PACKAGE_NOT_FOUND"
    message = "Package not found"


class PackageEligibilityError(BusinessLogicError):
    """Package eligibility error"""
    error_code = "PACKAGE_NOT_ELIGIBLE"
    message = "Package is not eligible for purchase"


class PaymentInitiationError(BusinessLogicError):
    """Payment initiation error"""
    error_code = "PAYMENT_INITIATION_FAILED"
    message = "Failed to initiate payment"