from flask import request, g
from functools import wraps


def add_security_headers(app):
    """Add security headers to responses"""

    @app.after_request
    def set_security_headers(response):
        """Set security headers on all responses"""
        security_headers = app.config.get('SECURITY_HEADERS', {})

        for header, value in security_headers.items():
            response.headers[header] = value

        # Add CORS debug info in development
        if app.config.get('DEBUG'):
            response.headers['X-Debug-CORS-Origin'] = request.headers.get('Origin', 'none')
            response.headers['X-Debug-Request-Method'] = request.method

        return response

    return app


def cors_preflight_handler():
    """Handle CORS preflight requests"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'OPTIONS':
                # Handle preflight request
                response = app.make_default_options_response()
                headers = response.headers

                headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
                headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
                headers['Access-Control-Max-Age'] = '3600'

                return response

            return f(*args, **kwargs)

        return decorated_function

    return decorator