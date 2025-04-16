from .reply import main_menu as kb_menu
from .reply import back_basket as kb_back_basket
from .inline import staff_menu as kb_staff_menu
from .inline import edit_product_action as kb_edit_product_action
from .inline import navigation_keyboard as kb_nav
from .callback_data import JuiceNavigation as callback_data_juice_nav
__version = "1.0.0"
__all__ = ["kb_menu", "kb_back_basket", "kb_staff_menu", "kb_edit_product_action", "kb_nav", "callback_data_juice_nav"]
