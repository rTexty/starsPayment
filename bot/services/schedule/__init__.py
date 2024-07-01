from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .jobs import add_available_checks
from datetime import datetime, timedelta
from pytz import timezone

class ScheduleService(AsyncIOScheduler):
    def __init__(self) -> None:
        super().__init__()

    def add_timer(self, func, minutes, *args, **kwargs):
        execute_time  = datetime.now() + timedelta(minutes=minutes)
        self.add_job(func, 'date', args=args, run_date=execute_time, misfire_grace_time=None, **kwargs)

    async def setup(self):
        # self.add_job(add_available_checks, 'cron', hour=12, minute=0, second=0, timezone=timezone('Europe/Moscow'))
        self.start()

    async def dispose(self):
        self.shutdown()
