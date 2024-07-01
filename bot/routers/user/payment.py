import asyncio
from datetime import datetime, timedelta
import logging
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.types import LabeledPrice, Message, SuccessfulPayment

from bot import markups
from bot.callback_data import PaymentCallbackData, StarsPaymentCallbackData
from bot.enums import DataCreatePayment
from bot.payments.AbstractPayment import AbstractPayment
from bot.services.schedule import ScheduleService
from bot.markups import confirmation_stars_def

from bot.state import PaymentState
from . import router
from ...services.database.models import BotUser, Payment, Settings
from aiogram.filters import Command
from ...utils.bot import Bot
from bot.bot import onevisionpay, bot, wallet_pay


logger = logging.getLogger(__name__)


@router.message(Command('payment'))
async def select_payment_method(message: types.Message, edit=False):
    text = 'Выберите способ оплаты Wallet Pay или Stars ⭐️'
    if edit:
          await message.edit_text(text, reply_markup=markups.select_payment_method)
    else:
          await message.answer(text, reply_markup=markups.select_payment_method)

@router.callback_query(F.data == 'payment')
async def call_help(call: types.CallbackQuery, bot: Bot):
     await select_payment_method(call.message, edit=True)


@router.callback_query(F.data == 'wallet_pay_method')
async def payment_version_1(call: types.CallbackQuery, ):
     text = '✳️ Оплата выбранного пакета проверок будет проводиться через кошелек Wallet Pay'
     await call.message.edit_text(text, reply_markup=markups.price_list)


@router.callback_query(F.data == 'stars_method')
async def payment_version_2(call: types.CallbackQuery,):
     text = '✳️ Оплата выбранного пакета проверок будет проводиться с помощью телеграмм-валюты Stars ⭐️'
     await call.message.edit_text(text, reply_markup=markups.stars_payment_keyboard)


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

@router.callback_query(StarsPaymentCallbackData.filter())
async def stars_payment_create(call: types.CallbackQuery, 
                               callback_data: StarsPaymentCallbackData, 
                               bot_user: BotUser, 
                               bot: Bot,
                               state: FSMContext):
    prices = [LabeledPrice(label='XTR', amount=callback_data.amount)]
    keyboard = confirmation_stars_def(amount=callback_data.amount)
    logger.info = f'User {call.from_user.id} selected STARS payment'
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="⭐️Stars Payment⭐️",
        description="Подтвердите оплату ⭐️",
        prices=prices,
        provider_token="your_provider_token",  # Укажите ваш провайдер токен
        payload="product",
        currency="XTR",
        reply_markup=keyboard,
    )

    await state.set_state(PaymentState.START)
    await state.update_data(amount = callback_data.amount,
                            checks = callback_data.checks)



@router.callback_query(F.data == 'stars_payment_cancel')
async def cancel_payment(call: types.CallbackQuery):
    await call.message.delete()

@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@router.message(F.successful_payment,)
async def payment_status(message: Message, state: PaymentState.START, bot_user: BotUser, bot: Bot):
     payment_id = message.successful_payment.telegram_payment_charge_id
     data = await state.get_data()
     amount = data.get('amount')
     checks = data.get('checks')
     if amount and checks:
          await Payment.create(
               id=payment_id,
               payment_id=payment_id,
               amount=amount,
               checks = checks,
               user = bot_user,
          )
     else: 
          await Bot.refund_star_payment(
               self=bot,
               user_id= message.from_user.id,
               telegram_payment_charge_id=payment_id
          )
     await message.answer('✅ Спасибо за оплату!')
     logger.info(f'Check Payment={payment_id}, User={message.from_user.id},')

     payment_db = await Payment.get(id=payment_id).prefetch_related('user')
     payment_db.user.available_checks += checks
     await payment_db.user.save()
     await bot.send_message(payment_db.user_id, f'✅ Успешно пополнено\nДоступно {payment_db.user.get_available_checks}')

    # Очистка платежа из состояния
     await state.update_data(amount=None, checks=None)

     await state.set_state(None)

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
