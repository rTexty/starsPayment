
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from bot import markups

from ..utils.router import Router
from . import root_handlers_router
from aiogram.utils.i18n import gettext as _
from ..services.database.models import BotUser
from ..utils.bot import Bot

router = Router()
root_handlers_router.include_router(router)

@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext, bot_user: BotUser, bot: Bot, is_new_user: bool, edit=False):
    await state.clear()

    me = await bot.me()

    # if is_new_user:
        # bot_user.available_checks = 3
        # await bot_user.save(update_fields=['available_checks'])

    text = f'Привет! Я - @{me.username}'

    if edit:
        await message.edit_text(text, reply_markup=await markups.main_markup())
    else:
        await message.answer(text, reply_markup=await markups.main_markup())

@router.callback_query(F.data == 'start')
async def call_help(call: types.CallbackQuery, state: FSMContext, bot_user: BotUser, bot: Bot, is_new_user: bool):
    await start_handler(call.message, state, bot_user, bot, is_new_user=False, edit=True)
