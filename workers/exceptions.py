"""Worker-specific exceptions"""

class TaskError(Exception):
    """Base task error"""
    pass

class TransientTaskError(TaskError):
    """Transient error that should be retried"""
    pass

class PermanentTaskError(TaskError):
    """Permanent error that should not be retried"""
    pass

class PackageEligibilityError(PermanentTaskError):
    """Package eligibility check failed"""
    pass

class PaymentInitiationError(PermanentTaskError):
    """Payment initiation failed"""
    pass

class UserNotAuthenticatedError(PermanentTaskError):
    """User not authenticated with IM3"""
    pass

class PackageNotFoundError(PermanentTaskError):
    """Package not found"""
    pass

class IM3ServiceError(TransientTaskError):
    """IM3 service temporary error"""
    pass