from aiogram import F, Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED
from aiogram.types import ChatMemberUpdated

from bot.services.database.models import BotUser

from . import root_handlers_router

user_router = Router()
user_router.message.filter(F.chat.type == 'private')
root_handlers_router.include_router(user_router)

@user_router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    user = await BotUser.get_or_none(id=event.from_user.id)
    if user:
        user.active = False
        await user.save()
