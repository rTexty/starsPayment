from bot.services.database.models import BotUser

async def add_available_checks():
    await BotUser.filter(active=True, available_checks__lt=3).update(available_checks=3)
