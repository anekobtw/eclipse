import os

from aiogram import Bot, F, Router, types

import handlers.helpers as helpers
from enums import Constants, Databases, Errors
from handlers.pages import generate_page

router = Router()
callback_storage = {}


def process_object(obj: str) -> str | tuple[str, types.InlineKeyboardMarkup] | None:
    hashes = [h for h in helpers.get_hashtype(obj) if h["hashcat"] is not None]
    if hashes:
        password = Databases.HASHES.value.get_hash(obj)
        if password:
            return f"<code>{obj}</code> - это скорее всего хеш <code>{hashes[0]['name']}</code>\n\n✅ У нас получилось его расшифровать: <code>{password[1]}</code>"
        return f"<code>{obj}</code> - это скорее всего хеш <code>{hashes[0]['name']}</code>\n\nК сожалению, мы не можем его расшифровать"

    entity_info = Databases.BASES.value.get_ip(obj) if helpers.is_ip_address(obj) else Databases.BASES.value.get_user(obj)
    if entity_info:
        return generate_page(obj, entity_info, 0)
    return None


async def process_objects(message: types.Message, objects: list[str]) -> None:
    if len(objects) > Constants.SEARCH_LIMIT.value:
        await message.answer(Errors.LENGTH_LIMIT_ERROR.value)
        return
    
    not_found = []
    for obj in objects:
        if not obj:
            continue

        user = Databases.USERS.value.get_user(message.from_user.id)

        if user[1] <= 0:
            await message.answer(Errors.QUOTA_ERROR.value)
            break

        result = process_object(obj)

        if result is None:
            not_found.append(obj)
            continue
        elif isinstance(result, tuple):
            await message.answer(text=result[0], reply_markup=result[1])
        else:
            msg = await message.answer("Я думаю, что это хеш")
            callback_storage[msg.message_id] = obj
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="⚠️ Это не хеш", callback_data=f"nothash")]])
            await msg.edit_text(result, reply_markup=kb)

        Databases.USERS.value.update_user(message.from_user.id, "searched", user[2] + 1)
        Databases.USERS.value.update_user(message.from_user.id, "quota", user[1] - 1)
       

    if not_found:
        await message.answer(f"<b>❌ Не найдено:</b>\n{', '.join(not_found)}")


async def is_subscribed(user_id, bot: Bot) -> bool:
    check_member = await bot.get_chat_member(Constants.CHANNEL_ID, user_id)
    return check_member.status in ["administrator", "member", "creator"]


@router.message(F.document)
async def process_document(message: types.Message, bot: Bot) -> None:
    # if not await is_subscribed(message.from_user.id, message.bot):
    #     await message.answer(Messages.NOT_SUBSCRIBED.value, reply_markup=Keyboards.subscribe())
    #     return

    filepath = f"{message.from_user.id}.txt"
    await bot.download(message.document, destination=filepath)

    with open(filepath, "r") as file:
        objects = file.read().splitlines()

    os.remove(filepath)
    await process_objects(message, objects)


@router.message(F.text)
async def process_text(message: types.Message) -> None:
    # if not await is_subscribed(message.from_user.id, message.bot):
    #     await message.answer(Messages.NOT_SUBSCRIBED.value, reply_markup=Keyboards.subscribe())
    #     return

    objects = message.text.split("\n")
    await process_objects(message, objects)


@router.callback_query(F.data.startswith("nothash"))
async def process_nothash(callback: types.CallbackQuery) -> None:
    # if not await is_subscribed(callback.from_user.id, callback.bot):
    #     await callback.message.answer(Messages.NOT_SUBSCRIBED.value, reply_markup=Keyboards.subscribe())
    #     return

    obj = callback_storage.get(callback.message.message_id, None)

    if obj is None:
        await callback.message.answer(Errors.OLD_DATA_ERROR.value)
        return

    entity_info = Databases.BASES.value.get_ip(obj) if helpers.is_ip_address(obj) else Databases.BASES.value.get_user(obj)
    if entity_info:
        result = generate_page(obj, entity_info, 0)
    else:
        await callback.message.answer(f"<b>❌ Не найдено:</b>\n{obj}")

    if result is None:
        await callback.message.answer(f"<b>❌ Не найдено:</b>\n{obj}")
    else:
        await callback.message.answer(text=result[0], reply_markup=result[1])
