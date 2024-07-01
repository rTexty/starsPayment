from tortoise import Tortoise

from bot.services.database.models import Settings
from ...bot import bot 

TORTOISE_ORM = {
        "connections": {"default": bot.config.database_uri},
        "apps": {
            "models": {
                "models": ["bot.services.database.models", "aerich.models"],
                "default_connection": "default",
            },
        },
    }



class DatabaseService:
    async def setup(self):
        await Tortoise.init(TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await Settings.create_fields()

    async def dispose(self):
        await Tortoise.close_connections()
