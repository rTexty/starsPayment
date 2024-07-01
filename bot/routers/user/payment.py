import asyncio
from datetime import datetime, timedelta
import logging
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from bot import markups
from bot.callback_data import PaymentCallbackData
from bot.enums import DataCreatePayment
from bot.payments.AbstractPayment import AbstractPayment
from bot.services.schedule import ScheduleService

from . import router
from ...services.database.models import BotUser, Payment, Settings
from aiogram.filters import Command
from ...utils.bot import Bot
from bot.bot import onevisionpay, bot, wallet_pay


logger = logging.getLogger(__name__)


@router.message(Command('payment'))
async def msg_payment(message: types.Message, edit=False):
     text = '✳️ Оплата выбранного пакета проверок будет проводиться через кошелек Wallet Pay'
     if edit:
         await message.edit_text(text, reply_markup=markups.price_list)
     else:
         await message.answer(text, reply_markup=markups.price_list)

@router.callback_query(F.data == 'payment')
async def call_help(call: types.CallbackQuery, bot: Bot):
     await msg_payment(call.message, edit=True)


@router.callback_query(PaymentCallbackData.filter())
async def call_help(call: types.CallbackQuery, callback_data: PaymentCallbackData, bot_user: BotUser):
     course = (await Settings.get(name='course')).float_value
     payment_class = await Settings.get_payment_class()

     payment = await payment_class.create_payment(
          callback_data.amount * course, callback_data.checks, bot_user.id
     )
     await call.message.edit_reply_markup(reply_markup=markups.payment_link(payment.payment_page_url))

     await Payment.create(id=payment.order_id, payment_id=payment.payment_id, amount=payment.amount, checks=callback_data.checks, user=bot_user)
     asyncio.create_task(check_status_payment(payment))

async def check_status_payment(payment: DataCreatePayment):
     payment_class = await Settings.get_payment_class()

     while True:
          payment_status = await payment_class.payment_status(payment.payment_id)
          
          payment_db = await Payment.get(id=payment.order_id).prefetch_related('user')
          payment_db.status = payment_status.status
          await payment_db.save()

          logger.info(f'Check Payment={payment_db.id}, User={payment_db.user_id}, Status={payment_db.status}')
          if payment_status.is_paid:
               payment_db.user.available_checks = payment_db.user.available_checks + payment_db.checks
               await payment_db.user.save()
               await bot.send_message(payment_db.user_id, f'✅ Успешно пополнено\nДоступно {payment_db.user.get_available_checks}')
               break

          new_date_time_obj = payment_status.created_date + timedelta(minutes=35)
          current_time = datetime.now(payment_status.created_date.tzinfo)
          if current_time > new_date_time_obj:
               payment_db.status = 'time_up'
               await payment_db.save()
               await bot.send_message(payment_db.user_id, '⚠️ Время платежа истекло. Перезапустите бота /start')
               return

          await asyncio.sleep(10)
