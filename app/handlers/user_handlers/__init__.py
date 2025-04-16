from aiogram import Router
from .juice_handler import router as juice_router
from .order_juice import router as composition_router
from .mode_handler import router as mode_router
from .contact_handler import router as contact_router
from .order_handler import router as order_router
from .recipe_handler import router as recipe_router
from .product_handler import router as product_router
from .basket_handlers import router as basket_router
__version__ = "1.0.0"
router = Router(name=__name__)

router.include_routers(
    juice_router,
    composition_router,
    mode_router,
    contact_router,
    order_router,
    recipe_router,
    product_router,
    basket_router

)
