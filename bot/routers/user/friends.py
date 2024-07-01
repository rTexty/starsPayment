from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

from bot import markups

from . import router
from ...services.database.models import BotUser
from aiogram.filters import Command
from aiogram.utils.deep_linking import create_start_link
from ...utils.bot import Bot

@router.message(Command('friends'))
async def msg_friends(message: types.Message, bot_user: BotUser, bot: Bot, edit=False):
     deep_link = await create_start_link(bot, bot_user.id)
     text = f'Пригласи друга:\n{deep_link}'

     if edit:
         await message.edit_text(text, reply_markup=markups.back_to_start)
     else:
         await message.answer(text, reply_markup=markups.back_to_start)

@router.callback_query(F.data == 'friends')
async def call_friends(call: types.CallbackQuery, bot_user: BotUser, bot: Bot):
     await msg_friends(call.message, bot_user, bot, edit=True)
