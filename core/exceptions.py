class BaseAPIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message, code=None, status_code=400):
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Raised when input validation fails"""
    def __init__(self, message, details=None):
        self.details = details or {}
        super().__init__(message, "VALIDATION_ERROR", 400)


class BusinessLogicError(BaseAPIException):
    """Raised when business logic validation fails"""
    def __init__(self, message, details=None):
        self.details = details or {}
        super().__init__(message, "BUSINESS_LOGIC_ERROR", 422)


class AuthenticationError(BaseAPIException):
    """Raised when authentication fails"""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid"""
    def __init__(self, message="Invalid username or password"):
        super().__init__(message)


class AuthorizationError(BaseAPIException):
    """Raised when authorization fails"""
    def __init__(self, message="Access denied"):
        super().__init__(message, "AUTHORIZATION_ERROR", 403)


class NotFoundError(BaseAPIException):
    """Raised when a resource is not found"""
    def __init__(self, message="Resource not found"):
        super().__init__(message, "NOT_FOUND_ERROR", 404)


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found"""
    def __init__(self, message="User not found"):
        super().__init__(message)


class PackageNotFoundError(NotFoundError):
    """Raised when a package is not found"""
    def __init__(self, message="Package not found"):
        super().__init__(message)


class ConflictError(BaseAPIException):
    """Raised when there's a conflict with existing data"""
    def __init__(self, message="Conflict with existing data"):
        super().__init__(message, "CONFLICT_ERROR", 409)


class UsernameExistsError(ConflictError):
    """Raised when a username already exists"""
    def __init__(self, message="Username already exists"):
        super().__init__(message)


class EmailExistsError(ConflictError):
    """Raised when an email already exists"""
    def __init__(self, message="Email already exists"):
        super().__init__(message)


class PhoneNumberExistsError(ConflictError):
    """Raised when a phone number already exists"""
    def __init__(self, message="Phone number already exists"):
        super().__init__(message)


class InternalServerError(BaseAPIException):
    """Raised when an internal server error occurs"""
    def __init__(self, message="Internal server error"):
        super().__init__(message, "INTERNAL_SERVER_ERROR", 500)