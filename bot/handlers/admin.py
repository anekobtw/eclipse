import os
import uuid

from aiogram import Bot, F, Router, exceptions, types
from aiogram.filters import Command

from enums import Constants, Databases, Errors

router = Router()


@router.message(F.document, Command("output"))
async def _(message: types.Message, bot: Bot) -> None:
    if message.from_user.id not in Constants.ADMINS:
        return

    try:
        await bot.download(message.document, destination="hashes.txt")
    except exceptions.TelegramBadRequest:
        await message.answer(Errors.FILE_LIMIT_ERROR.value)
        return

    with open("hashes.txt", "r") as f:
        hashes = []
        passwords = []
        for line in f:
            line = line.strip()
            if not line:
                continue

            hash, password = line.split(":")
            hashes.append(hash)
            passwords.append(password)
        Databases.HASHES.value.add_hashes(hashes, passwords)
    os.remove("hashes.txt")
    await message.answer("✅ Все хеши были успешно добавлены в базу!")


@router.message(F.text, Command("ref"))
async def _(message: types.Message) -> None:
    if message.from_user.id not in [1718021890, 8052123210]:
        return

    args = message.text.split(" ")
    if len(args) != 2:
        await message.answer(Errors.REF_ERROR.value)
        return
    args[1]
    id = str(uuid.uuid4())
    Databases.REFERRALS.value.add_referral(id, args[1])
    await message.answer(f"t.me/anekobtw_dev_bot?start={id}")
