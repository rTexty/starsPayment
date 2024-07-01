from datetime import date
from tortoise import fields
from tortoise.models import Model
from typing import Union, List
from tortoise import Tortoise
from dataclasses import dataclass

from bot.enums import PaymentEnum
from bot.payments.AbstractPayment import AbstractPayment


class Metric(Model):
    id = fields.IntField(pk=True, unique=True)
    code = fields.TextField()
    description = fields.TextField()

    users: fields.ReverseRelation["BotUser"]

    @classmethod
    async def get_metrics(cls):
        query = """
            SELECT m.code AS code, m.description AS desc, COUNT(u.id) AS count
            FROM metrics AS m
            LEFT JOIN bot_users AS u ON m.id = u.metric_id
            GROUP BY m.id;
        """
        metrics = await Tortoise.get_connection('default').execute_query_dict(query)
        
        return metrics
    
    class Meta:
        table = 'metrics'


class Settings(Model):
    name = fields.TextField(pk=True)
    float_value = fields.FloatField(default=1)
    bool_value = fields.BooleanField(default=True)

    @classmethod
    async def create_fields(cls):
        await cls.create_if_not_exists(name='course')
        await cls.create_if_not_exists(name='affiliate_program')
        await cls.create_if_not_exists(name='pdf_format')
        await cls.create_if_not_exists(name='payment_method')

    @classmethod
    async def create_if_not_exists(cls, name: str):
        if not await cls.exists(name=name):
            await cls.create(name=name)

    @classmethod    
    async def get_payment_class(cls) -> AbstractPayment:
        from bot.bot import onevisionpay, wallet_pay
        payment_method = (await cls.get(name='payment_method')).bool_value
        return [onevisionpay, wallet_pay,][payment_method]

class BotUser(Model):
    id = fields.BigIntField(pk=True)
    username = fields.TextField(null=True)
    admin = fields.BooleanField(default=False)
    time_reg = fields.DatetimeField(auto_now_add=True)
    metric: fields.ForeignKeyRelation[Metric] = fields.ForeignKeyField(
        "models.Metric", on_delete=fields.SET_NULL, related_name="metric", null=True
    )
    referrer: fields.ForeignKeyRelation['BotUser'] = fields.ForeignKeyField(
        'models.BotUser', on_delete=fields.SET_NULL, null=True
    )
    active = fields.BooleanField(default=True)
    is_banned = fields.BooleanField(default=False)

    available_checks = fields.IntField(default=0)
    free_checks = fields.IntField(default=0)
    time_use_free_check = fields.DateField(null=True)

    @property
    def get_available_checks(self) -> str:

        suffixes_available = {
            'one': 'проверка',
            'many': 'проверки',
            'other': 'проверок',
        }

        suffixes_free = {
            'one': 'бесплатная проверка',
            'many': 'бесплатные проверки',
            'other': 'бесплатных проверок',
        }
        
        if self.available_checks == 1:
            text_available = suffixes_available.get('one')
        elif self.available_checks in [2, 3, 4]:
            text_available = suffixes_available.get('many')
        else:
            text_available = suffixes_available.get('other')

        if self.free_checks == 1:
            text_free = suffixes_free.get('one')
        elif self.free_checks in [2, 3, 4]:
            text_free = suffixes_free.get('many')
        else:
            text_free = suffixes_free.get('other')

        if self.free_checks:
            if not self.available_checks:
                return f'<b>{self.free_checks} {text_free}</b>'
            else:
                return f'<b>{self.available_checks} {text_available} и {self.free_checks} {text_free}</b>'

        return f'<b>{self.available_checks} {text_available}</b>'

    @property
    def url(self) -> str:
        url = f'<a href="{self.id}">*ссылка*</a>'
        if self.username: url = '@' + self.username
        return url
    
    async def subtract_check(self) -> PaymentEnum:

        if self.admin:
            return PaymentEnum.successfully

        if self.free_checks and await self.check_and_update_date():
            self.free_checks = self.free_checks - 1
            await self.save(update_fields=['free_checks'])
            return PaymentEnum.successfully

        elif self.available_checks > 0:
            self.available_checks = self.available_checks - 1
            await self.save(update_fields=['available_checks'])
            return PaymentEnum.successfully
        
        if not await self.check_and_update_date():
            return PaymentEnum.free_checks_over
        if self.available_checks <= 0:
            return PaymentEnum.not_enough_funds
        
        return PaymentEnum.not_enough_funds

    async def check_and_update_date(self):
        if self.time_use_free_check != date.today():
            self.time_use_free_check = date.today()
            await self.save()
            return True
        return False
    
    @classmethod
    async def get_user(cls, query: Union[int, str]) -> 'BotUser':
        if isinstance(query, int):
            field = 'id'
        else:
            query = query.replace('@', '').replace('https://t.me/', '')
            field = 'id' if query.isdecimal() else 'username'
        user =  await cls.get_or_none(**{field: query})

        return user

    @classmethod
    async def get_top_referrers(cls) -> List['UserReferralData']:
        query = """
            SELECT t1.id AS user_id, COUNT(t2.id) AS count
            FROM bot_users AS t1
            LEFT JOIN bot_users AS t2 ON t1.id = t2.referrer_id
            GROUP BY t1.id
            ORDER BY count DESC
            LIMIT 5;
        """

        result = await Tortoise.get_connection('default').execute_query_dict(query)
        user_ids = [row['user_id'] for row in result]

        top_referrers = await BotUser.filter(id__in=user_ids)

        users_dict = {user.id: user for user in top_referrers}

        refs = []
        for row in result:

            refs.append(
                UserReferralData(
                    users_dict.get(
                        row['user_id']
                    ),
                    row['count']
                )
            )

        return refs


    class Meta:
        table = 'bot_users'

class Payment(Model):
    id = fields.TextField(pk=True)
    payment_id = fields.TextField()
    amount = fields.FloatField()
    checks = fields.IntField()
    user: fields.ForeignKeyRelation[BotUser] = fields.ForeignKeyField(
        "models.BotUser", related_name="user"
    )
    status = fields.TextField(null=True)



@dataclass
class UserReferralData:
    user: BotUser
    referral_count: int

# class ModelFields(Model):
#     id = fields.IntField(pk=True, unique=True)
#     need_comment = fields.BooleanField(default=False)

#     id = fields.BigIntField(pk=True, unique=True)
#     time_start = fields.DatetimeField(auto_now_add=True)
#     time_finish = fields.DatetimeField(null=True)

#     address: fields.ReverseRelation["ChecksOption"]
#     option: fields.ForeignKeyRelation["ChecksOption"] = fields.ForeignKeyField(
#         "models.ChecksOption", on_delete='CASCADE', related_name="option_orders"
#     )
#     comment = fields.TextField(default='')
