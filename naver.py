import hashlib
import hmac
import base64
import time
import requests


class Naver:
    BASE_URL = 'https://api.naver.com'
    API_KEY = ''
    CUSTOMER_ID = ''
    SECRET_KEY = ''

    @staticmethod
    def generate_signature(timestamp, method, url):
        message = "{}.{}.{}".format(timestamp, method, url)
        hash = hmac.new(bytes(Naver.SECRET_KEY, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)

        hash.hexdigest()
        return base64.b64encode(hash.digest())

    @staticmethod
    def call_api(method, url, payload):
        timestamp = str(round(time.time() * 1000))
        signature = Naver.generate_signature(timestamp, method, url)
        headers = {
            'X-Timestamp': timestamp,
            'X-API-KEY': Naver.API_KEY,
            'X-Customer': Naver.CUSTOMER_ID,
            'X-Signature': signature,
        }

        response = requests.get(f'{Naver.BASE_URL}{url}', params=payload, headers=headers)

        return response.json()
