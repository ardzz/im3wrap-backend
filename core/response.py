from typing import Optional, Dict, Any, List
from flask import jsonify
import uuid
from datetime import datetime


class BaseResponse:
    """Base response class"""

    def __init__(self, success: bool = True, request_id: Optional[str] = None):
        self.success = success
        self.request_id = request_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            'success': self.success,
            'request_id': self.request_id,
            'timestamp': self.timestamp
        }

    def to_response(self, status_code: int = 200):
        """Convert to Flask response"""
        return jsonify(self.to_dict()), status_code


class SuccessResponse(BaseResponse):
    """Success response"""

    def __init__(self, data: Any = None, message: Optional[str] = None,
                 meta: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(success=True, **kwargs)
        self.data = data
        self.message = message
        self.meta = meta or {}

    def to_dict(self) -> Dict[str, Any]:
        response = super().to_dict()
        response.update({
            'data': self.data,
            'message': self.message,
            'meta': self.meta
        })
        return response


class ErrorResponse(BaseResponse):
    """Error response"""

    def __init__(self, error_code: str, message: str,
                 details: Optional[Dict[str, Any]] = None,
                 status_code: int = 400, **kwargs):
        super().__init__(success=False, **kwargs)
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        response = super().to_dict()
        response.update({
            'error': {
                'code': self.error_code,
                'message': self.message,
                'details': self.details
            }
        })
        return response

    def to_response(self, status_code: Optional[int] = None):
        """Convert to Flask response"""
        return jsonify(self.to_dict()), status_code or self.status_code


class PaginatedResponse(SuccessResponse):
    """Paginated response"""

    def __init__(self, data: List[Any], page: int, per_page: int,
                 total: int, **kwargs):
        total_pages = (total + per_page - 1) // per_page

        meta = {
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }

        super().__init__(data=data, meta=meta, **kwargs)