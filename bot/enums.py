from datetime import datetime
from enum import IntEnum, auto
from dataclasses import dataclass

class PaymentEnum(IntEnum):
    successfully = auto()
    not_enough_funds  = auto()
    free_checks_over  = auto()

@dataclass
class DataCreatePayment:
    order_id: str
    payment_id: str
    amount: float
    payment_page_url: str

@dataclass
class DataStatusPayment:
    order_id: str
    amount: float
    status: str
    is_paid: bool
    created_date: datetime