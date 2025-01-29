from time import sleep

from database import db
from im3.repository.package import Package as PackageRepository
from models.package import Package
from models.user import User
from models.transaction import Transaction
from app import celery, app


@celery.task(name='tasks.package_transaction.purchase_package', max_retries=3)
def purchase_package(user_id, package_id):
    with app.app_context():
        me = User.query.filter_by(id=user_id).first()
        if me.token_id is None:
            return "USER_NOT_LOGGED_IN"
        else:
            package = Package.query.filter_by(id=package_id).first()
            if package is None:
                return "PACKAGE_NOT_FOUND"
            else:
                im3package = PackageRepository(
                    pvr_code=package.pvr_code,
                    keyword=package.keyword,
                    discount_price=package.discount_price,
                    normal_price=package.normal_price,
                    package_name=package.package_name,
                    token_id=me.token_id
                )
                transaction = Transaction(
                    user_id=me.id,
                    package_id=package.id,
                )
                db.session.add(transaction)
                db.session.commit()
                check_eligible = im3package.check_eligible()
                if check_eligible["status"] != "0":
                    transaction.status = "FAILED_TO_CHECK_PACKAGE_ELIGIBILITY"
                    db.session.commit()
                    return "FAILED_TO_CHECK_PACKAGE_ELIGIBILITY"
                else:
                    for _ in range(6):
                        check_eligible_status = im3package.check_eligible_status(check_eligible["transid"])
                        if check_eligible_status["status"] == "0" and "eligibility" in check_eligible_status["data"]:
                            break
                        sleep(2)
                    else:
                        transaction.status = "PACKAGE_MIGHT_NOT_BE_ELIGIBLE_TO_BUY"
                        db.session.commit()
                        # return "PACKAGE_MIGHT_NOT_BE_ELIGIBLE_TO_BUY"
                    initiate_payment = im3package.initiate_payment(check_eligible["transid"])
                    if initiate_payment["status"] != "0":
                        transaction.status = "FAILED_TO_INITIATE_PAYMENT"
                        db.session.commit()
                        return "FAILED_TO_INITIATE_PAYMENT"
                    else:
                        qr_code = initiate_payment['data']['SendPaymentResp']['actionData']
                        transaction.qr_code = qr_code
                        transaction.status = "PAYMENT_INITIATED_SUCCESSFULLY"
                        db.session.commit()
                        return "PAYMENT_INITIATED_SUCCESSFULLY"
