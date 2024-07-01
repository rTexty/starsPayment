from contextlib import suppress
from pydantic.error_wrappers import ValidationError

from aiogram import F, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.exceptions import TelegramBadRequest

from . import router
from ... import markups
from ...state import GetUserState
from ...callback_data import ActionsWithUser
from ...services.database.models import BotUser


@router.callback_query(F.data =='admin_get_user')
async def get_user_info(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(GetUserState.waiting_user_id)
    await call.message.edit_text(_('Пришлите id или username пользователя'), reply_markup=markups.back_admin())

@router.message(F.text, GetUserState.waiting_user_id)
async def admin_get_user(message: types.Message, state: FSMContext):
    await state.clear()
    await send_user_text(message, message.text)


async def send_user_text(message: types.Message, text: str):
    user = await BotUser.get_user(text)

    if not user:
        return message.answer(_('Пользователь не найден 🙁'), reply_markup=await markups.admin_panel())
    
    await user.fetch_related('metric')
    count_ref = await BotUser.filter(referrer=user).count()

    lst_bool = [_('Нет'), _('Да'),]

    text = _(
        'ID: {}\nUsername: {}\nДоступно проверок: {}\nБесплатных проверок: {}\nРефералов: {}\nМетрика: {}\nРеферер: {}\nАктивный: {}\nДата регистрации: {}\n'
    ).format(
        user.id, user.url, user.available_checks, user.free_checks, count_ref, getattr(user.metric, "code",
        lst_bool[0]), user.referrer_id or lst_bool[0], lst_bool[user.active],
        user.time_reg.strftime("%m.%d.%Y %H:%M")
    )

    if message.from_user.is_bot:
        await message.edit_text(text, reply_markup=markups.actions_with_user(user))
    else:
        await message.answer(text, reply_markup=markups.actions_with_user(user))

@router.callback_query(ActionsWithUser.filter())
async def work_with_user(call: types.CallbackQuery, callback_data: ActionsWithUser, bot: Bot, state: FSMContext):
    user = await BotUser.get_user(callback_data.user_id)

    if not user:
        return call.message.answer(_('Пользователь не найден'))

    if callback_data.action == 'admin':
        user.admin = not user.admin

    elif callback_data.action == 'ban':
        user.is_banned = not user.is_banned

    elif callback_data.action == 'del':
        return call.message.answer(
            _('Вы действительно хотите удалить пользователя?'),
            reply_markup=markups.question_delete_entity(user.id, 'user')
        )
    
    elif callback_data.action == 'edit_balance':
        await state.set_state(GetUserState.waiting_amount)
        await state.update_data(user=user)
        return await call.message.edit_text(_(
            'Введите кол-во проверок со знаком "+" или "-"\nПример: +100'),
            reply_markup=markups.back_admin())
    
    await user.save()

    with suppress(TelegramBadRequest, ValidationError):
        await bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id,
            reply_markup=markups.actions_with_user(user)
        )


@router.message(F.text, GetUserState.waiting_amount, flags={'del_markup': True})
async def admin_edit_balane(message: types.Message, state: FSMContext):
    try:
        sign, checks = message.text[0], int(message.text[1:])

        user: BotUser = (await state.get_data())['user']

        if sign == '-':
            user.available_checks = user.available_checks - checks
        if sign == '+':
            user.available_checks = user.available_checks + checks
        
        await user.save()
        await send_user_text(message, user.id)

    except:
        return await message.answer(
            '⚠️ Не правильный формат ввода',
            reply_markup=markups.back_admin()
        )
        