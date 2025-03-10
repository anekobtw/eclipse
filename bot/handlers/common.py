import asyncio

from aiogram import F, Router, types

import handlers.helpers as helpers
from db import BasesDatabase, Referral, ReferralsDatabase, User, UsersDatabase
from handlers.helpers import text
from handlers.keyboards import subscription_kb

router = Router()
bd = BasesDatabase()
ud = UsersDatabase()
rd = ReferralsDatabase()


def format_search_result(entity: str, entity_type: str, entity_info: list[tuple]) -> list:
    counts = {
        "usernames": sum(1 for row in entity_info if len(row) > 0 and row[0]),
        "passwords": sum(1 for row in entity_info if len(row) > 1 and row[1]),
        "hashes": sum(1 for row in entity_info if len(row) > 2 and row[2]),
        "ips": sum(1 for row in entity_info if len(row) > 3 and row[3])
    }

    match entity_type:
        case "ip":
            txt = text(f"{entity_type}_info").format(
                ip=entity,
                usernames=f"найдено ({counts["usernames"]})" if counts["usernames"] else "не найдено",
                hashes=f"найдено ({counts["hashes"]})" if counts["hashes"] else "не найдено",
                passwords=f"найдено ({counts["passwords"]})" if counts["passwords"] else "не найдено"
            )
        case "user":
            txt = text(f"{entity_type}_info").format(
                username=entity,
                ips=f"найдено ({counts["ips"]})" if counts["ips"] else "не найдено",
                hashes=f"найдено ({counts["hashes"]})" if counts["hashes"] else "не найдено",
                passwords=f"найдено ({counts["passwords"]})" if counts["passwords"] else "не найдено"
            )
    return [txt, subscription_kb(entity, any(counts.values()))]


def search_entity(value: str) -> list:
    entity_info, entity_type = (bd.get_by_ip(value), "ip") if helpers.is_ip_address(value) else (bd.get_user(value), "user")
    return format_search_result(value, entity_type, entity_info) if entity_info else [text(f"{entity_type}_not_found"), None]


@router.message(F.text)
async def process_message(message: types.Message) -> None:
    for line in message.text.split("\n"):
        if not line:
            continue

        hashes = [h for h in helpers.get_hashtype(line) if h["hashcat"]]
        if hashes:
            await message.answer(f"Это скорее всего хеш <code>{hashes[0]['name']}</code>\nК сожалению, мы не можем его расшифровать")
            return

        result = search_entity(line)
        msg = await message.answer(result[0], reply_markup=result[1])
        if result[1] == None:
            await asyncio.sleep(3)
            await msg.delete()


@router.callback_query(F.data.startswith("btn_watch"))
async def process_callback(callback: types.CallbackQuery) -> None:
    user = ud.get_user(callback.from_user.id)
    if not user or user.quota == 0:
        await callback.message.answer(text("error_limit"))
        return

    ud.update_user(callback.from_user.id, "quota", user.quota - 1)
    entity_value = callback.data[10:]
    entity_info = bd.get_by_ip(entity_value) if helpers.is_ip_address(entity_value) else bd.get_user(entity_value)

    messages, buffer = [], ""
    for index, entry in enumerate(entity_info, start=1):
        details = {k: v for k, v in zip(["👤 Никнейм", "🔑 Пароль", "🔒 Хеш", "🌍 Айпи", "💻 Сервер"], entry) if v}
        buffer += "\n".join(f"{key}: <code>{value}</code>" for key, value in details.items()) + "\n———————————————————————\n"

        if index % 5 == 0:
            messages.append(buffer)
            buffer = ""

    if buffer:
        messages.append(buffer)

    for msg in messages:
        await callback.message.answer(msg)
