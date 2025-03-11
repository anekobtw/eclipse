from aiogram import types


def start_kb() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🔎 Поиск", callback_data="btn_search"),
                types.InlineKeyboardButton(text="👤 Мой аккаунт", callback_data="btn_account"),
            ],
            [
                types.InlineKeyboardButton(text="🆘 Поддержка", callback_data="btn_support"),
                types.InlineKeyboardButton(text="💳 Тарифы", callback_data="btn_rates"),
            ],
        ]
    )


def subscription_kb(nickname: str, show: bool) -> types.InlineKeyboardMarkup:
    kb = []
    if show:
        kb.append([types.InlineKeyboardButton(text="👀 Посмотреть информацию (-1 запрос)", callback_data=f"btn_watch_1_0_{nickname}")])
    kb.append([types.InlineKeyboardButton(text="💳 Оформить подписку", callback_data="btn_rates")])
    return types.InlineKeyboardMarkup(inline_keyboard=kb)


def back_kb() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="← Назад", callback_data="btn_back")],
        ]
    )


def purchase_kb(back: bool = False) -> types.InlineKeyboardMarkup:
    buttons = [[types.InlineKeyboardButton(text="Приобрести (вручную)", url="https://t.me/ophanix")]]
    if back:
        buttons.append([types.InlineKeyboardButton(text="← Назад", callback_data="btn_back")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def support_kb(back: bool = False) -> types.InlineKeyboardMarkup:
    buttons = [[types.InlineKeyboardButton(text="Связаться", url="https://t.me/ophanix")]]
    if back:
        buttons.append([types.InlineKeyboardButton(text="← Назад", callback_data="btn_back")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
