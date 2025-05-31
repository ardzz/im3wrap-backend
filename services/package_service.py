from typing import Dict, Any, List

from core.exceptions import (
    BusinessLogicError,
    PackageNotFoundError
)
from models.package import Package
from models.transaction import Transaction
from repositories.package_repository import PackageRepository
from repositories.transaction_repository import TransactionRepository
from repositories.user_repository import UserRepository
from .base_service import BaseService


class PackageService(BaseService[Package]):
    """Package management service"""

    def __init__(self):
        super().__init__(PackageRepository())
        self.user_repository = UserRepository()
        self.transaction_repository = TransactionRepository()

    def get_available_packages(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all available packages"""
        user = self.user_repository.get_or_raise(user_id)

        if not user.token_id:
            raise BusinessLogicError("User must be authenticated with IM3 to view packages")

        packages = self.repository.get_available_packages()

        return [self._package_to_dict(package) for package in packages]

    def initiate_package_purchase(self, user_id: int, package_id: int) -> Dict[str, Any]:
        """Initiate package purchase (create transaction and queue background task)"""
        user = self.user_repository.get_or_raise(user_id)
        package = self.repository.get_or_raise(package_id)

        if not user.token_id:
            raise BusinessLogicError("User must be authenticated with IM3 to purchase packages")

        # Create transaction record
        transaction = self.transaction_repository.create(
            user_id=user.id,
            package_id=package.id,
            status="PENDING"
        )

        # Import here to avoid circular imports
        from tasks.package_transaction import purchase_package

        # Queue background task
        task = purchase_package.delay(user_id=user.id, package_id=package.id)

        self.logger.info(f"Package purchase initiated for user {user_id}, package {package_id}, task {task.id}")

        return {
            "transaction_id": transaction.id,
            "task_id": task.id,
            "package_detail": self._package_to_dict(package),
            "message": "Transaction is being processed",
            "status": "PENDING"
        }

    def get_user_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's transaction history"""
        user = self.user_repository.get_or_raise(user_id)
        transactions = self.transaction_repository.get_by_user(user_id)

        return [self._transaction_to_dict(transaction) for transaction in transactions]

    def get_transaction_status(self, user_id: int, transaction_id: int) -> Dict[str, Any]:
        """Get transaction status"""
        user = self.user_repository.get_or_raise(user_id)
        transaction = self.transaction_repository.get_by_id(transaction_id)

        if not transaction or transaction.user_id != user_id:
            raise PackageNotFoundError("Transaction not found")

        return self._transaction_to_dict(transaction)

    def _package_to_dict(self, package: Package) -> Dict[str, Any]:
        """Convert package model to dictionary"""
        return {
            "id": package.id,
            "pvr_code": package.pvr_code,
            "keyword": package.keyword,
            "discount_price": package.discount_price,
            "normal_price": package.normal_price,
            "package_name": package.package_name,
            "created_at": package.created_at.isoformat() if package.created_at else None,
            "updated_at": package.updated_at.isoformat() if package.updated_at else None
        }

    def _transaction_to_dict(self, transaction: Transaction) -> Dict[str, Any]:
        """Convert transaction model to dictionary"""
        return {
            "id": transaction.id,
            "user_id": transaction.user_id,
            "package_id": transaction.package_id,
            "status": transaction.status,
            "qr_code": transaction.qr_code,
            "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
            "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None
        }