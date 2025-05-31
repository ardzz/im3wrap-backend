from typing import Dict, Any

from workers.base.base_task import BaseTask
from workers.base.task_status import TaskStatus, TaskResult
from workers.handlers.package_handler import PackagePurchaseHandler
from workers.exceptions import (
    UserNotAuthenticatedError,
    PackageNotFoundError,
    TaskError
)
from services.user_service import UserService
from services.package_service import PackageService
from repositories.transaction_repository import TransactionRepository


# Import celery instance directly from app
def register_package_tasks(celery_app):
    """Register package tasks with the Celery app"""

    @celery_app.task(bind=True, base=BaseTask, name='workers.tasks.purchase_package')
    def purchase_package_task(self, user_id: int, package_id: int) -> Dict[str, Any]:
        """
        Purchase package task - refactored with proper separation of concerns
        """
        try:
            self.logger.info(f"Starting package purchase for user {user_id}, package {package_id}")

            # Initialize services (using dependency injection pattern)
            user_service = UserService()
            package_service = PackageService()
            transaction_repo = TransactionRepository()
            purchase_handler = PackagePurchaseHandler()

            # Get user and package
            user = user_service.repository.get_or_raise(user_id)
            package = package_service.repository.get_or_raise(package_id)

            self.logger.info(f"Processing purchase: User {user.username}, Package {package.package_name}")

            # Find the transaction record
            transaction = transaction_repo.session.query(transaction_repo.model).filter_by(
                user_id=user_id,
                package_id=package_id,
                status="PENDING"
            ).first()

            if not transaction:
                raise TaskError("No pending transaction found for this purchase")

            # Set up progress callback to update transaction status
            def update_transaction_progress(status: TaskStatus, progress: int = None,
                                            error: str = None, details: Dict[str, Any] = None):
                transaction.status = status.value
                if error:
                    transaction.status = f"FAILED_{status.value}"
                transaction_repo.session.commit()
                self.update_status(status, progress, error, details)

            self.set_progress_callback(update_transaction_progress)

            # Process the purchase
            result = purchase_handler.process_purchase(
                user=user,
                package=package,
                progress_callback=update_transaction_progress
            )

            # Update transaction with results
            transaction.qr_code = result.get('qr_code')
            transaction.status = TaskStatus.PAYMENT_INITIATED.value
            transaction_repo.session.commit()

            self.logger.info(f"Package purchase completed successfully for user {user_id}")

            return {
                "task_result": TaskResult.SUCCESS.value,
                "transaction_id": transaction.id,
                "user_id": user_id,
                "package_id": package_id,
                "execution_details": result
            }

        except UserNotAuthenticatedError as e:
            self.logger.error(f"User authentication error: {e}")
            return self.handle_exception(e)

        except PackageNotFoundError as e:
            self.logger.error(f"Package not found error: {e}")
            return self.handle_exception(e)

        except Exception as e:
            self.logger.exception(f"Unexpected error in package purchase task: {e}")
            return self.handle_exception(e)

    @celery_app.task(bind=True, base=BaseTask, name='workers.tasks.check_transaction_status')
    def check_transaction_status_task(self, transaction_id: int) -> Dict[str, Any]:
        """
        Check and update transaction status
        """
        try:
            self.logger.info(f"Checking status for transaction {transaction_id}")

            transaction_repo = TransactionRepository()
            transaction = transaction_repo.get_by_id(transaction_id)

            if not transaction:
                raise TaskError(f"Transaction {transaction_id} not found")

            # Here you would implement actual status checking logic
            # For now, this is a placeholder

            return {
                "transaction_id": transaction_id,
                "status": transaction.status,
                "checked_at": "2025-05-31T10:41:40Z"
            }

        except Exception as e:
            self.logger.exception(f"Error checking transaction status: {e}")
            return self.handle_exception(e)

    return purchase_package_task, check_transaction_status_task