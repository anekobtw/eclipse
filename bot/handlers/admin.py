import uuid

from aiogram import F, Router, types
from aiogram.filters import Command
from db import Referral, ReferralsDatabase, UsersDatabase
from handlers.helpers import parse_duration, text

router = Router()
refd = ReferralsDatabase()
ud = UsersDatabase()


@router.message(F.text, Command("ref"))
async def _(message: types.Message) -> None:
    if message.from_user.id not in [1718021890, 8052123210]:
        return

    try:
        args = message.text.split(" ")
        subscription, time, uses_left = args[1], args[2], args[3]
    except IndexError:
        await message.answer(text("ref_error"))
        return

    if subscription in ["premium", "premium+"] and parse_duration(time):
        id = str(uuid.uuid4())
        refd.add_referral(Referral(id, uses_left, subscription, time))
        await message.answer(f"t.me/insomniachecker_bot?start={id}")
    else:
        await message.answer("Ты ввел что-то неверно.")


@router.message(F.text, Command("reset"))
async def _(message: types.Message) -> None:
    if message.from_user.id in [1718021890, 8052123210]:
        users = ud.get_all()
        for user in users:
            new_quota = {"free": 5, "premium": 20, "premium+": 100}[user.subscription] + user.invited
            ud.update_user(user.user_id, "quota", new_quota)
    await message.answer("Все лимиты были сброшены!")
