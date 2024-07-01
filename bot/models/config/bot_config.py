from typing import Union, List

from pydantic import Field

from ..config_model import ConfigModel


class BotConfig(ConfigModel):
    __filenames__ = ("config_dev.json", "config.json")

    bot_token: str = Field()
    database_uri: str = Field()
    payment_api_key: str = Field()
    payment_secret_key: str = Field()
    merchant_id: str = Field()
    service_id: str = Field()
    wallet_pay_api_key: str = Field()