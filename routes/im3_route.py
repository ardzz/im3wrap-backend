from flask import Blueprint
from controllers.im3_controller import IM3Controller

im3_routes = Blueprint('im3_routes', __name__)
im3_controller = IM3Controller()

@im3_routes.route('/send-otp', methods=['GET'])
def send_otp():
    return im3_controller.send_otp()

@im3_routes.route('/verify-otp', methods=['POST'])
def verify_otp():
    return im3_controller.verify_otp()

@im3_routes.route('/profile', methods=['GET'])
def get_profile():
    return im3_controller.get_profile()