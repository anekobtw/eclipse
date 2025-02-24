from aiogram import Router

from . import commands, common

router = Router()
router.include_router(commands.router)
router.include_router(common.router)
