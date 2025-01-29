from flask import Blueprint
from controllers.im3_auth import IM3Auth

im3_routes = Blueprint('im3_routes', __name__)


@im3_routes.route('/send-otp', methods=['GET'])
def send_otp():
    return IM3Auth.send_otp()


@im3_routes.route('/verify-otp', methods=['POST'])
def verify_otp():
    return IM3Auth.verify_otp()


@im3_routes.route('/profile', methods=['GET'])
def get_profile():
    return IM3Auth.get_profile()