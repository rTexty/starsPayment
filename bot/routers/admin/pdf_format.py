from aiogram import F, types

from . import router
from ... import markups
from ...services.database.models import Settings


@router.callback_query(F.data == 'pdf_format')
async def get_statistics_callback(call: types.CallbackQuery):
    ap = await Settings.get(name='pdf_format')
    ap.bool_value = not ap.bool_value
    await ap.save()
    await call.message.edit_reply_markup(reply_markup=await markups.admin_panel())
