import os

from aiogram import Bot, F, Router, types

import handlers.helpers as helpers
from db import BasesDatabase, HashesDatabase, UsersDatabase
from handlers.helpers import text
from handlers.keyboards import subscription_kb, subscribe

router = Router()
bd = BasesDatabase()
ud = UsersDatabase()
hd = HashesDatabase()

SUBSCRIPTION_LIMITS = {"free": 20, "premium": 100, "premium+": 300}
callback_storage = {}


def format_search_result(entity: str, entity_type: str, entity_info: list[tuple]) -> tuple[str, types.InlineKeyboardMarkup]:
    counts = {"usernames": sum(1 for row in entity_info if len(row) > 0 and row[0]), "passwords": sum(1 for row in entity_info if len(row) > 1 and row[1]), "hashes": sum(1 for row in entity_info if len(row) > 2 and row[2]), "ips": sum(1 for row in entity_info if len(row) > 3 and row[3])}
    placeholders = {"usernames": f"найдено ({counts['usernames']})" if counts["usernames"] else "не найдено", "passwords": f"найдено ({counts['passwords']})" if counts["passwords"] else "не найдено", "hashes": f"найдено ({counts['hashes']})" if counts["hashes"] else "не найдено", "ips": f"найдено ({counts['ips']})" if counts["ips"] else "не найдено"}
    txt = text(f"{entity_type}_info").format(ip=entity if entity_type == "ip" else "", username=entity if entity_type == "user" else "", **placeholders)
    return txt, subscription_kb(entity, any(counts.values()))


def handle_message(text: str) -> str | tuple[str, types.InlineKeyboardMarkup] | None:
    hashes = [h for h in helpers.get_hashtype(text) if h["hashcat"] is not None]
    if hashes:
        password = hd.get_hash(text)
        if password:
            return f"<code>{text}</code> - это скорее всего хеш <code>{hashes[0]['name']}</code>\n\n✅ У нас получилось его расшифровать: <code>{password[1]}</code>"
        return f"<code>{text}</code> - это скорее всего хеш <code>{hashes[0]['name']}</code>\n\nК сожалению, мы не можем его расшифровать"

    entity_info, entity_type = (bd.get_by_ip(text), "ip") if helpers.is_ip_address(text) else (bd.get_user(text), "user")
    return format_search_result(text, entity_type, entity_info) if entity_info else None


async def process_objects(message: types.Message, objects: list[str]) -> None:
    user = ud.get_user(message.from_user.id)
    if not len(objects) == 1:  # because of hashes
        limit = SUBSCRIPTION_LIMITS.get(user.subscription, 20)

        if len(objects) > limit:
            await message.answer("⚠️ Превышен лимит строк в одном сообщении")
            return

    not_found = []
    for obj in objects:
        if not obj:
            continue
        result = handle_message(obj)
        if result is None:
            not_found.append(obj)
        elif isinstance(result, tuple):
            await message.answer(text=result[0], reply_markup=result[1])
        else:
            msg = await message.answer("Я думаю, что это хеш")
            callback_storage[msg.message_id] = obj
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="⚠️ Это не хеш", callback_data=f"nothash")]])
            await msg.edit_text(result, reply_markup=kb)

    if not_found:
        await message.answer(f"<b>❌ Не найдено:</b>\n{', '.join(not_found)}")

    ud.update_user(message.from_user.id, "searched", user.searched + len(objects))


async def is_subscribed(user_id, bot: Bot) -> bool:
    check_member = await bot.get_chat_member(-1002360182485, user_id) 
    if check_member.status in ["administrator", "member", "creator"]:
        return True
    return False


@router.message(F.document)
async def process_document(message: types.Message, bot: Bot) -> None:
    if not await is_subscribed(message.from_user.id, message.bot):
        await message.answer(text("not_subscribed"), reply_markup=subscribe())
        return

    filepath = f"{message.from_user.id}.txt"
    await bot.download(message.document, destination=filepath)

    with open(filepath, "r") as file:
        objects = file.read().splitlines()

    os.remove(filepath)
    await process_objects(message, objects)


@router.message(F.text)
async def process_text(message: types.Message) -> None:
    if not await is_subscribed(message.from_user.id, message.bot):
        await message.answer(text("not_subscribed"), reply_markup=subscribe())
        return

    objects = message.text.split("\n")
    await process_objects(message, objects)


@router.callback_query(F.data.startswith("nothash"))
async def process_nothash(callback: types.CallbackQuery) -> None:
    if not await is_subscribed(callback.from_user.id, callback.bot):
        await callback.message.answer(text("not_subscribed"), reply_markup=subscribe())
        return

    obj = callback_storage.get(callback.message.message_id, None)

    if obj is None:
        await callback.message.answer("⚠️ Ошибка: Данные устарели или не найдены.")
        return

    entity_info, entity_type = (bd.get_by_ip(obj), "ip") if helpers.is_ip_address(obj) else (bd.get_user(obj), "user")
    result = format_search_result(obj, entity_type, entity_info) if entity_info else None

    if result is None:
        await callback.message.answer(f"<b>❌ Не найдено:</b>\n{obj}")
    else:
        await callback.message.answer(text=result[0], reply_markup=result[1])
