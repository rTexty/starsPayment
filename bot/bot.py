from aiogram.fsm.storage.memory import MemoryStorage

from bot.payments.onevisionpay import Onevisionpay
from bot.payments.wallet_pay import WalletPay


from .models.config.bot_config import BotConfig
from .utils.bot import Bot
from .utils.dispatcher import Dispatcher


bot = Bot(BotConfig.load_first(), parse_mode="html")
dispatcher = Dispatcher(storage=MemoryStorage())
onevisionpay = Onevisionpay(
    bot.config.payment_api_key, bot.config.payment_secret_key,
    bot.config.merchant_id, bot.config.service_id
)

wallet_pay = WalletPay(bot.config.wallet_pay_api_key)
