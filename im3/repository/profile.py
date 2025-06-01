from im3 import api_service


class Profile:
    def __init__(self, token_id, debug=False):
        self.api_service_instance = api_service.IMIOAuthHelper("Android", "82.5.1", token_id, debug=debug)

    def get_profile(self):
        return self.api_service_instance.send_request("api/v2/profile/get", {})

    def get_dashboard(self):
        return self.api_service_instance.send_request("api/v2/dashboard/get/v4", {})