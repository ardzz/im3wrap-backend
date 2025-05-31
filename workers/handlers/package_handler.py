import time
from typing import Dict, Any
from config import get_config
from workers.base.task_status import TaskStatus, TaskResult
from workers.exceptions import (
    PackageEligibilityError,
    PaymentInitiationError,
    IM3ServiceError,
    UserNotAuthenticatedError,
    PackageNotFoundError
)
from workers.utils.task_monitoring import TaskMonitor
from im3.repository.package import Package as IM3Package


class PackagePurchaseHandler:
    """Handler for package purchase business logic"""

    def __init__(self):
        self.config = get_config().PACKAGE_TASK_CONFIG
        self.eligibility_retries = self.config['eligibility_check_retries']
        self.eligibility_interval = self.config['eligibility_check_interval']
        self.payment_timeout = self.config['payment_timeout']

    def process_purchase(self, user, package, progress_callback=None) -> Dict[str, Any]:
        """Process package purchase with proper error handling and monitoring"""
        monitor = TaskMonitor(f"purchase_{user.id}_{package.id}")

        try:
            # Validate user authentication
            if not user.token_id:
                raise UserNotAuthenticatedError("User is not authenticated with IM3")

            monitor.checkpoint("validation_complete")

            # Initialize IM3 package service
            im3_package = IM3Package(
                pvr_code=package.pvr_code,
                keyword=package.keyword,
                discount_price=package.discount_price,
                normal_price=package.normal_price,
                package_name=package.package_name,
                token_id=user.token_id
            )

            monitor.checkpoint("im3_service_initialized")

            # Step 1: Check package eligibility
            if progress_callback:
                progress_callback(TaskStatus.CHECKING_ELIGIBILITY, 20)

            transid = self._check_package_eligibility(im3_package, monitor)

            monitor.checkpoint("eligibility_checked")

            # Step 2: Wait for eligibility confirmation
            if progress_callback:
                progress_callback(TaskStatus.WAITING_FOR_ELIGIBILITY, 40)

            self._wait_for_eligibility_confirmation(im3_package, transid, monitor)

            monitor.checkpoint("eligibility_confirmed")

            # Step 3: Initiate payment
            if progress_callback:
                progress_callback(TaskStatus.INITIATING_PAYMENT, 70)

            qr_code = self._initiate_payment(im3_package, transid, monitor)

            monitor.checkpoint("payment_initiated")

            if progress_callback:
                progress_callback(TaskStatus.PAYMENT_INITIATED, 100)

            execution_time = monitor.get_execution_time()

            return {
                "result": TaskResult.PAYMENT_INITIATED_SUCCESSFULLY.value,
                "qr_code": qr_code,
                "transaction_id": transid,
                "execution_time": execution_time,
                "checkpoints": monitor.checkpoints
            }

        except Exception as e:
            monitor.checkpoint("error_occurred", {"error": str(e)})
            raise

    def _check_package_eligibility(self, im3_package: IM3Package, monitor: TaskMonitor) -> str:
        """Check package eligibility"""
        try:
            response = im3_package.check_eligible()

            if response.get('status') != '0':
                error_msg = response.get('message', 'Unknown eligibility check error')
                monitor.checkpoint("eligibility_check_failed", {"error": error_msg})
                raise PackageEligibilityError(f"Package eligibility check failed: {error_msg}")

            transid = response.get('transid')
            if not transid:
                raise PackageEligibilityError("No transaction ID received from eligibility check")

            monitor.checkpoint("eligibility_check_success", {"transid": transid})
            return transid

        except Exception as e:
            if isinstance(e, PackageEligibilityError):
                raise
            raise IM3ServiceError(f"IM3 service error during eligibility check: {str(e)}")

    def _wait_for_eligibility_confirmation(self, im3_package: IM3Package, transid: str, monitor: TaskMonitor):
        """Wait for eligibility confirmation with retries"""
        for attempt in range(1, self.eligibility_retries + 1):
            monitor.checkpoint(f"eligibility_status_check_attempt_{attempt}")

            try:
                response = im3_package.check_eligible_status(transid)

                if response.get('status') == '0' and 'eligibility' in response.get('data', {}):
                    monitor.checkpoint("eligibility_confirmed", {"attempt": attempt})
                    return

                # If not ready yet, wait before next attempt
                if attempt < self.eligibility_retries:
                    time.sleep(self.eligibility_interval)

            except Exception as e:
                monitor.checkpoint(f"eligibility_status_error_attempt_{attempt}", {"error": str(e)})
                if attempt == self.eligibility_retries:
                    raise IM3ServiceError(f"Failed to check eligibility status: {str(e)}")
                time.sleep(self.eligibility_interval)

        # If we get here, eligibility was not confirmed
        monitor.checkpoint("eligibility_timeout")
        raise PackageEligibilityError("Package eligibility could not be confirmed within timeout period")

    def _initiate_payment(self, im3_package: IM3Package, transid: str, monitor: TaskMonitor) -> str:
        """Initiate payment process"""
        try:
            response = im3_package.initiate_payment(transid)

            if response.get('status') != '0':
                error_msg = response.get('message', 'Unknown payment initiation error')
                monitor.checkpoint("payment_initiation_failed", {"error": error_msg})
                raise PaymentInitiationError(f"Payment initiation failed: {error_msg}")

            qr_code = response.get('data', {}).get('SendPaymentResp', {}).get('actionData')
            if not qr_code:
                raise PaymentInitiationError("No QR code received from payment initiation")

            monitor.checkpoint("payment_initiation_success", {"qr_code_length": len(qr_code)})
            return qr_code

        except Exception as e:
            if isinstance(e, PaymentInitiationError):
                raise
            raise IM3ServiceError(f"IM3 service error during payment initiation: {str(e)}")