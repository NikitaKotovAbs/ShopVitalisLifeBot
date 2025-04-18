from aiogram import Router
from .staff_handler import router as staff_router
from .mailing_handle import router as mailing_router
from .edit_products_handler import router as edit_products_router
from .add_product_handler import router as add_products_router
from .order_handler import router as order_handler_router

__version__ = "1.0.0"
router = Router(name=__name__)

router.include_routers(
    staff_router,
    mailing_router,
    edit_products_router,
    add_products_router,
    order_handler_router
)
