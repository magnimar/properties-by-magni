import hmac
import hashlib
import base64
import time
import requests
import json
import os
import secrets
import string
from dotenv import load_dotenv

load_dotenv("/opt/properties-by-magni/.env")

RAPYD_ACCESS_KEY = os.getenv("RAPYD_ACCESS_KEY")
RAPYD_SECRET_KEY = os.getenv("RAPYD_SECRET_KEY")
RAPYD_BASE_URL = os.getenv("RAPYD_BASE_URL", "https://sandboxapi.rapyd.net")

class RapydService:
    @staticmethod
    def _generate_salt(length=12):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

    @staticmethod
    def _get_signature(http_method, path, salt, timestamp, body):
        body_str = json.dumps(body, separators=(',', ':'), ensure_ascii=False) if body else ''
        if body_str == '{}':
            body_str = ''
            
        sig_string = (
            http_method.lower() +
            path +
            salt +
            str(timestamp) +
            RAPYD_ACCESS_KEY +
            RAPYD_SECRET_KEY +
            body_str
        )

        hash_object = hmac.new(
            RAPYD_SECRET_KEY.encode('utf-8'),
            sig_string.encode('utf-8'),
            hashlib.sha256
        )
        
        signature = base64.b64encode(hash_object.hexdigest().encode('utf-8')).decode('utf-8')
        return signature

    @classmethod
    def make_request(cls, http_method, path, body=None):
        salt = cls._generate_salt()
        timestamp = int(time.time())
        signature = cls._get_signature(http_method, path, salt, timestamp, body)

        headers = {
            'access_key': RAPYD_ACCESS_KEY,
            'salt': salt,
            'timestamp': str(timestamp),
            'signature': signature,
            'Content-Type': 'application/json'
        }

        url = f"{RAPYD_BASE_URL}{path}"
        body_str = json.dumps(body, separators=(',', ':'), ensure_ascii=False) if body else ''

        if http_method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif http_method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=body_str)
        else:
            raise ValueError(f"Unsupported HTTP method: {http_method}")

        return response.json()

    @classmethod
    def create_customer(cls, email, name=None):
        path = '/v1/customers'
        body = {
            'email': email,
            'name': name or email
        }
        return cls.make_request('POST', path, body)

    @classmethod
    def create_product(cls, name, product_type='service', description=None):
        path = '/v1/products'
        body = {
            'name': name,
            'type': product_type,
        }
        if description:
            body['description'] = description
        return cls.make_request('POST', path, body)

    @classmethod
    def create_plan(cls, product_id, amount, currency, interval='month',
                    interval_count=1, nickname=None):
        path = '/v1/plans'
        body = {
            'product': product_id,
            'currency': currency,
            'interval': interval,
            'interval_count': interval_count,
            'billing_scheme': 'per_unit',
            'amount': amount,
            'usage_type': 'licensed',
        }
        if nickname:
            body['nickname'] = nickname
        return cls.make_request('POST', path, body)

    @classmethod
    def create_checkout_page(cls, customer_id, plan_id, amount, complete_url,
                             cancel_url, country='IS', currency='ISK'):
        path = '/v1/checkout'
        body = {
            'customer': customer_id,
            'country': country,
            'currency': currency,
            'amount': amount,
            'subscription_items': [
                {'plan': plan_id, 'quantity': 1}
            ],
            'complete_checkout_url': complete_url,
            'cancel_checkout_url': cancel_url,
        }
        return cls.make_request('POST', path, body)
