import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from db import UsersDatabase
from handlers import helpers, router

ud = UsersDatabase()


async def reset_limits() -> None:
    users = ud.get_all()
    for user in users:
        ud.update_user(user.user_id, "quota", helpers.get_quota_max(user.user_id))


async def run_bot() -> None:
    load_dotenv("config/.env")
    logging.basicConfig(
        level=logging.INFO,
        format="[%(name)s] %(message)s - %(asctime)s",
        datefmt="%H:%M:%S",
    )

    scheduler = AsyncIOScheduler()
    scheduler.add_job(reset_limits, "cron", hour=0, minute=0)
    scheduler.start()

    bot = Bot(token=os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
