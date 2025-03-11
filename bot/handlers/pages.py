from aiogram import F, Router, types

import handlers.helpers as helpers
from db import BasesDatabase, ReferralsDatabase, UsersDatabase

router = Router()
bd = BasesDatabase()
ud = UsersDatabase()
rd = ReferralsDatabase()


@router.callback_query(F.data.startswith("btn_watch_"))
async def _(callback: types.CallbackQuery) -> None:
    _, _, is_first, page, entity_value = callback.data.split("_")
    page = int(page)

    if is_first == "1":
        user = ud.get_user(callback.from_user.id)
        if not user or user.quota == 0:
            await callback.message.answer(helpers.text("error_limit"))
            return
        ud.update_user(callback.from_user.id, "quota", user.quota - 1)

    entity_info = bd.get_by_ip(entity_value) if helpers.is_ip_address(entity_value) else bd.get_user(entity_value)

    # Paginate the results (sorry for making this unreadable)
    pages = ["\n\n".join(
        f"👤  <b>{entry[0]}</b>" + (f" • {entry[3]}" if entry[3] else "") + "\n" +
        "\n".join(f"{icon}  <code>{value.strip()}</code>" for icon, value in zip(
            ["🔑", "🔒", "🌍", "🗄️"], entry[1:]) if value and (icon != "🌍")  # IP is already shown
        ) for entry in entity_info[i:i + 5]
    ) for i in range(0, len(entity_info), 5)]

    # Handle page navigation
    if page < 0 or page >= len(pages):
        await callback.answer("Нет больше страниц.")
        return

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="⬅️", callback_data=f"btn_watch_0_{page-1}_{entity_value}"),
                types.InlineKeyboardButton(text=f"{page+1}/{len(pages)}", callback_data="nothing"),
                types.InlineKeyboardButton(text="➡️", callback_data=f"btn_watch_0_{page+1}_{entity_value}"),
            ],
        ]
    )

    await callback.message.edit_text(pages[page], reply_markup=keyboard)
    await callback.answer()
