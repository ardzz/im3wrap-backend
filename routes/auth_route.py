from flask import Blueprint
from controllers.auth_controller import AuthController

auth_routes = Blueprint('auth_routes', __name__)


@auth_routes.route('/register', methods=['POST'])
def register():
    return AuthController.register()


@auth_routes.route('/login', methods=['POST'])
def login():
    return AuthController.login()

