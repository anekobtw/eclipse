from enum import Enum

from aiogram import types

from db import BasesDatabase, HashesDatabase, ReferralsDatabase, UsersDatabase


class Databases(Enum):
    USERS = UsersDatabase()
    BASES = BasesDatabase()
    REFERRALS = ReferralsDatabase()
    HASHES = HashesDatabase()


class Constants(Enum):
    CHANNEL_ID = -1002360182485
    SEARCH_LIMIT = 100
    ADMINS = [8052123210, 1718021890, 1338590379]


class Messages(Enum):
    NOT_SUBSCRIBED = "<b><i>⚠️ Для поиска необходимо подписаться на канал проекта!</i></b>"
    WELCOME = "<b>👋 Приветствую!</b>\n<i>Мы используем данные из открытых источников, соблюдая законность их получения, и превращаем их в полезную информацию для поиска.</i>\n\n<b>📊 Всего запросов: <code>{searched}</code></b>\n\n<b><u>Выберите действие:</u></b>"
    SEARCH = "<b>🔎 <u>Поиск</u></b>\n\n<b>⬇️Примеры команд для ввода:</b>\n\n<b>👤Поиск</b>\n├  <code>Dream</code> (поиск по нику)\n└ <code>192.168.0.1</code> (поиск по айпи)\n\n<b>🔐Дехеш</b>\n├ <code>5d41402abc4b2a76b9719d911017c592</code> (MD5)\n└ <code>$SHA$98b56309949a071c$0d2c567a0</code> (AuthMe)"
    SUPPORT = "<b><u>❓ Часто задаваемые вопросы (FAQ)</u></b>\n\n<b>• Откуда берутся данные?</b>\n— Из открытых источников, а также частично из приватных баз, предоставленных нашими коллегами.\n\n<b>• Где можно посмотреть всю базу?</b>\n— Ознакомиться с базой данных можно <a href='https://t.me/insomniachecker/5'>здесь</a>\n\n<b>• Как быстро работает чекер?</b>\n— Среднее время обработки одного запроса — менее 0,3 мс.\n\n<b>• Что это за набор символов? (🔒$SHA$7d0a52749fff2a...)</b>\n— Это хеш - зашифрованный пароль, который нельзя прочитать напрямую без расшифровки.\n\n<b>• Что мне делать с хешем?</b>\n— Отправьте его в нашего бота. Если бот не сможет расшифровать, придется найти альтернативные методы расшифровки.\n\n<b>• Можно ли с нами сотрудничать?</b>\n— Да, вы можете делиться базами, хешами или как-то иначе помогать в развитии проекта, получая за это привилегии в чекере (иногда и деньги).\n\n<b>Если здесь нет ответа на ваш вопрос, можете написать нам по кнопке ниже.</b>"
    ACCOUNT = "<b>👤 <u>Мой аккаунт</u></b>\n\n<b>• 🪪 ID:</b> <code>{id}</code>\n<b>• ⚙️ Кол-во запросов:</b> <code>{quota}</code>\n<b>• 📊 Всего найдено:</b> <code>{searched}</code>\n\n<b>• 🔗 Твоя ссылка:</b> <code>{link}</code>"
    RATES = "<b>💳 <u>Тарифы</u></b>"


class Errors(Enum):
    QUOTA_ERROR = "❌ <b>У вас закончился лимит.</b> Обновление лимита будет в <code>0:00</code>"
    LENGTH_LIMIT_ERROR = "⚠️ Превышен лимит строк в одном сообщении"
    FILE_LIMIT_ERROR = "⚠️ Файл превышает 20 мегабайт."
    REF_ERROR = "/ref {кол-во запросов}\nНапример: <code>/ref 5</code>"
    OLD_DATA_ERROR = "⚠️ Ошибка: Данные устарели или не найдены."


class Keyboards(Enum):
    def start() -> types.InlineKeyboardMarkup:
        kb = [
            [
                types.InlineKeyboardButton(text="🔎 Поиск", callback_data="btn_search"),
                types.InlineKeyboardButton(text="👤 Мой аккаунт", callback_data="btn_account"),
            ],
            [
                types.InlineKeyboardButton(text="🆘 Поддержка", callback_data="btn_support"),
                types.InlineKeyboardButton(text="💳 Тарифы", callback_data="btn_rates"),
            ],
        ]
        return types.InlineKeyboardMarkup(inline_keyboard=kb)

    def subscription(nickname: str, show: bool) -> types.InlineKeyboardMarkup:
        kb = []
        if show:
            kb.append([types.InlineKeyboardButton(text="👀 Посмотреть информацию (-1 запрос)", callback_data=f"btn₽watch₽1₽0₽{nickname}")])
        kb.append([types.InlineKeyboardButton(text="💳 Оформить подписку", callback_data="btn_rates")])
        return types.InlineKeyboardMarkup(inline_keyboard=kb)

    def back() -> types.InlineKeyboardMarkup:
        return types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="← Назад", callback_data="btn_back")]])

    def purchase(back: bool = False) -> types.InlineKeyboardMarkup:
        buttons = [[types.InlineKeyboardButton(text="Приобрести (вручную)", url="https://t.me/ophanix")]]
        if back:
            buttons.append([types.InlineKeyboardButton(text="← Назад", callback_data="btn_back")])
        return types.InlineKeyboardMarkup(inline_keyboard=buttons)

    def support(back: bool = False) -> types.InlineKeyboardMarkup:
        buttons = [[types.InlineKeyboardButton(text="Связаться", url="https://t.me/ophanix")]]
        if back:
            buttons.append([types.InlineKeyboardButton(text="← Назад", callback_data="btn_back")])
        return types.InlineKeyboardMarkup(inline_keyboard=buttons)

    def subscribe() -> types.InlineKeyboardMarkup:
        return types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="✅ Подписаться", url="t.me/insomniachecker")]])
