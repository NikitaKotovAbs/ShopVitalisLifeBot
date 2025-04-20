from aiogram import Router
from .juice_handler import router as juice_router
from .order_juice import router as composition_router
from .mode_handler import router as mode_router
from .contact_handler import router as contact_router
from .my_order_handler import router as my_order_router
from .recipe_handler import router as recipe_router
from .product_handler import router as product_router
from .basket_handlers import router as basket_router
from .order_payment import router as order_payment_router
__version__ = "1.0.0"
router = Router(name=__name__)

router.include_routers(
    juice_router,
    composition_router,
    mode_router,
    contact_router,
    my_order_router,
    recipe_router,
    product_router,
    basket_router,
    order_payment_router

)
