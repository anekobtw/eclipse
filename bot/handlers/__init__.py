from aiogram import Router

from . import commands, common, pages

router = Router()
router.include_router(commands.router)
router.include_router(common.router)
router.include_router(pages.router)
