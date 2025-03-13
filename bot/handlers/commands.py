from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command, CommandObject, CommandStart

from db import ReferralsDatabase, User, UsersDatabase
from handlers import helpers
from handlers.helpers import parse_duration, text
from handlers.keyboards import back_kb, purchase_kb, start_kb, support_kb

router = Router()
ud = UsersDatabase()
refd = ReferralsDatabase()


# Start
@router.message(CommandStart(deep_link=True))
async def _(message: types.Message, command: CommandObject) -> None:
    if command.args.isdigit():
        # Got that from a user
        if ud.get_user(message.from_user.id) is None:
            ud.add_user(User(message.from_user.id, "free", None, 5, 0, 0))
            new_invited = ud.get_user(int(command.args)).invited + 1
            ud.update_user(int(command.args), "invited", new_invited)

    else:
        # It's a premium referral link
        ud.add_user(User(message.from_user.id, "free", None, 5, 0, 0))

        ref = refd.get_referral(command.args)
        refd.use_referral(command.args)
        if not ref:
            return

        if ud.get_user(message.from_user.id).subscription == "premium+" and ref.subscription == "premium":
            await message.answer("Подождите пока у вас закончится нынешний тариф.")
            return

        if ud.get_user(message.from_user.id).subscription == "free":
            new_date = datetime.now() + parse_duration(ref.time)
            ud.update_user(message.from_user.id, "subscription_until", new_date)
        else:
            new_date = datetime.strptime(ud.get_user(message.from_user.id).subscription_until, "%Y-%m-%d %H:%M:%S.%f") + parse_duration(ref.time)
            ud.update_user(message.from_user.id, "subscription_until", new_date)

        ud.update_user(message.from_user.id, "subscription", ref.subscription)
        ud.update_user(message.from_user.id, "quota", {"free": 5, "premium": 20, "premium+": 100}[ref.subscription])
    await message.answer(text("welcome").format(searched=helpers.get_all_time_searched()), reply_markup=start_kb())


@router.message(F.text, Command("menu", "start"))
async def _(message: types.Message) -> None:
    ud.add_user(User(message.from_user.id, "free", None, 5, 0, 0))
    await message.answer(text("welcome").format(searched=helpers.get_all_time_searched()), reply_markup=start_kb())


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
    await message.answer(text("support"), reply_markup=support_kb(False), link_preview_options=types.link_preview_options.LinkPreviewOptions(is_disabled=True))


@router.callback_query(F.data == "btn_support")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(text("support"), reply_markup=support_kb(True), link_preview_options=types.link_preview_options.LinkPreviewOptions(is_disabled=True))


# Account
@router.message(F.text, Command("account"))
async def _(message: types.Message) -> None:
    user = ud.get_user(message.from_user.id)

    await message.answer(
        text("account").format(
            id=user.user_id,
            subscription_emoji={"free": "🥀", "premium": "⭐️", "premium+": "💫"}[user.subscription],
            subscription=user.subscription.capitalize(),
            subscription_until=user.subscription_until,
            quota=user.quota,
            quota_max=helpers.get_quota_max(message.from_user.id),
            searched=user.searched,
            link=f"t.me/insomniachecker_bot?start={message.from_user.id}",
            invited=user.invited,
            progress_bar=helpers.get_progressbar(message.from_user.id)
        ),
        link_preview_options=types.link_preview_options.LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "btn_account")
async def _(callback: types.CallbackQuery) -> None:
    user = ud.get_user(callback.from_user.id)

    await callback.message.edit_text(
        text("account").format(
            id=user.user_id,
            subscription_emoji={"free": "🥀", "premium": "⭐️", "premium+": "💫"}[user.subscription],
            subscription=user.subscription.capitalize(),
            subscription_until=user.subscription_until,
            quota=user.quota,
            quota_max=helpers.get_quota_max(callback.from_user.id),
            searched=user.searched,
            link=f"t.me/insomniachecker_bot?start={callback.from_user.id}",
            invited=user.invited,
            progress_bar=helpers.get_progressbar(callback.from_user.id)
        ),
        reply_markup=back_kb(),
        link_preview_options=types.link_preview_options.LinkPreviewOptions(is_disabled=True),
    )


# Sub
@router.message(F.text, Command("sub"))
async def _(message: types.Message) -> None:
    await message.answer(text("rates"), reply_markup=purchase_kb(False))


@router.callback_query(F.data == "btn_rates")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(text("rates"), reply_markup=purchase_kb(True))
