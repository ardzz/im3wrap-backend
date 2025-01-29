import hashlib
import json
import time

import httpx
import urllib3

from .utils import rc4

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IMIOAuthHelper:
    def __init__(self, app_os: str, version: str, token_id: str, debug: bool = False):
        self.app_os = app_os
        self.version = version
        self.token_id = token_id
        self.debug = debug

    @staticmethod
    def get_values(id_str: str) -> str:
        if not id_str:
            raise ValueError("id cannot be None or empty")

        result = [id_str[i] for i in range(len(id_str)) if (i + 1) % 2 != 0]
        return ''.join(result)

    def make_x_imi_oauth(self, request_body: dict, rc4_operator: bool = False) -> str:
        if rc4_operator:
            RC4 = rc4.ODPRC4("INDOSAT2798")
            req_body = RC4.encrypt(json.dumps(request_body, separators=(',', ':')))
        else:
            req_body = json.dumps(request_body, separators=(',', ':'))
        salt = self.get_values(self.token_id)
        input_string = f"REQBODY={req_body}&SALT={salt}"
        return hashlib.sha512(input_string.encode()).hexdigest()

    @staticmethod
    def make_imi_uid() -> str:
        return str(int(time.time() * 1000))

    def make_x_imi_hash(self, req_time: str) -> str:
        salt = self.get_values(req_time)
        hashable = f"parent${self.app_os}${self.version}${self.token_id}&SALT={salt}"
        return hashlib.sha512(hashable.encode()).hexdigest()

    def send_request(self, endpoint: str, request_body: dict, rc4_status: bool = False) -> object:
        x_imi_uid = self.make_imi_uid()
        RC4 = rc4.ODPRC4("INDOSAT2798")
        headers = {
            "Host": "myim3api1.ioh.co.id",
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; SM-N976N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36",
            "Authorization": "642d1cc69d90666962726e",
            "X-Imi-App-Oem": "samsung",
            "X-Imi-App-Model": "SM-N976N",
            "X-Imi-App-Os": "Android",
            "X-Imi-Channel": "V2MYIM3",
            "X-Imi-Servicekey": "i4WxFMMLvWqnrvuAyg58",
            "X-Imi-App-Osversion": "7.1.2",
            "X-Imi-Version": "82.5.1",
            "X-Imi-Versioncode": "560003678",
            "X-Deviceid": "b29a9816e1229d9a",
            "X-Devicename": "SM-G977N",
            "X-Imi-Adid": "0ad68471-370c-4024-9afe-2d320234151c",
            "X-Imi-Adid-Islimited": "false",
            "X-Imi-Language": "EN",
            "X-Low-Quota": "NO",
            "X-Sptravel": "NO",
            "X-Imi-Uid": x_imi_uid,
            "X-Imi-Network": "Mobile",
            "X-Imi-Hash": self.make_x_imi_hash(x_imi_uid),
            "X-Imi-Tokenid": self.token_id,
            "X-Imi-Oauth": self.make_x_imi_oauth(request_body, rc4_operator=rc4_status),
            "Content-Type": "application/json",
        }
        json_request_body = json.dumps(request_body, separators=(',', ':'))

        with httpx.Client(verify=False, http2=True) as client:
            if not rc4_status:
                response = client.post(f"https://myim3api1.ioh.co.id/{endpoint}", headers=headers, data=json_request_body)
            else:
                response = client.post(f"https://myim3api1.ioh.co.id/{endpoint}", headers=headers, data=RC4.encrypt(json_request_body))
        """if not rc4_status:
            response = httpx.post(f"https://myim3api1.ioh.co.id/{endpoint}", headers=headers, 
                                     data=json_request_body, verify=False, proxies={"https": "http://127.0.0.1:8080"} if self.debug else None)
        else:
            response = httpx.post(f"https://myim3api1.ioh.co.id/{endpoint}", headers=headers,
                                     data=RC4.encrypt(json_request_body), verify=False, proxies={"https": "http://127.0.0.1:8080"} if self.debug else None)
                                     """
        return response.json()
