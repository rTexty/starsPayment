import io
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from bot.services.database.models import BotUser, Payment

from . import router

from aiogram.types import BufferedInputFile
from openpyxl import Workbook

@router.callback_query(F.data =='admin_get_excel')
async def get_user_info(call: types.CallbackQuery, state: FSMContext):
    bot_users = await BotUser.all()
    file = create_excel_user(bot_users)
    input_file = BufferedInputFile(file.getvalue(), 'bot_users.xlsx')
    await call.message.answer_document(input_file)

@router.callback_query(F.data =='admin_get_payments')
async def get_user_info(call: types.CallbackQuery, state: FSMContext):
    payments = await Payment.all()
    file = create_excel_payments(payments)
    input_file = BufferedInputFile(file.getvalue(), 'payments.xlsx')
    await call.message.answer_document(input_file)
        
def create_excel_user(data: list[BotUser]):
    wb = Workbook()
    ws = wb.active
    
    ws.append(['Telegram ID', 'username', 'Проверок', 'Бесплатных проверок', 'Имеет ли доступ админа',
               'Активный', 'Забанен', 'Время регистрации'
              ])

    for user in data:
        ws.append(
            [
                user.id, user.username, user.available_checks, user.free_checks, user.admin,
                user.active, user.is_banned, user.time_reg.strftime('%H:%M:%S %d.%m/.Y')
            ]
        )
    file = io.BytesIO()
    wb.save(file)
    return file


def create_excel_payments(data: list[Payment]):
    wb = Workbook()
    ws = wb.active
    
    ws.append(['ID', 'ID в платежке', 'Сумма', 'Проверок', 'Пользователь', 'Статус'])

    for payment in data:
        ws.append(
            [payment.id, payment.payment_id, payment.amount, payment.checks, payment.user_id, payment.status]
        )
    file = io.BytesIO()
    wb.save(file)
    return file