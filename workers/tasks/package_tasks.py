import time
import traceback

from celery.utils.log import get_task_logger

from database import db
from im3.repository.package import Package as IM3Package
from models.package import Package
from models.transaction import Transaction
from models.user import User

logger = get_task_logger(__name__)


def register_package_tasks(celery_app):
    """Register package-related tasks with the Celery app"""

    @celery_app.task(bind=True, name='purchase_package', queue='package_purchases')
    def purchase_package_task(self, transaction_id):
        """
        Process package purchase for a given transaction

        Args:
            transaction_id (int): ID of the transaction to process
        """
        logger.info(f"Starting package purchase for transaction {transaction_id}")

        try:
            # Get transaction from database
            transaction = Transaction.query.get(transaction_id)
            if not transaction:
                raise Exception(f"Transaction {transaction_id} not found")

            # Get related package and user
            package = Package.query.get(transaction.package_id)
            if not package:
                raise Exception(f"Package {transaction.package_id} not found")

            user = User.query.get(transaction.user_id)
            if not user or not user.token_id:
                raise Exception(f"User {transaction.user_id} not found or IM3 not linked")

            logger.info(f"Processing purchase: User {user.id}, Package {package.id} ({package.package_name})")

            # Update transaction status to processing
            transaction.status = "PROCESSING"
            db.session.commit()

            # Initialize IM3 package service
            im3_package = IM3Package(
                pvr_code=package.pvr_code,
                keyword=package.keyword,
                discount_price=package.discount_price,
                normal_price=package.normal_price,
                package_name=package.package_name,
                token_id=user.token_id
            )

            # Step 1: Check eligibility
            logger.info("Checking package eligibility...")
            eligibility_result = im3_package.check_eligible()

            if eligibility_result.get('status') != '0':
                error_msg = eligibility_result.get('message', 'Eligibility check failed')
                logger.error(f"Eligibility check failed: {error_msg}")
                transaction.status = "FAILED"
                db.session.commit()
                return {
                    'success': False,
                    'transaction_id': transaction_id,
                    'error': error_msg,
                    'step': 'eligibility_check'
                }

            # Get transaction ID from eligibility check
            im3_transid = eligibility_result.get('transid')
            if not im3_transid:
                logger.error("No transaction ID returned from eligibility check")
                transaction.status = "FAILED"
                db.session.commit()
                return {
                    'success': False,
                    'transaction_id': transaction_id,
                    'error': 'No transaction ID from IM3',
                    'step': 'eligibility_check'
                }

            logger.info(f"Eligibility check passed. IM3 TransID: {im3_transid}")

            # Step 2: Check eligibility status
            logger.info("Checking eligibility status...")
            status_result = im3_package.check_eligible_status(im3_transid)

            logger.info(f"Eligibility check passed. IM3 TransID: {im3_transid}")

            logger.info("Checking eligibility status with retry mechanism...")
            max_status_attempts = 5
            status_delay = 3
            status_success = False
            status_result = None

            for attempt in range(1, max_status_attempts + 1):
                logger.info(f"Status check attempt {attempt}/{max_status_attempts}")

                try:
                    status_result = im3_package.check_eligible_status(im3_transid)

                    # Log the full response for debugging
                    logger.info(f"Status check response (attempt {attempt}): {status_result}")

                    # Check if status is successful
                    # Based on your condition, we want status != '0' and 'eligibility' NOT in data
                    status_code = status_result.get('status', status_result.get('code'))
                    status_data = status_result.get('data', {})

                    # Success conditions (adjust these based on actual IM3 API responses)
                    if status_code != '0' and 'eligibility' not in str(status_data).lower():
                        logger.info(f"Status check successful on attempt {attempt}")
                        status_success = True
                        break
                    else:
                        logger.warning(
                            f"Status check not ready on attempt {attempt}: status={status_code}, data={status_data}")

                        if attempt < max_status_attempts:
                            logger.info(f"Waiting {status_delay} seconds before next attempt...")
                            time.sleep(status_delay)

                except Exception as status_error:
                    logger.warning(f"Status check attempt {attempt} failed with error: {str(status_error)}")

                    if attempt < max_status_attempts:
                        logger.info(f"Waiting {status_delay} seconds before retrying...")
                        time.sleep(status_delay)
                    else:
                        logger.error(f"All {max_status_attempts} status check attempts failed")

            # Check if status verification was successful
            if not status_success:
                error_msg = f"Status check failed after {max_status_attempts} attempts"
                if status_result:
                    error_msg += f": {status_result.get('message', 'Unknown error')}"

                logger.error(error_msg)
                transaction.status = "FAILED"
                db.session.commit()
                """return {
                    'success': False,
                    'transaction_id': transaction_id,
                    'error': error_msg,
                    'step': 'status_check',
                    'attempts_made': max_status_attempts,
                    'last_response': status_result
                }"""

            logger.info(f"Status check passed after {attempt} attempt(s)")

            # Step 3: Initiate payment
            logger.info("Initiating payment...")
            payment_result = im3_package.initiate_payment(im3_transid)

            if payment_result.get('status') != '0':
                error_msg = payment_result.get('message', 'Payment initiation failed')
                logger.error(f"Payment failed: {error_msg}")
                transaction.status = "FAILED"
                db.session.commit()
                return {
                    'success': False,
                    'transaction_id': transaction_id,
                    'error': error_msg,
                    'step': 'payment'
                }
            else:
                # Payment successful
                logger.info(payment_result)
                transaction.status = "SUCCESS"
                transaction.qr_code = payment_result['data']['SendPaymentResp']['actionData']
                db.session.commit()

                logger.info(f"Package purchase successful for transaction {transaction_id}")
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'message': 'Package purchased successfully',
                    'qr_code': payment_result['data']['SendPaymentResp']['actionData'],
                    'im3_transid': im3_transid
                }


        except Exception as e:
            logger.error(f"Package purchase failed for transaction {transaction_id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Update transaction status to failed
            try:
                transaction = Transaction.query.get(transaction_id)
                if transaction:
                    transaction.status = "FAILED"
                    db.session.commit()
            except Exception as db_error:
                logger.error(f"Failed to update transaction status: {str(db_error)}")

            # Retry the task if it's a temporary failure
            if self.request.retries < 3:
                logger.info(f"Retrying task in 60 seconds (attempt {self.request.retries + 1}/3)")
                raise self.retry(countdown=60, exc=e)

            return {
                'success': False,
                'transaction_id': transaction_id,
                'error': str(e),
                'step': 'exception'
            }

    @celery_app.task(bind=True, name='check_transaction_status', queue='package_purchases')
    def check_transaction_status_task(self, transaction_id):
        """
        Check the status of a transaction

        Args:
            transaction_id (int): ID of the transaction to check
        """
        logger.info(f"Checking status for transaction {transaction_id}")

        try:
            transaction = Transaction.query.get(transaction_id)
            if not transaction:
                return {
                    'success': False,
                    'error': 'Transaction not found'
                }

            return {
                'success': True,
                'transaction_id': transaction_id,
                'status': transaction.status,
                'qr_code': transaction.qr_code,
                'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
                'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
            }

        except Exception as e:
            logger.error(f"Failed to check transaction status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    return purchase_package_task, check_transaction_status_task