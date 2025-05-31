from flask import Blueprint
from controllers.auth_controller import AuthController

auth_routes = Blueprint('auth_routes', __name__)
auth_controller = AuthController()

@auth_routes.route('/register', methods=['POST'])
def register():
    return auth_controller.register()

@auth_routes.route('/login', methods=['POST'])
def login():
    return auth_controller.login()