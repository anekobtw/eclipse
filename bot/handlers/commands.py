import uuid
from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command, CommandObject, CommandStart

from db import RefIDsDatabase, UsersDatabase
from handlers.helpers import parse_duration, text
from handlers.keyboards import back_kb, purchase_kb, start_kb, support_kb

router = Router()
ud = UsersDatabase()
refd = RefIDsDatabase()


# Start
@router.message(F.text, Command("ref"))
async def _(message: types.Message) -> None:
    if message.from_user.id in [1718021890, 8052123210]:
        args = message.text.split(" ")
        try:
            subscription, time, uses_left = args[1], args[2], args[3]
        except IndexError:
            await message.answer(text("ref_error"))
            return
        if subscription in ["premium", "premium+"] and parse_duration(time):
            id = str(uuid.uuid4())
            refd.add_refid(id, uses_left, subscription, time)
            await message.answer(f"t.me/eclipse_mc_bot?start={id}")
        else:
            await message.answer("Ты ввел что-то неверно.")


@router.message(CommandStart(deep_link=True))
async def _(message: types.Message, command: CommandObject) -> None:
    if command.args.isdigit():
        if ud.get_user(message.from_user.id) is None:
            ud.add_user(message.from_user.id, "free", None, 5, 0)
            ud.update_user(int(command.args), "invited", ud.get_user(int(command.args))[4] + 1)
    else:
        ref = refd.get_refid(command.args)
        if ref:
            if ud.get_user(message.from_user.id)[1] == "premium+" and ref[2] == "premium":
                await message.answer("Подождите пока у вас закончится нынешний тариф.")
                return
            if ud.get_user(message.from_user.id)[1] == "free":
                ud.update_user(message.from_user.id, "subscription_until", datetime.now() + parse_duration(ref[3]))
            else:
                ud.update_user(message.from_user.id, "subscription_until", datetime.strptime(ud.get_user(message.from_user.id)[2], "%Y-%m-%d %H:%M:%S.%f") + parse_duration(ref[3]))
            ud.update_user(message.from_user.id, "subscription", ref[2])
            ud.update_user(message.from_user.id, "quota", {"free": 5, "premium": 20, "premium+": 100}[ref[2]])
        refd.use_refid(command.args)
    await message.answer(text("welcome"), reply_markup=start_kb())


@router.message(F.text, Command("menu", "start"))
async def _(message: types.Message) -> None:
    ud.add_user(message.from_user.id, "free", None, 5, 0)
    await message.answer(text("welcome"), reply_markup=start_kb())


@router.callback_query(F.data == "btn_back")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(text("welcome"), reply_markup=start_kb())


# Search
@router.message(F.text, Command("search"))
async def _(message: types.Message) -> None:
    await message.answer(text("search"))


@router.callback_query(F.data == "btn_search")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(text("search"), reply_markup=back_kb())


# Support
@router.message(F.text, Command("support"))
async def _(message: types.Message) -> None:
    await message.answer(text("support"), reply_markup=support_kb(False))


@router.callback_query(F.data == "btn_support")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(text("support"), reply_markup=support_kb(True))


# Account
@router.message(F.text, Command("account"))
async def _(message: types.Message) -> None:
    user = ud.get_user(message.from_user.id)

    await message.answer(
        text("account").format(
            id=user[0],
            subscription_emoji={"free": "🥀", "premium": "⭐️", "premium+": "💫"}[user[1]],
            subscription=user[1].capitalize(),
            subscription_until=user[2],
            quota=user[3],
            quota_max={"free": 5, "premium": 20, "premium+": 100}[user[1]],
            link=f"t.me/eclipse_mc_bot?start={message.from_user.id}",
        )
    )


@router.callback_query(F.data == "btn_account")
async def _(callback: types.CallbackQuery) -> None:
    user = ud.get_user(callback.from_user.id)

    await callback.message.edit_text(
        text("account").format(
            id=user[0],
            subscription_emoji={"free": "🥀", "premium": "⭐️", "premium+": "💫"}[user[1]],
            subscription=user[1].capitalize(),
            subscription_until=user[2],
            quota=user[3],
            quota_max={"free": 5, "premium": 20, "premium+": 100}[user[1]],
            link=f"t.me/eclipse_mc_bot?start={callback.from_user.id}",
        ),
        reply_markup=back_kb(),
    )


# Sub
@router.message(F.text, Command("sub"))
async def _(message: types.Message) -> None:
    await message.answer(text("rates"), reply_markup=purchase_kb(False))


@router.callback_query(F.data == "btn_rates")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(text("rates"), reply_markup=purchase_kb(True))
