from aiogram import F, Router, types

import handlers.helpers as helpers
from db import BasesDatabase, UsersDatabase
from handlers.helpers import text
from handlers.keyboards import subscription_kb

router = Router()
bd = BasesDatabase()
ud = UsersDatabase()


@router.message(F.text)
async def _(message: types.Message) -> None:
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
    if ud.get_user(callback.from_user.id)[3] == 0:
        await callback.message.answer("У вас закончился лимит. Обновление лимита будет в 00:00.")
        return

    ud.update_user(callback.from_user.id, "quota", ud.get_user(callback.from_user.id)[3] - 1)
    user_data = bd.get_user(callback.data[10:])

    messages, buffer = [], ""
    for index, user in enumerate(user_data, start=1):
        details = {
            "🔑 Пароль": user[1],
            "🔒 Хеш": user[2],
            "🌍 Айпи": user[3],
            "💻 Сервер": user[4],
        }

        entry = "\n".join(f"{key}: <code>{value}</code>" for key, value in details.items() if value)
        buffer += f"{entry}\n\n"
        
        if index % 5 == 0:
            messages.append(buffer)
            buffer = ""

    if buffer:
        messages.append(buffer)
    
    for msg in messages:
        await callback.message.answer(msg)
