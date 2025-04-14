from aiogram import F, Router, types
from aiogram.filters import Command, CommandObject, CommandStart

from enums import Databases, Keyboards, Messages
from handlers import helpers

router = Router()


# Start
@router.message(CommandStart(deep_link=True))
async def _(message: types.Message, command: CommandObject) -> None:
    user = Databases.USERS.value.get_user(message.from_user.id)

    if command.args.isdigit():
        # Got that from a user
        if user is None:
            Databases.USERS.value.add_user(message.from_user.id, 1, 0)
            referal = Databases.USERS.value.get_user(int(command.args))
            Databases.USERS.value.update_user(int(command.args), "quota", referal[1] + 5)

    else:
        # It's a premium referral link
        Databases.USERS.value.add_user(message.from_user.id, 1, 0)

        ref = Databases.REFERRALS.value.get_referral(command.args)
        if ref:
            Databases.USERS.value.update_user(message.from_user.id, "quota", user[1] + ref[1])
            Databases.REFERRALS.value.delete_referral(command.args)

    await message.answer(Messages.WELCOME.value.format(searched=helpers.get_all_time_searched()), reply_markup=Keyboards.start())


@router.message(F.text, Command("menu", "start"))
async def _(message: types.Message) -> None:
    Databases.USERS.value.add_user(message.from_user.id, 1, 0)
    await message.answer(Messages.WELCOME.value.format(searched=helpers.get_all_time_searched()), reply_markup=Keyboards.start())


@router.callback_query(F.data == "btn_back")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(Messages.WELCOME.value.format(searched=helpers.get_all_time_searched()), reply_markup=Keyboards.start())


# Search
@router.message(F.text, Command("search"))
async def _(message: types.Message) -> None:
    await message.answer(Messages.SEARCH.value)


@router.callback_query(F.data == "btn_search")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(Messages.SEARCH.value, reply_markup=Keyboards.back())


# Support
@router.message(F.text, Command("support"))
async def _(message: types.Message) -> None:
    await message.answer(Messages.SUPPORT.value, reply_markup=Keyboards.support(False), link_preview_options=types.link_preview_options.LinkPreviewOptions(is_disabled=True))


@router.callback_query(F.data == "btn_support")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(Messages.SUPPORT.value, reply_markup=Keyboards.support(True), link_preview_options=types.link_preview_options.LinkPreviewOptions(is_disabled=True))


# Account
@router.message(F.text, Command("account"))
async def _(message: types.Message) -> None:
    user = Databases.USERS.value.get_user(message.from_user.id)

    await message.answer(
        Messages.ACCOUNT.value.format(
            id=user[0],
            quota=user[1],
            searched=user[2],
            link=f"t.me/insomniachecker_bot?start={message.from_user.id}",
        ),
        link_preview_options=types.link_preview_options.LinkPreviewOptions(is_disabled=True),
    )


@router.callback_query(F.data == "btn_account")
async def _(callback: types.CallbackQuery) -> None:
    user = Databases.USERS.value.get_user(callback.from_user.id)

    await callback.message.edit_text(
        Messages.ACCOUNT.value.format(
            id=user[0],
            quota=user[1],
            searched=user[2],
            link=f"t.me/insomniachecker_bot?start={callback.from_user.id}",
        ),
        reply_markup=Keyboards.back(),
        link_preview_options=types.link_preview_options.LinkPreviewOptions(is_disabled=True),
    )


# Sub
@router.message(F.text, Command("sub"))
async def _(message: types.Message) -> None:
    await message.answer(Messages.RATES.value, reply_markup=Keyboards.purchase(False))


@router.callback_query(F.data == "btn_rates")
async def _(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(Messages.RATES.value, reply_markup=Keyboards.purchase(True))
