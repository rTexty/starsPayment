import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram.dispatcher.middlewares.base import BaseMiddleware

from ..services.database.models import BotUser, Metric, Settings
from ..protocols.telegram_user_event import TelegramUserEvent
from bot.bot import bot

logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramUserEvent, Dict[str, Any]], Awaitable[Any]],
        event: TelegramUserEvent,
        data: Dict[str, Any],
    ) -> Any:
        if event.text:
            split = event.text.split()

            if split[0] == '/start' and len(split) == 2:
                bot_user = await BotUser.get_or_none(id=event.from_user.id)

                if not bot_user:
                    logger.info(f'New user id={event.from_user.id} utm={split[1]}')
                    ap = await Settings.get(name='affiliate_program')
                    if ap.bool_value and split[1].isdecimal():
                        if referor := await BotUser.get_or_none(id=split[1]):
                            await BotUser.create(id=event.from_user.id, referrer=referor, username=event.from_user.username)
                            referor.free_checks = referor.free_checks + 1
                            await referor.save(update_fields=['free_checks'])
                            await bot.send_message(referor.id, f'Только что присоединился твой друг! 🎉\n\nТеперь у тебя есть {referor.get_available_checks}. Спасибо за поддержку нашего сервиса! 🤗')
                            data["is_new_user"] = True
                    else:
                        if ads := await Metric.get_or_none(code=split[1]):
                            await BotUser.create(id=event.from_user.id, metric_id=ads.id, username=event.from_user.username)
                            data["is_new_user"] = True


        return await handler(event, data)
