import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import UsersDatabase
from dotenv import load_dotenv
from handlers import router

ud = UsersDatabase()


async def check_users() -> None:
    users = ud.get_all()
    for user in users:
        if user.subscription_until is not None:
            if datetime.now() >= datetime.strptime(user.subscription_until, "%Y-%m-%d %H:%M:%S.%f"):
                ud.update_user(user.user_id, "subscription", "free")
                ud.update_user(user.user_id, "subscription_until", None)
                ud.update_user(user.user_id, "quota", 5)


async def reset_limits() -> None:
    users = ud.get_all()
    for user in users:
        new_quota = {"free": 5, "premium": 20, "premium+": 100}[user.subscription] + user.invited
        ud.update_user(user.user_id, "quota", new_quota)


async def run_bot() -> None:
    load_dotenv("config/.env")
    logging.basicConfig(
        level=logging.INFO,
        format="[%(name)s] %(message)s - %(asctime)s",
        datefmt="%H:%M:%S",
    )

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_users, "interval", minutes=1)
    scheduler.add_job(reset_limits, "cron", hour=0, minute=0)
    scheduler.start()

    bot = Bot(token=os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
