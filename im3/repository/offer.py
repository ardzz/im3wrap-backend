from im3 import api_service


class Offer:
    def __init__(self, token_id, debug=False):
        self.api_service_instance = api_service.IMIOAuthHelper("Android", "82.5.1", token_id, debug=debug)

    def get_list(self, source_id = 0):
        return self.api_service_instance.send_request("api/v2/offer/getlist", {"sourceid": source_id})

    def get_superhemat(self, source_id=0):
        return self.api_service_instance.send_request("api/v2/offer/superhemat", {"sourceid": source_id})

    def get_flashsale(self, source_id=0):
        return self.api_service_instance.send_request("api/v2/offer/flashsale?ruleid=FLASHSALE", {"sourceid": source_id})