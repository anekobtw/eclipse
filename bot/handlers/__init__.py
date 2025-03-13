from aiogram import Router

from . import admin, commands, pages, search

router = Router()
router.include_router(admin.router)
router.include_router(commands.router)
router.include_router(search.router)
router.include_router(pages.router)
