from datetime import datetime
import logging
import uuid
import aiohttp
import json
import base64
import hmac
import hashlib

from bot.enums import DataCreatePayment, DataStatusPayment
from bot.payments.AbstractPayment import AbstractPayment
logger = logging.getLogger(__name__)

class Onevisionpay(AbstractPayment):
    def __init__(self, api_key, secret_key, merchant_id, service_id):
        pass

    async def _send_request(self, url, data):
        pass

    async def create_payment(self, amount: float, checks: int, user_id: int) -> DataCreatePayment:
        pass

    async def payment_status(self, payment_id: str) -> DataStatusPayment:
        pass
