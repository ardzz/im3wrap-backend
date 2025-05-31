from flask import Blueprint
from controllers.package_controller import PackageController

package_routes = Blueprint('package_routes', __name__)
package_controller = PackageController()

@package_routes.route('/packages', methods=['GET'])
@package_routes.route('/', methods=['GET'])
def get_packages():
    return package_controller.get_packages()

@package_routes.route('/<int:package_id>/purchase', methods=['POST'])
def purchase_package(package_id):
    return package_controller.purchase_package(package_id)

@package_routes.route('/transactions', methods=['GET'])
def get_transactions():
    return package_controller.get_transactions()

@package_routes.route('/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    return package_controller.get_transaction(transaction_id)