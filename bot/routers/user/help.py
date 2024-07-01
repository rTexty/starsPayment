from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from bot import markups

from . import router
from ...services.database.models import BotUser
from aiogram.filters import Command
from ...utils.bot import Bot

@router.message(Command('help'))
async def msg_help(message: types.Message, bot: Bot, edit=False):
     me = await bot.me()
     text = '''Привет! Я - @{}.'''.format(me.username)
     
     if edit:
         await message.edit_text(text, reply_markup=markups.back_to_start)
     else:
         await message.answer(text, reply_markup=markups.back_to_start)

@router.callback_query(F.data == 'help')
async def call_help(call: types.CallbackQuery, bot: Bot):
     await msg_help(call.message, bot, edit=True)
