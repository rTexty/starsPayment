import logging
import traceback
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject

from bot.routers.admin.admin import admin_panel

from . import router
from ...services.database.models import Settings

logger = logging.getLogger(__name__)


@router.message(Command('change_course'))
async def get_statistics_callback(message: types.Message, command: CommandObject, state: FSMContext):
    error = 'Неверный ввод, пример:\n<code>/change_course 45.2</code>'

    if command.args is None:
        await message.answer(error)
        return
    try:
        course = await Settings.get(name='course')
        course.float_value = float(command.args)
        await course.save()
        await message.answer('✅ Успешно')
        await admin_panel(message, state)
    except:
        logger.error(traceback.format_exc())
        await message.answer(error)