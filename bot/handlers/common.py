from aiogram import F, Router, types

import handlers.helpers as helpers
from db import BasesDatabase, UsersDatabase
from handlers.helpers import text
from handlers.keyboards import subscription_kb

router = Router()
bd = BasesDatabase()
ud = UsersDatabase()


def search_ip(ip: str) -> list:
    ip_info = bd.get_by_ip(ip)
    if not ip_info:
        return [text("ip_not_found"), None]

    usernames = len([row[0] for row in ip_info if row[0] is not None])
    hashes = len([row[2] for row in ip_info if row[2] is not None])
    passwords = len([row[1] for row in ip_info if row[1] is not None])

    return [text("ip_info").format(
            ip=ip,
            usernames=f"найдено ({usernames})" if usernames > 0 else "не найдено",
            hashes=f"найдено ({hashes})" if hashes > 0 else "не найдено",
            passwords=f"найдено ({passwords})" if passwords > 0 else "не найдено",
        ), subscription_kb(ip, any([usernames>0, hashes>0, passwords>0]))]


def search_user(user: str) -> list:
    user_info = bd.get_user(user)
    if not user_info:
        return [text("user_not_found"), None]

    hashes = len([row[2] for row in user_info if row[2] is not None])
    passwords = len([row[1] for row in user_info if row[1] is not None])
    ips = len([row[3] for row in user_info if row[3] is not None])

    return [text("user_info").format(
            username=user,
            hashes=f"найдено ({hashes})" if hashes > 0 else "не найдено",
            passwords=f"найдено ({passwords})" if passwords > 0 else "не найдено",
            ips=f"найдено ({ips})" if ips > 0 else "не найдено",
        ), subscription_kb(user, any([ips>0, hashes>0, passwords>0]))]


@router.message(F.text)
async def _(message: types.Message) -> None:
    try:
        for txt in message.text.split("\n"):
            if not txt:
                continue
            if helpers.get_hashtype(txt):
                hashes = [h for h in helpers.get_hashtype(txt) if h["hashcat"] is not None]
                if hashes:
                    await message.answer(f"Это скорее всего хеш <code>{hashes[0]["name"]}</code>\nК сожалению, мы не можем его расшифровать")
                    return
            result = search_ip(txt) if helpers.is_ip_address(txt) else search_user(txt)
            await message.answer(result[0], reply_markup=result[1])

    except Exception as e:
        print(e)
        await message.answer(text("error"))


@router.callback_query(F.data.startswith("btn_watch"))
async def _(callback: types.CallbackQuery) -> None:
    if ud.get_user(callback.from_user.id)[3] == 0:
        await callback.message.answer(text("error_limit"))
        return

    ud.update_user(callback.from_user.id, "quota", ud.get_user(callback.from_user.id)[3] - 1)
    user_data = bd.get_by_ip(callback.data[10:]) if helpers.is_ip_address(callback.data[10:]) else bd.get_user(callback.data[10:])

    messages, buffer = [], ""
    for index, user in enumerate(user_data, start=1):
        details = {
            "👤 Никнейм": user[0],
            "🔑 Пароль": user[1],
            "🔒 Хеш": user[2],
            "🌍 Айпи": user[3],
            "💻 Сервер": user[4],
        }

        entry = "\n".join(f"{key}: <code>{value}</code>" for key, value in details.items() if value)
        buffer += f"{entry}\n———————————————————————\n"

        if index % 5 == 0:
            messages.append(buffer)
            buffer = ""

    if buffer:
        messages.append(buffer)

    for msg in messages:
        await callback.message.answer(msg)
