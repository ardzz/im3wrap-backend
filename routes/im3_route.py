from flask import Blueprint
from controllers.im3_auth import IM3Auth
from controllers.im3_package import IM3Package

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


@im3_routes.route('/package', methods=['GET'])
def get_package():
    return IM3Package.get_package()


@im3_routes.route('/package/buy', methods=['POST'])
def buy_package():
    return IM3Package.purchase_package()
