import asyncio
import io
import threading
import uuid
from aiogram import F, types
from aiogram.utils.i18n import gettext as _
from pathlib import Path

from antiplagiat import get_web_report
from bot import markups
from bot.enums import PaymentEnum

from . import router
from ...services.database.models import BotUser, Settings
from bot.bot import bot

@router.message(F.document)
async def checkdoc(message: types.Message, bot_user: BotUser):
     pass
