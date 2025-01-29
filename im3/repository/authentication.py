from im3 import IMIOAuthHelper


class Authentication:
    def __init__(self, phone_number, debug=False):
        token_id = IMIOAuthHelper.get_values(IMIOAuthHelper.make_imi_uid())
        self.api_service_instance = IMIOAuthHelper("Android", "82.5.1", token_id, debug=debug)
        self.phone_number = self.parse_number(phone_number)

    def send_otp(self):
        return self.api_service_instance.send_request("api/v2/otp/send/v1",{"msisdn": self.phone_number, "action": "register"})

    def verify_otp(self, transid, code):
        return self.api_service_instance.send_request("api/v2/otp/validate/v1", {"transid":transid,"otp":str(code)})

    @staticmethod
    def parse_number(number):
        if number.startswith("0"):
            return "62" + number[1:]
        elif number.startswith("8"):
            return "628" + number[1:]
        else:
            return number
