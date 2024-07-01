import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram.dispatcher.middlewares.base import BaseMiddleware

from ..protocols.telegram_user_event import TelegramUserEvent
from ..services.database.models import BotUser

logger = logging.getLogger(__name__)

class BotUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramUserEvent, Dict[str, Any]], Awaitable[Any]],
        event: TelegramUserEvent,
        data: Dict[str, Any],
    ) -> Any:

        bot_user, is_new_user = await BotUser.update_or_create(
            dict(username=event.from_user.username, active=True),
            id=event.from_user.id
        )
        
        if is_new_user:
            logger.info(f'New user id={event.from_user.id}')
            bot_user.available_checks = 1
            await bot_user.save(update_fields=['available_checks'])
            logger.info(f'Plus one check for user id={event.from_user.id}')

        data["bot_user"] = bot_user
        data["is_new_user"] = data.get('is_new_user', is_new_user)
        
        return await handler(event, data)
