from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram.utils.i18n import gettext as _

from bot.services.database.models import Settings

from . import router
from ... import markups


@router.message(Command('admin'))
async def admin_panel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(await get_admin_text(), reply_markup=await markups.admin_panel())

@router.callback_query(F.data == 'back_admin')
async def back_admin(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(await get_admin_text(), reply_markup=await markups.admin_panel())


async def get_admin_text():
    course = await Settings.get(name='course')
    return f'👨‍💻 Админка\nКурс: <b>{course.float_value}</b>\nСмена курса: <code>/change_course 64.8</code>'