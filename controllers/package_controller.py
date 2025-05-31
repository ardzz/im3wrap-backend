from services.package_service import PackageService
from schemas.package_schemas import PurchasePackageSchema
from core.response import SuccessResponse
from .base_controller import validate_json, get_current_user_id


class PackageController:
    """Package management controller"""

    def __init__(self):
        self.package_service = PackageService()

    def get_packages(self):
        """Get available packages"""
        user_id = get_current_user_id()
        packages = self.package_service.get_available_packages(user_id)

        return SuccessResponse(
            data=packages,
            message="Packages retrieved successfully"
        ).to_response()

    @validate_json(PurchasePackageSchema)
    def purchase_package(self, validated_data: dict):
        """Purchase a package"""
        user_id = get_current_user_id()
        result = self.package_service.initiate_package_purchase(
            user_id=user_id,
            package_id=validated_data['package_id']
        )

        return SuccessResponse(
            data=result,
            message="Package purchase initiated"
        ).to_response()

    def get_transactions(self):
        """Get user's transaction history"""
        user_id = get_current_user_id()
        transactions = self.package_service.get_user_transactions(user_id)

        return SuccessResponse(
            data=transactions,
            message="Transactions retrieved successfully"
        ).to_response()

    def get_transaction_status(self, transaction_id: int):
        """Get transaction status"""
        user_id = get_current_user_id()
        transaction = self.package_service.get_transaction_status(user_id, transaction_id)

        return SuccessResponse(
            data=transaction,
            message="Transaction status retrieved successfully"
        ).to_response()