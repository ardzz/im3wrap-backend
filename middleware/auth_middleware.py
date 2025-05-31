from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def auth_middleware(exempt_routes=None):
    def middleware_wrapper(app):
        @app.before_request
        def check_authentication():
            # Skip authentication for exempt routes (e.g., login, register)
            # print("endpoint: ", request.endpoint)

            # Default exempt routes
            default_exempt = [
                'auth_routes.login',
                'auth_routes.register',
                'static',  # Static files
                'health_check',  # Health check endpoint
                'cors_test',  # CORS test endpoint
            ]

            # Add custom exempt routes
            all_exempt_routes = default_exempt + (exempt_routes or [])

            # Check if current endpoint should be exempted
            if request.endpoint in all_exempt_routes:
                return

            # Exempt documentation routes
            if request.path.startswith('/docs'):
                return

            if request.path.startswith('/static'):
                return

            if request.path.startswith('/api-docs'):
                return

            # Exempt Swagger UI static files and API spec
            if request.path.startswith('/swaggerui'):
                return

            if request.path.startswith('/health'):
                return

            if request.path == '/static/openapi.yaml':
                return

            # Exempt favicon and other common static requests
            if request.path in ['/favicon.ico', '/robots.txt']:
                return

            # Check for OPTIONS requests (CORS preflight)
            if request.method == 'OPTIONS':
                return

            # Check if a valid JWT exists in the request
            try:
                verify_jwt_in_request()
                # Optionally: Fetch user details
                current_user_id = get_jwt_identity()
                # Store user info in request context (optional)
                request.user_id = current_user_id
            except Exception as e:
                return jsonify({
                    "success": False,
                    "timestamp": "2025-05-31T10:48:51Z",
                    "error": {
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Authentication required",
                        "details": {
                            "endpoint": request.endpoint,
                            "path": request.path,
                            "method": request.method,
                            "error": str(e)
                        }
                    }
                }), 401

        return app

    return middleware_wrapper