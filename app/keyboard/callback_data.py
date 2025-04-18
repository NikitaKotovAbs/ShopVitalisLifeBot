from sys import prefix

from aiogram.filters.callback_data import CallbackData

class JuiceNavigation(CallbackData, prefix="juice"):
    action: str  # "prev" или "next"
    current_index: int
    is_admin: bool = False

class ProductAction (CallbackData, prefix="product"):
    action: str # "add" | "remove" | "view" | "clear" | "checkout"
    product_id: int = 0 # ID товара

class CloseBasket (CallbackData, prefix="close_basket"):
    action: str # "add" | "remove" | "view" | "clear" | "checkout"

class StaffAction(CallbackData, prefix="staff"):
    action: str
    product_id: int = 0

class OrderNavigation(CallbackData, prefix="order_nav"):
    action: str
    order_id: int | None = None
    page: int | None = None
    status: str | None = None

