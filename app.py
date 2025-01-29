import os

from dotenv import load_dotenv
from flask import Flask
from celery import Celery
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from database import db
from middleware.auth_middleware import auth_middleware
from models.user import User
from models.package import Package
from models.transaction import Transaction

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY_BROKER_URL='redis://redis:6379/0',
        CELERY_RESULT_BACKEND='redis://redis:6379/0',
        CELERY_WORKER_SEND_TASK_EVENTS=True,
        CELERY_TASK_SEND_SENT_EVENT=True,
        CELERY_ENABLE_UTC=True,
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'postgresql+psycopg2://myuser:mypassword@db:5432/im3wrap'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET', 'jwt-super-secret-key'),
        WTF_CSRF_ENABLED=False
    )

    # Middleware
    exclude_routes = ['auth_routes.login', 'auth_routes.register']
    app = auth_middleware(exempt_routes=exclude_routes)(app)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    with app.app_context():
        from routes.auth_route import auth_routes
        from routes.profile_route import user_routes
        from routes.im3_route import im3_routes

        app.register_blueprint(auth_routes, url_prefix='/auth')
        app.register_blueprint(user_routes, url_prefix='/user')
        app.register_blueprint(im3_routes, url_prefix='/im3')

    celery = Celery(app.import_name,
                    broker=app.config['CELERY_BROKER_URL'],
                    include=['tasks.package_transaction'])  # Add this line
    celery.conf.update(app.config)
    app.celery = celery

    return app


app = create_app()
celery = app.celery

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_DEBUG', False))
