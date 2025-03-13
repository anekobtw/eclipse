from aiogram import Router

from . import commands, pages, search

router = Router()
router.include_router(commands.router)
router.include_router(search.router)
router.include_router(pages.router)
