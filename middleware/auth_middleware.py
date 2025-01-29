from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def auth_middleware(exempt_routes=None):
    def middleware_wrapper(app):
        @app.before_request
        def check_authentication():
            # Skip authentication for exempt routes (e.g., login, register)
            # print("endpoint: ", request.endpoint)
            if request.endpoint in (exempt_routes or []):
                return

            # Check if a valid JWT exists in the request
            try:
                verify_jwt_in_request()
                # Optionally: Fetch user details
                current_user_id = get_jwt_identity()
                # Store user info in request context (optional)
                request.user_id = current_user_id
            except Exception as e:
                return jsonify({"error": "Unauthorized", "message": str(e)}), 401

        return app

    return middleware_wrapper
