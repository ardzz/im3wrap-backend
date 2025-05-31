from core.exceptions import ValidationError, AuthenticationError, NotFoundError
from core.response import SuccessResponse
from database import db
from models.package import Package
from models.transaction import Transaction
from models.user import User
from .base_controller import get_current_user_id


class PackageController:
    """Package management controller"""

    def get_packages(self):
        """Get all available packages"""
        try:
            packages = Package.get_all()
            package_list = [package.to_dict() for package in packages]

            return SuccessResponse(
                data=package_list,
                message="Packages retrieved successfully"
            ).to_response()

        except Exception as e:
            raise ValidationError(f"Failed to get packages: {str(e)}")

    def purchase_package(self, package_id: int):
        """Purchase a package"""
        try:
            user_id = get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")

            user = User.query.get(user_id)
            if not user or not user.token_id:
                raise ValidationError("IM3 account not linked. Please verify OTP first.")

            package = Package.query.get(package_id)
            if not package:
                raise NotFoundError("Package not found")

            # Create transaction record
            transaction = Transaction(
                user_id=user_id,
                package_id=package_id,
                status="PENDING"
            )
            db.session.add(transaction)
            db.session.commit()

            # Queue the purchase task (if Celery is available)
            try:
                from app import app
                if hasattr(app, 'celery_tasks') and 'purchase_package' in app.celery_tasks:
                    task = app.celery_tasks['purchase_package'].delay(transaction.id)

                    return SuccessResponse(
                        data={
                            "transaction_id": transaction.id,
                            "task_id": task.id,
                            "status": "PROCESSING",
                            "message": "Purchase initiated. Check back for updates."
                        },
                        message="Package purchase initiated"
                    ).to_response(202)
                else:
                    # Fallback if Celery is not available
                    transaction.status = "FAILED"
                    db.session.commit()
                    raise ValidationError("Purchase service temporarily unavailable")

            except ImportError:
                transaction.status = "FAILED"
                db.session.commit()
                raise ValidationError("Purchase service not configured")

        except Exception as e:
            if isinstance(e, (ValidationError, AuthenticationError, NotFoundError)):
                raise
            raise ValidationError(f"Failed to purchase package: {str(e)}")

    def get_transactions(self):
        """Get user's transactions"""
        try:
            user_id = get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")

            transactions = Transaction.query.filter_by(user_id=user_id).all()
            transaction_list = []

            for transaction in transactions:
                transaction_data = transaction.to_dict()
                # Add package information
                package = Package.query.get(transaction.package_id)
                if package:
                    transaction_data['package'] = package.to_dict()
                transaction_list.append(transaction_data)

            return SuccessResponse(
                data=transaction_list,
                message="Transactions retrieved successfully"
            ).to_response()

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            raise ValidationError(f"Failed to get transactions: {str(e)}")

    def get_transaction(self, transaction_id: int):
        """Get specific transaction"""
        try:
            user_id = get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")

            transaction = Transaction.query.filter_by(
                id=transaction_id,
                user_id=user_id
            ).first()

            if not transaction:
                raise NotFoundError("Transaction not found")

            transaction_data = transaction.to_dict()
            # Add package information
            package = Package.query.get(transaction.package_id)
            if package:
                transaction_data['package'] = package.to_dict()

            return SuccessResponse(
                data=transaction_data,
                message="Transaction retrieved successfully"
            ).to_response()

        except Exception as e:
            if isinstance(e, (AuthenticationError, NotFoundError)):
                raise
            raise ValidationError(f"Failed to get transaction: {str(e)}")