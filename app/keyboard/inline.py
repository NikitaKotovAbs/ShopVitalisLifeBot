from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.keyboard.callback_data import JuiceNavigation, ProductAction, StaffAction, OrderNavigation
from app.product_manage import ProductManager
product_manager = ProductManager()


def navigation_keyboard(
        current_index: int,
        total_items: int,
        item_id: int,
        current_qty: int,
        user_id: int,
        is_admin: bool = False
):
    builder = InlineKeyboardBuilder()

    match is_admin:
        case True:
            builder.button(text="🗑 Удалить", callback_data=StaffAction(action="delete", product_id=item_id))
            builder.button(text="✏️ Добавить", callback_data=StaffAction(action="add", product_id=item_id))
            builder.button(text="Вернуться в меню", callback_data=StaffAction(action="back_staff_menu"))
        case False:
            # Кнопки корзины
            if current_qty > 0:
                builder.button(
                    text="➖",
                    callback_data=ProductAction(action="remove", product_id=item_id)
                )

            builder.button(
                text=f"➕({current_qty})" if current_qty > 0 else "➕",
                callback_data=ProductAction(action="add", product_id=item_id)
            )
            # Исправленная строка - используем product_manager вместо ProductAction
            product_has_items = any(qty > 0 for qty in product_manager.get_products(user_id).values()) if user_id else False
            if product_has_items:
                builder.button(
                    text="🛒 Корзина",
                    callback_data=ProductAction(action="view")
                )

    # Кнопки навигации
    if current_index > 0:
        builder.button(
            text="⬅️ Назад",
            callback_data=JuiceNavigation(action="prev", current_index=current_index, is_admin=is_admin)
        )

    if current_index < total_items - 1:
        builder.button(
            text="Вперёд ➡️",
            callback_data=JuiceNavigation(action="next", current_index=current_index, is_admin=is_admin)
        )
    # Распределение кнопок
    nav_buttons = 2 if (current_index > 0 and current_index < total_items - 1) else 1
    builder.adjust(nav_buttons, 2 if current_qty > 0 else 1, 1)

    return builder.as_markup()


def basket_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🧹 Очистить", callback_data=ProductAction(action="clear"))
    builder.button(text="✅ Оформить", callback_data=ProductAction(action="checkout"))
    builder.button(text="🔙 Назад",callback_data=ProductAction(action="close_basket"))
    builder.adjust(2, 1)
    return builder.as_markup()


def staff_menu(
    role: str
):
    builder = InlineKeyboardBuilder()

    if role == "owner":
        builder.button(
            text="Товары",
            callback_data=StaffAction(action="edit_products")
        )
        builder.button(
            text="Рассылка",
            callback_data=StaffAction(action="mailing")
        )
        builder.button(
            text="Заказы",
            callback_data=StaffAction(action="orders")
        )
        builder.button(
            text="⬅️ Назад",
            callback_data=StaffAction(action="back_main_menu")
        )
    return builder.as_markup()


def orders_keyboard(orders: list, current_page: int, is_admin: bool = False):
    builder = InlineKeyboardBuilder()

    # Кнопки навигации
    if current_page > 0:
        builder.button(
            text="⬅️ Предыдущий",
            callback_data=OrderNavigation(action="view_order", page=current_page - 1, is_admin=is_admin)
        )

    if current_page < len(orders) - 1:
        builder.button(
            text="Следующий ➡️",
            callback_data=OrderNavigation(action="view_order", page=current_page + 1, is_admin=is_admin)
        )

    if is_admin:
        # Кнопка изменения статуса
        builder.button(
            text="Изменить статус",
            callback_data=OrderNavigation(action="change_status", order_id=orders[current_page]['id'])
        )

        builder.button(
            text="Вернуться в меню",
            callback_data=StaffAction(action="back_staff_menu")
        )

    builder.adjust(2, 1)
    return builder.as_markup()


def status_keyboard(order_id: int):
    builder = InlineKeyboardBuilder()

    statuses = {
        "processing": "В обработке",
        "delivering": "В доставке",
        "delivered": "Доставлен",
        "completed": "Выполнен"
    }

    for status, text in statuses.items():
        builder.button(
            text=text,
            callback_data=OrderNavigation(
                action="set_status",
                order_id=order_id,
                status=status
            )
        )

    builder.button(
        text="Назад",
        callback_data=OrderNavigation(action="back_order")
    )

    builder.adjust(1)  # По одной кнопке в строке
    return builder.as_markup()

def edit_product_action():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Удалить",
        callback_data=StaffAction(action="delete_product")
    )
    return builder.as_markup()