from datetime import datetime
from flask import jsonify


class SuccessResponse:
    """Standard success response format"""

    def __init__(self, data=None, message="Success", timestamp=None):
        self.data = data
        self.message = message
        self.timestamp = timestamp or datetime.utcnow().isoformat() + 'Z'

    def to_response(self, status_code=200):
        """Convert to Flask response"""
        response_data = {
            "success": True,
            "timestamp": self.timestamp,
            "message": self.message
        }

        if self.data is not None:
            response_data["data"] = self.data

        return jsonify(response_data), status_code


class ErrorResponse:
    """Standard error response format"""

    def __init__(self, code, message, details=None, timestamp=None):
        self.code = code
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp or datetime.utcnow().isoformat() + 'Z'

    def to_response(self, status_code=400):
        """Convert to Flask response"""
        response_data = {
            "success": False,
            "timestamp": self.timestamp,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }

        return jsonify(response_data), status_code