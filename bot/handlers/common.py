from aiogram import F, Router, types

import handlers.helpers as helpers
from db import BasesDatabase, UsersDatabase
from handlers.helpers import text
from handlers.keyboards import subscription_kb

router = Router()
bd = BasesDatabase()
ud = UsersDatabase()


@router.message(F.text)
async def process_message(message: types.Message) -> None:
    try:
        txt = message.text

        if helpers.get_hashtype(txt):
            password = await helpers.dehash(txt)
            await message.answer(text("dehash_succeeded").format(password=password or "не найдено"))
            return

        if helpers.is_ip_address(txt):
            ip_info = bd.get_by_ip(txt)
            if not ip_info:
                await message.answer(text("ip_not_found"))
                return

            usernames = len([row[0] for row in ip_info if row[0] is not None])
            hashes = len([row[2] for row in ip_info if row[2] is not None])
            passwords = len([row[1] for row in ip_info if row[1] is not None])
            
            await message.answer(
                text("ip_info").format(
                    ip=txt,
                    usernames=f"найдено ({usernames})" if usernames > 0 else "не найдено",
                    hashes=f"найдено ({hashes})" if hashes > 0 else "не найдено",
                    passwords=f"найдено ({passwords})" if passwords > 0 else "не найдено",
                ),
                reply_markup=subscription_kb(txt, any([usernames>0, hashes>0, passwords>0])),
            )
            return

        user_info = bd.get_user(txt)
        if not user_info:
            await message.answer(text("user_not_found"))
            return

        hashes = len([row[2] for row in user_info if row[2] is not None])
        passwords = len([row[1] for row in user_info if row[1] is not None])
        ips = len([row[3] for row in user_info if row[3] is not None])

        await message.answer(
            text("user_info").format(
                username=txt,
                hashes=f"найдено ({hashes})" if hashes > 0 else "не найдено",
                passwords=f"найдено ({passwords})" if passwords > 0 else "не найдено",
                ips=f"найдено ({ips})" if ips > 0 else "не найдено",
            ),
            reply_markup=subscription_kb(txt, any([hashes>0, passwords>0, ips>0])),
        )

    except Exception as e:
        print(e)
        await message.answer(text("error"))


@router.callback_query(F.data.startswith("btn_watch"))
async def _(callback: types.CallbackQuery) -> None:
    ud.update_user(callback.from_user.id, "quota", ud.get_user(callback.from_user.id)[3] - 1)
    nickname = callback.data[10:]
    data = bd.get_user(nickname)

    message, c = "", 0
    for user in data:
        message += f"🔑 <b>Пароль:</b> <code>{user[1]}</code>\n" f"🔒 <b>Хеш:</b> <code>{user[2]}</code>\n" f"🌍 <b>Айпи:</b> <code>{user[3]}</code>\n" f"💻 <b>Сервер:</b> <code>{user[4]}</code>\n" "────────────────────────────\n"
        c += 1
        if c == 5:
            await callback.message.answer(message)
            message, c = "", 0
