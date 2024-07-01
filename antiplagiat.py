import asyncio
import io
import os
import time
import base64
import PyPDF2
from suds.client import Client
import uuid
from bot import markups
from bot.bot import bot
from bot.services.database.models import BotUser
import logging
import requests
from aiogram.types import BufferedInputFile

logger = logging.getLogger(__name__)



def send_request(name: str, *args):
    pass
def get_doc_data(buffer: io.BytesIO, filename: str):
    pass
def check_status(id, name: str):
    pass
def get_web_report(loop, bot_user: BotUser, buffer: io.BytesIO, filename, pdf_format: bool):
    pass
