from abc import ABC, abstractmethod

from bot.enums import DataCreatePayment, DataStatusPayment

class AbstractPayment(ABC):
        
    @abstractmethod
    async def _send_request(self, method: str, url: str, data: dict):
        pass

    @abstractmethod
    async def create_payment(self, amount: float, checks: int, user_id: int) -> DataCreatePayment:
        pass

    @abstractmethod
    async def payment_status(self, order_id: str) -> DataStatusPayment:
        pass