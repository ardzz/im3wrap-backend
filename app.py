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
from routes.auth_route import auth_routes
from routes.profile_route import user_routes
from routes.im3_route import im3_routes

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
    )

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'jwt-super-secret-key')
    app.config['WTF_CSRF_ENABLED'] = False

    app.register_blueprint(auth_routes, url_prefix='/auth')
    app.register_blueprint(user_routes, url_prefix='/user')
    app.register_blueprint(im3_routes, url_prefix='/im3')

    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'],
    )
    celery.conf.update(app.config)

    exclude_routes = ['auth_routes.login', 'auth_routes.register']
    app = auth_middleware(exempt_routes=exclude_routes)(app)

    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    return app, celery


app, celery = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
