from aiogram.filters.base import Filter

from ..protocols.telegram_user_event import TelegramUserEvent
from ..services.database.models import BotUser


class AdminFilter(Filter):
    async def __call__(self, telegram_object: TelegramUserEvent, **data):
        bot_user: BotUser = data.get('bot_user', None)
        if bot_user is not None:
            return bot_user.admin
        return False
