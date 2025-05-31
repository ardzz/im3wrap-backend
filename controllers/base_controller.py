import functools
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError


def validate_json(schema_class):
    """Decorator to validate JSON input using Marshmallow schemas"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get JSON data from request
                json_data = request.get_json()
                if json_data is None:
                    return jsonify({
                        "success": False,
                        "timestamp": "2025-05-31T11:12:42Z",
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "message": "No JSON data provided",
                            "details": {}
                        }
                    }), 400

                # Validate using schema
                schema = schema_class()
                validated_data = schema.load(json_data)

                # Pass validated data as keyword argument to preserve self
                return f(*args, validated_data=validated_data, **kwargs)

            except ValidationError as e:
                return jsonify({
                    "success": False,
                    "timestamp": "2025-05-31T11:12:42Z",
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Validation failed",
                        "details": e.messages
                    }
                }), 400

            except Exception as e:
                return jsonify({
                    "success": False,
                    "timestamp": "2025-05-31T11:12:42Z",
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": str(e)
                    }
                }), 500

        return decorated_function
    return decorator


def get_current_user_id():
    """Helper function to get current user ID from JWT token"""
    try:
        return get_jwt_identity()
    except Exception:
        return None