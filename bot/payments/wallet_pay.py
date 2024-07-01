from datetime import datetime
import logging
import uuid
import aiohttp
import pytz

from bot.enums import DataCreatePayment, DataStatusPayment
from bot.payments.AbstractPayment import AbstractPayment

logger = logging.getLogger(__name__)

class WalletPay(AbstractPayment):
    def __init__(self, api_key):
        pass

    async def _send_request(self, method, url, data):
        pass

    async def create_payment(self, amount: float, checks: int, user_id: int) -> DataCreatePayment:
        pass

    async def payment_status(self, order_id: str) -> DataStatusPayment:
        pass
