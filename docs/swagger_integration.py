from flask import Blueprint, render_template_string
from flask_swagger_ui import get_swaggerui_blueprint


def setup_swagger_docs(app):
    """Setup Swagger UI documentation"""

    # Swagger UI blueprint
    SWAGGER_URL = '/docs'
    API_URL = '/static/openapi.yaml'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "IM3Wrap Backend API",
            'supportedSubmitMethods': ['get', 'post', 'put', 'delete'],
            'tryItOutEnabled': True,
            'displayRequestDuration': True
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Serve OpenAPI spec
    @app.route('/static/openapi.yaml')
    def openapi_spec():
        with open('docs/openapi.yaml', 'r') as f:
            return f.read(), 200, {'Content-Type': 'application/x-yaml'}

    # API documentation index
    docs_blueprint = Blueprint('docs', __name__)

    @docs_blueprint.route('/')
    def api_docs():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>IM3Wrap API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
                .section { margin-bottom: 30px; }
                .btn { 
                    display: inline-block; 
                    padding: 10px 20px; 
                    background: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    margin-right: 10px;
                }
                .btn:hover { background: #0056b3; }
                .code { background: #f8f9fa; padding: 15px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>IM3Wrap Backend API Documentation</h1>
                <p>Comprehensive API documentation for the IM3Wrap backend service.</p>
                <p><strong>Version:</strong> 2.0.0 | <strong>Generated:</strong> {{ timestamp }}</p>
            </div>

            <div class="section">
                <h2>Quick Links</h2>
                <a href="/docs" class="btn">Interactive API Documentation (Swagger UI)</a>
                <a href="/static/openapi.yaml" class="btn">OpenAPI Specification</a>
                <a href="/health" class="btn">API Health Check</a>
            </div>

            <div class="section">
                <h2>Getting Started</h2>
                <p>To get started with the IM3Wrap API:</p>
                <ol>
                    <li>Register a new user account using <code>POST /api/auth/register</code></li>
                    <li>Login to get your JWT token using <code>POST /api/auth/login</code></li>
                    <li>Use the token in Authorization header for authenticated endpoints</li>
                    <li>Set your phone number using <code>PUT /api/user/me</code></li>
                    <li>Authenticate with IM3 using OTP verification</li>
                    <li>Browse and purchase packages</li>
                </ol>
            </div>

            <div class="section">
                <h2>Quick Test</h2>
                <p>Test the API health:</p>
                <div class="code">
                    curl {{ base_url }}/health
                </div>
            </div>

            <div class="section">
                <h2>Authentication Example</h2>
                <div class="code">
# Register<br>
curl -X POST {{ base_url }}/auth/register \\<br>
&nbsp;&nbsp;-H "Content-Type: application/json" \\<br>
&nbsp;&nbsp;-d '{"username":"testuser","password":"password123"}'<br><br>

# Login<br>
curl -X POST {{ base_url }}/auth/login \\<br>
&nbsp;&nbsp;-H "Content-Type: application/json" \\<br>
&nbsp;&nbsp;-d '{"username":"testuser","password":"password123"}'
                </div>
            </div>
        </body>
        </html>
        """,
                                      timestamp="2025-05-31T09:44:01Z",
                                      base_url="{{ request.url_root }}api"
                                      )

    app.register_blueprint(docs_blueprint, url_prefix='/api-docs')