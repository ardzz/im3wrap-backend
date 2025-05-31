import logging
import os

from celery import Celery
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import get_config
from core.error_handlers import register_error_handlers
from database import db
from docs.swagger_integration import setup_swagger_docs
from health import health_bp
from middleware.auth_middleware import auth_middleware
from workers.celery_config import CELERY_CONFIG

load_dotenv()


def setup_logging(app):
    """Setup application logging"""
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/app.log') if not app.config.get('TESTING') else logging.NullHandler()
        ]
    )


def setup_cors(app):
    """Setup CORS configuration"""
    if app.config.get('TESTING'):
        # Allow all origins in testing
        CORS(app, origins="*")
    elif app.config.get('DEBUG'):
        # Development CORS settings
        CORS(app,
             origins=[
                 "http://localhost:3000",  # React dev server
                 "http://localhost:3001",  # Alternative React port
                 "http://localhost:8080",  # Vue dev server
                 "http://127.0.0.1:3000",  # Local development
                 "http://127.0.0.1:8080",  # Local development
                 "http://localhost:5173",  # Vite dev server
                 "http://127.0.0.1:5173"
             ],
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
             supports_credentials=True,
             max_age=3600)
    else:
        # Production CORS settings
        CORS(app,
             origins=[
                 "https://im3wrap.my.id",
                 "https://www.im3wrap.my.id",
                 "https://app.im3wrap.my.id",
                 # Add your production frontend domains here
             ],
             methods=["GET", "POST", "PUT", "DELETE"],
             allow_headers=["Content-Type", "Authorization"],
             supports_credentials=True,
             max_age=86400)  # 24 hours


def create_celery(app):
    """Create and configure Celery instance"""
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])

    # Update configuration from our worker config
    celery.conf.update(CELERY_CONFIG)
    celery.conf.update(app.config)

    # Task base classes
    from workers.base.base_task import BaseTask
    celery.Task = BaseTask

    class ContextTask(BaseTask):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask

    # Register tasks with proper app context
    with app.app_context():
        # Register package tasks
        from workers.tasks.package_tasks import register_package_tasks
        purchase_package_task, check_transaction_status_task = register_package_tasks(celery)

        # Register auth tasks
        from workers.tasks.auth_tasks import register_auth_tasks
        cleanup_expired_tokens_task, validate_im3_tokens_task = register_auth_tasks(celery)

        # Register notification tasks
        from workers.tasks.notification_tasks import register_notification_tasks
        send_notification_task, send_bulk_notifications_task = register_notification_tasks(celery)

        # Store task references for import
        app.celery_tasks = {
            'purchase_package': purchase_package_task,
            'check_transaction_status': check_transaction_status_task,
            'cleanup_expired_tokens': cleanup_expired_tokens_task,
            'validate_im3_tokens': validate_im3_tokens_task,
            'send_notification': send_notification_task,
            'send_bulk_notifications': send_bulk_notifications_task,
        }

    return celery


def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs') and not app.config.get('TESTING'):
        os.makedirs('logs')

    # Setup logging
    setup_logging(app)

    # Setup CORS before other extensions
    setup_cors(app)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # Setup API documentation
    setup_swagger_docs(app)

    # Register error handlers
    register_error_handlers(app)

    # Setup middleware with minimal exempt routes (documentation routes are handled in middleware)
    exclude_routes = [
        'auth_routes.login',
        'auth_routes.register'
    ]
    app = auth_middleware(exempt_routes=exclude_routes)(app)

    # Register blueprints
    with app.app_context():
        from routes.auth_route import auth_routes
        from routes.user_route import user_routes
        from routes.im3_route import im3_routes
        from routes.package_route import package_routes

        app.register_blueprint(auth_routes, url_prefix='/api/auth')
        app.register_blueprint(user_routes, url_prefix='/api/user')
        app.register_blueprint(im3_routes, url_prefix='/api/im3')
        app.register_blueprint(package_routes, url_prefix='/api/packages')

        # Register health check blueprint
        app.register_blueprint(health_bp)

    # Setup Celery
    celery = create_celery(app)
    app.celery = celery

    return app


app = create_app()
celery = app.celery

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', False)
    )