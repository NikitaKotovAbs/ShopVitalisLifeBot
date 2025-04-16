from aiogram import Router
from .commands import router as commands_router
from .messages import router as messages_router
from .callbacks import router as callbacks_router
from .user_handlers import router as user_handlers
from .admin_handlers import router as admin_handler

__version = "1.0.0"

router = Router(name=__name__)

router.include_routers(
    commands_router,
    callbacks_router,
    user_handlers,
    admin_handler
)
