from flask import Blueprint
from controllers.user_controller import UserController

user_routes = Blueprint('user_routes', __name__)
user_controller = UserController()

@user_routes.route('/me', methods=['GET'])
def get_me():
    return user_controller.get_me()

@user_routes.route('/me', methods=['PUT'])
def update_me():
    return user_controller.update_me()

@user_routes.route('/me/change-password', methods=['POST'])
def change_password():
    return user_controller.change_password()