from aiogram import types
from aiogram.utils.i18n import gettext as _
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, WebAppInfo

from .services.database.models import BotUser, Settings
from .callback_data import ActionsWithUser, DeleteCallbackData, PaymentCallbackData, StarsPaymentCallbackData


remove_markup = types.ReplyKeyboardRemove(remove_keyboard=True)
symbols = ['❌', '✅']

async def admin_panel():
    affiliate_program = await Settings.get(name='affiliate_program')
    pdf_format = await Settings.get(name='pdf_format')
    payment_method = await Settings.get(name='payment_method')
    return (
        InlineKeyboardBuilder()
        .button(text=_('📨 Рассылка'), callback_data='admin_mailing')
        .button(text=_('📈 Статистика'), callback_data='admin_statistics')
        .button(text=_('👤 Пользователи'), callback_data='admin_get_user')
        .button(text=_('💳 Платежи'), callback_data='admin_get_payments')
        .button(text=_('📄 Excel'), callback_data='admin_get_excel')
        .button(text=f'{symbols[affiliate_program.bool_value]} Партнерка', callback_data='affiliate_program')
        .button(text=f'{symbols[pdf_format.bool_value]} PDF Формат', callback_data='pdf_format')
        .button(text=f'{symbols[payment_method.bool_value]} Wallet Pay', callback_data='payment_method')
        .adjust(2, repeat=True)
        .as_markup()
    )

def actions_with_user(user: BotUser):
    markup = (
        InlineKeyboardBuilder()
        .button(text=_('{} Админ').format(symbols[user.admin]), callback_data=ActionsWithUser(user_id=user.id, action='admin').pack())
        .button(text=_('{} Забанен').format(symbols[user.is_banned]), callback_data=ActionsWithUser(user_id=user.id, action='ban').pack())
        .button(text=_('💳 Изменить баланс'), callback_data=ActionsWithUser(user_id=user.id, action='edit_balance').pack())
        .button(text=_('🗑 Удалить с базы'), callback_data=ActionsWithUser(user_id=user.id, action='del').pack())
        .button(text=_('◀️ Назад'), callback_data='back_admin')
        .adjust(2, repeat=True)
        .as_markup()
    )
    return markup

def question_delete_entity(entity_id: int, type_entity: str):
    markup = (
    InlineKeyboardBuilder()
        .button(text=f'✅', callback_data=DeleteCallbackData(id=entity_id, type_entity=type_entity).pack())
        .button(text=f'❌', callback_data=DeleteCallbackData(id=entity_id, type_entity='back').pack())
        .adjust(2, repeat=True)
        .as_markup()
    )
    return markup

def sending_keyboard():
    return (
        InlineKeyboardBuilder()
        .button(text=_('👥 Отправить всем'), callback_data='everyone')
        .button(text=_('👤 Отправить одному'), callback_data='one')
        .button(text=_('❌ Отменить'), callback_data='cancel')
        .adjust(2, repeat=True)
        .as_markup()
    )

def add_metric():
    return (
        InlineKeyboardBuilder()
        .button(text=_('➕ Добавить метрику'), callback_data='add_metric')
        .button(text=_('🗑 Удалить метрику'), callback_data='del_metric')
        .button(text=_('◀️ Назад'), callback_data='back_admin')
        .adjust(2, repeat=True)
        .as_markup()
    )

def back_admin():
    return (
        InlineKeyboardBuilder()
        .button(text=_('◀️ Назад'), callback_data='back_admin')
        .adjust(1, repeat=True)
        .as_markup()
    )

def report_link(link: str):
    return (
        InlineKeyboardBuilder()
        .button(text='📑 Посмотреть отчет', url=link)
        .adjust(1, repeat=True)
        .as_markup()
    )

async def main_markup():
    ap = await Settings.get(name='affiliate_program')
                            
    main_markup = (
        InlineKeyboardBuilder()
        .button(text='💡 Помощь', callback_data='help')
        .button(text='💳 Оплата', callback_data='payment')
    )
    if ap.bool_value:
        main_markup.button(text='🤝 Реферальная программа', callback_data='friends')
    return main_markup.adjust(2, repeat=True).as_markup()



payment = (
    InlineKeyboardBuilder()
    .button(text='💳 Оплата', callback_data='payment')
    .adjust(1, repeat=True)
    .as_markup()
)

price_list = (
    InlineKeyboardBuilder()
    .button(text='1 проверка - $2,2', callback_data=PaymentCallbackData(checks=1, amount=2.2).pack())
    .button(text='10 проверок - $20', callback_data=PaymentCallbackData(checks=10, amount=20).pack())
    .button(text='25 проверок - $48', callback_data=PaymentCallbackData(checks=25, amount=48).pack())
    .button(text='50 проверок - $90', callback_data=PaymentCallbackData(checks=50, amount=90).pack())
    .button(text='100 проверок - $170', callback_data=PaymentCallbackData(checks=100, amount=170).pack())
    .button(text='1000 проверок - $1 600', callback_data=PaymentCallbackData(checks=1000, amount=1600).pack())
    .button(text='5000 проверок - $7 500', callback_data=PaymentCallbackData(checks=5000, amount=7500).pack())
    .button(text='◀️ Назад', callback_data='start')
    .adjust(1, repeat=True)
    .as_markup()
)

def payment_link(url: str):
    if 't.me' in url:
        r = InlineKeyboardBuilder().button(text='💳 Оплатить', web_app=WebAppInfo(url=url))

    r = InlineKeyboardBuilder().button(text='💳 Оплатить', url=url)
    
    return r.adjust(1, repeat=True).as_markup()

back_to_start = (
    InlineKeyboardBuilder()
    .button(text='◀️ Назад', callback_data='start')
    .adjust(1, repeat=True)
    .as_markup()
)

def example_reply():
    return (
        ReplyKeyboardBuilder()
        .button(text='First bnt')
        .button(text='Second bnt')
        .adjust(2, repeat=True)
        .as_markup(is_persistent=True, resize_keyboard=True)
    )

stars_payment_keyboard = (
    InlineKeyboardBuilder()
    .button(text='1 проверка - 93 ⭐️', callback_data=StarsPaymentCallbackData(checks=1, amount=93).pack(), pay=True)
    .button(text='10 проверок - 844 ⭐️', callback_data=StarsPaymentCallbackData(checks=10, amount=844).pack(), pay=True)
    .button(text='25 проверок - 2026 ⭐️', callback_data=StarsPaymentCallbackData(checks=25, amount=2026).pack(), pay=True)
    .button(text='50 проверок - 3799 ⭐️', callback_data=StarsPaymentCallbackData(checks=50, amount=3799).pack(), pay=True)
    .button(text='100 проверок - 7177 ⭐️', callback_data=StarsPaymentCallbackData(checks=100, amount=7177).pack(), pay=True)
    .button(text='1000 проверок - 67546 ⭐️', callback_data=StarsPaymentCallbackData(checks=1000, amount=67546).pack(), pay=True)
    .button(text='5000 проверок - 316623 ⭐️', callback_data=StarsPaymentCallbackData(checks=5000, amount=316623).pack(), pay=True)
    .button(text='◀️ Назад', callback_data='start')
    .adjust(1, repeat=True)
    .as_markup()
)

select_payment_method = (
    InlineKeyboardBuilder()
    .button(text='Wallet Pay', callback_data='wallet_pay_method')
    .button(text='Stars ⭐️', callback_data='stars_method')
    .adjust(1, repeat=True)
    .as_markup()
)

def confirmation_stars_def(amount: int):
    # Создаем кнопки
    pay_button = InlineKeyboardButton(text=f'✅ Оплатить {amount}⭐️', pay=True)
    back_button = InlineKeyboardButton(text='❌ Назад', callback_data='stars_payment_cancel')

    # Создаем клавиатуру и добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [pay_button],  # Кнопка в первом ряду
        [back_button]  # Кнопка во втором ряду
    ])

    return keyboard
