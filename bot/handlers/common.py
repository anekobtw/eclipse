from aiogram import F, Router, types

import handlers.helpers as helpers
from db import BasesDatabase
from handlers.helpers import text
from handlers.keyboards import subscription_kb

router = Router()
bd = BasesDatabase()


def format_search_result(entity: str, entity_type: str, entity_info: list[tuple]) -> list:
    counts = {"usernames": sum(1 for row in entity_info if len(row) > 0 and row[0]), "passwords": sum(1 for row in entity_info if len(row) > 1 and row[1]), "hashes": sum(1 for row in entity_info if len(row) > 2 and row[2]), "ips": sum(1 for row in entity_info if len(row) > 3 and row[3])}

    match entity_type:
        case "ip":
            txt = text(f"{entity_type}_info").format(ip=entity, usernames=f"найдено ({counts["usernames"]})" if counts["usernames"] else "не найдено", hashes=f"найдено ({counts["hashes"]})" if counts["hashes"] else "не найдено", passwords=f"найдено ({counts["passwords"]})" if counts["passwords"] else "не найдено")
        case "user":
            txt = text(f"{entity_type}_info").format(username=entity, ips=f"найдено ({counts["ips"]})" if counts["ips"] else "не найдено", hashes=f"найдено ({counts["hashes"]})" if counts["hashes"] else "не найдено", passwords=f"найдено ({counts["passwords"]})" if counts["passwords"] else "не найдено")
    return [txt, subscription_kb(entity, any(counts.values()))]


def search_entity(value: str) -> list:
    entity_info, entity_type = (bd.get_by_ip(value), "ip") if helpers.is_ip_address(value) else (bd.get_user(value), "user")
    return format_search_result(value, entity_type, entity_info) if entity_info else [text("not_found").format(entity=value), None]


@router.message(F.text)
async def process_message(message: types.Message) -> None:
    msgs_to_delete = []
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
            msgs_to_delete.append(msg.message_id)
    for mid in msgs_to_delete:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=mid)
