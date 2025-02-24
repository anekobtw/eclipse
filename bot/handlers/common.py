from aiogram import F, Router, types

import handlers.helpers as helpers
from db import bases_get_ip, bases_get_user, usersdb_get, usersdb_update
from handlers.helpers import text
from handlers.keyboards import subscription_kb

router = Router()


def count_non_none(values: dict) -> int:
    return sum(1 for v in values.values() if v is not None)


def format_count(values: dict) -> str:
    return f"найдено ({count_non_none(values)})" if count_non_none(values) > 0 else "не найдено"


@router.message(F.text)
async def process_message(message: types.Message) -> None:
    try:
        txt = message.text

        if helpers.get_hashtype(txt):
            password = await helpers.dehash(txt)
            await message.answer(text("dehash_succeeded").format(password=password or "не найдено"))
            return

        if helpers.is_ip_address(txt):
            ip_info = bases_get_ip(txt)
            if ip_info is None:
                await message.answer(text("ip_not_found"))
                return

            reply_markup = subscription_kb(txt, any(count_non_none(ip_info[key]) for key in ["username", "hash", "password"]))
            await message.answer(text("ip_info").format(ip=txt, usernames=format_count(ip_info["username"]), hashes=format_count(ip_info["hash"]), passwords=format_count(ip_info["password"])), reply_markup=reply_markup)
            return

        user_info = bases_get_user(txt)
        if user_info is None:
            await message.answer(text("user_not_found"))
            return

        reply_markup = subscription_kb(txt, any(count_non_none(user_info[key]) for key in ["ip", "hash", "password"]))
        await message.answer(text("user_info").format(username=txt, hashes=format_count(user_info["hash"]), passwords=format_count(user_info["password"]), ips=format_count(user_info["ip"])), reply_markup=reply_markup)

    except Exception as e:
        print(e)
        await message.answer(text("error"))


@router.callback_query(F.data.startswith("btn_watch"))
async def _(callback: types.CallbackQuery) -> None:
    usersdb_update(callback.from_user.id, "quota", usersdb_get(callback.from_user.id)[3] - 1)
    nickname = callback.data[10:]
    data = bases_get_user(nickname)

    results = []

    for key in data["username"]:
        hash_value = data["hash"].get(key, "N/A")
        password = data["password"].get(key, "N/A")
        ip = data["ip"].get(key, "N/A")
        server = data["server"].get(key, "N/A")

        results.append({"hash": hash_value, "password": password, "ip": ip, "server": server})

    for i in range(0, len(results), 5):
        chunk = results[i : i + 5]
        message = ""

        for entry in chunk:
            message += f"🔑 <b>Пароль:</b> <code>{entry['password']}</code>\n" f"🔒 <b>Хеш:</b> <code>{entry['hash']}</code>\n" f"🌍 <b>Айпи:</b> <code>{entry['ip']}</code>\n" f"💻 <b>Сервер:</b> <code>{entry['server']}</code>\n" "────────────────────────────\n"

        await callback.message.answer(message)
