from aiogram import F, Router, types

import handlers.helpers as helpers
from enums import Databases

router = Router()


def generate_page(value: str, entity_info: str, page: int) -> tuple[str, types.InlineKeyboardMarkup]:
    pages = ["\n\n".join(f"👤  <b>{entry[0]}</b>" + (f" • {entry[3]}" if entry[3] else "") + "\n" + "\n".join(f"{icon}  <code>{value.strip()}</code>" for icon, value in zip(["🔑", "🔒", "🌍", "🗄️"], entry[1:]) if value and (icon != "🌍")) for entry in entity_info[i : i + 5]) for i in range(0, len(entity_info), 5)]

    if page < 0 or page + 1 > len(pages):
        raise ValueError("Invalid page number")

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="⬅️", callback_data=f"watch₽{page-1}₽{value}"),
                types.InlineKeyboardButton(text=f"{page+1}/{len(pages)}", callback_data="nothing"),
                types.InlineKeyboardButton(text="➡️", callback_data=f"watch₽{page+1}₽{value}"),
            ],
        ]
    )

    return (pages[page], keyboard)


@router.callback_query(F.data.startswith("watch₽"))
async def _(callback: types.CallbackQuery) -> None:
    _, page, entity_value = callback.data.split("₽")
    page = int(page)

    if helpers.is_ip_address(entity_value):
        entity_info = Databases.BASES.value.get_ip(entity_value)
    else:
        entity_info = Databases.BASES.value.get_user(entity_value)

    try:
        res = generate_page(entity_value, entity_info, page)
    except ValueError:
        await callback.answer("Нет больше страниц.")
        return

    await callback.message.edit_text(res[0], reply_markup=res[1])
    await callback.answer()
