from im3 import api_service
from . import profile


class Package:
    def __init__(self, pvr_code, keyword, discount_price, normal_price, package_name, token_id):
        self.api_service_instance = api_service.IMIOAuthHelper("Android", "82.5.1", token_id)
        self.phone_number = "62" + profile.Profile(token_id).get_profile()
        self.pvr_code = pvr_code.replace("$MSISDN$", self.phone_number)
        self.keyword = keyword
        self.discount_price = discount_price
        self.normal_price = normal_price
        self.package_name = package_name

    def check_eligible(self):
        check_eligible_payload = {
            "billaccount": "",
            "discountprice": self.discount_price,
            "keyword": self.keyword,
            "name": "",
            "normalprice": self.normal_price,
            "offerid": self.pvr_code,
            "operationtype": "buy",  # buy/gift
            "packagename": self.package_name,
            "paymentchannel": "QRIS",
            "shortcode": "",
            "tomsisdn": self.phone_number,
            "transid": "",
            "transtype": "cvm",
            "validity": "",
            "walletmsisdn": ""
        }
        return self.api_service_instance.send_request("api/v2/cvm/checkeligible", check_eligible_payload,
                                                      rc4_status=True)

    def check_eligible_status(self, transid):
        return self.api_service_instance.send_request("api/v2/esb/checkeligiblestatus", {"transid": transid})

    def initiate_payment(self, transid):
        initiate_payment_payload = {
            "balancereceive": 0.0,
            "validity": "",
            "discountprice": self.discount_price,
            "due": 0.0,
            "duedate": "",
            "keyword": self.keyword,
            "name": "",
            "normalprice": self.normal_price,
            "offerid": self.pvr_code,
            "operationtype": "buy",
            "packagename": self.package_name,
            "paymentchannel": "QRIS",
            "shortcode": "",
            "tomsisdn": self.phone_number,
            "transid": transid,
            "transtype": "cvm",
            "walletmsisdn": ""
        }
        return self.api_service_instance.send_request("api/v2/esb/initiatepayment", initiate_payment_payload)
