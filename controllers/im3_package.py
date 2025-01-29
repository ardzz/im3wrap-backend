from flask import jsonify, request

from models.package import Package
from models.user import User


class IM3Package:
    @staticmethod
    def get_package():
        try:
            me = User.query.filter_by(id=request.user_id).first()
            if me.token_id is None:
                return jsonify({"error": "You haven't logged in"}), 400
            else:
                packages = Package.query.all()
                if len(packages) > 0:
                    return jsonify([package.to_dict() for package in packages]), 200
                else:
                    return jsonify({"error": "No packages found"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @staticmethod
    def purchase_package():
        me = User.query.filter_by(id=request.user_id).first()
        if me.token_id is None:
            return jsonify({"error": "You haven't logged in"}), 400
        else:
            package = Package.query.filter_by(id=request.json['package_id']).first()
            if package is None:
                return jsonify({"error": "Package not found"}), 400
            else:
                from tasks.package_transaction import purchase_package
                tasks = purchase_package.delay(user_id=me.id, package_id=package.id)
                return jsonify({"package_detail": package.to_dict(), "message": "Transaction is being processed",
                                "transaction_id": tasks.id}), 200
