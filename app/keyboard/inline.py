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
        role: str = "user"
):
    builder = InlineKeyboardBuilder()

    if role in ("owner", "staff"):
        builder.button(text="🗑️ Удалить", callback_data=StaffAction(action="delete", product_id=item_id))
        builder.button(text="✏️ Редактировать", callback_data=StaffAction(action="add", product_id=item_id))
        builder.button(text="🔙 В меню", callback_data=StaffAction(action="back_staff_menu"))
        builder.adjust(2, 1)  # 2 кнопки в первом ряду, 1 во втором

    # Пользовательские кнопки
    if role == "user":
        # Кнопки управления количеством
        if current_qty > 0:
            builder.button(text="➖ Убрать", callback_data=ProductAction(action="remove", product_id=item_id))

        builder.button(
            text=f"➕ Добавить ({current_qty})" if current_qty > 0 else "➕ Добавить",
            callback_data=ProductAction(action="add", product_id=item_id)
        )

        # Кнопка корзины
        if any(qty > 0 for qty in product_manager.get_products(user_id).values()):
            builder.button(text="🛒 В корзину", callback_data=ProductAction(action="view"))

    # Навигация между товарами
    if current_index > 0:
        builder.button(text="⬅️ Назад",
        callback_data=JuiceNavigation(action="prev", current_index=current_index, role=role))

    if current_index < total_items - 1:
        builder.button(text="Вперёд ➡️",
        callback_data=JuiceNavigation(action="next", current_index=current_index, role=role))

        # Группировка кнопок
    builder.adjust(2 if current_qty > 0 else 1, 1,
        2 if (current_index > 0 and current_index < total_items - 1) else 1)

    return builder.as_markup()


def basket_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🧹 Очистить корзину", callback_data=ProductAction(action="clear"))
    builder.button(text="✅ Оформить заказ", callback_data=ProductAction(action="checkout"))
    builder.button(text="🔙 Продолжить покупки", callback_data=ProductAction(action="close_basket"))
    builder.adjust(1, 2)  # Очистить отдельно, остальные в ряд
    return builder.as_markup()


def staff_menu(role: str):
    builder = InlineKeyboardBuilder()

    if role in ("owner", "staff"):
        builder.button(text="🛍️ Управление товарами", callback_data=StaffAction(action="edit_products"))
        builder.button(text="📢 Создать рассылку", callback_data=StaffAction(action="mailing"))
        builder.button(text="📦 Просмотр заказов", callback_data=StaffAction(action="orders"))

        if role == "owner":
            builder.button(text="👥 Управление персоналом", callback_data=StaffAction(action="add_staff"))

        builder.button(text="⬅️ В главное меню", callback_data=StaffAction(action="back_main_menu"))

        # Группировка кнопок
        if role == "owner":
            builder.adjust(1, 2, 1, 1)  # Для владельца
        else:
            builder.adjust(1, 2, 1)  # Для персонала

    return builder.as_markup()


def orders_keyboard(orders: list, current_page: int, role: str = "user"):
    builder = InlineKeyboardBuilder()

    # Навигация по заказам
    if current_page > 0:
        builder.button(text="⬅️ Предыдущий",
                       callback_data=OrderNavigation(action="view_order", page=current_page - 1, role=role))

    if current_page < len(orders) - 1:
        builder.button(text="Следующий ➡️",
                       callback_data=OrderNavigation(action="view_order", page=current_page + 1, role=role))

    # Функции для персонала
    if role in ("staff", "owner"):
        builder.button(text="🔄 Изменить статус",
                       callback_data=OrderNavigation(action="change_status", order_id=orders[current_page]['id']))
        builder.button(text="🔙 В меню", callback_data=StaffAction(action="back_staff_menu"))

    builder.adjust(2, 2)  # Навигация и функции в разных рядах
    return builder.as_markup()


def status_keyboard(order_id: int):
    builder = InlineKeyboardBuilder()

    statuses = [
        ("🔄 В обработке", "processing"),
        ("🚚 В доставке", "delivering"),
        ("📦 Доставлен", "delivered"),
        ("✅ Выполнен", "completed")
    ]

    for text, status in statuses:
        builder.button(text=text, callback_data=OrderNavigation(action="set_status", order_id=order_id, status=status))

    builder.button(text="🔙 Назад к заказу", callback_data=OrderNavigation(action="back_order"))

    builder.adjust(1)  # Все кнопки в столбик
    return builder.as_markup()


def edit_product_action():
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑️ Удалить товар", callback_data=StaffAction(action="delete_product"))
    builder.button(text="✏️ Изменить данные", callback_data=StaffAction(action="edit_product"))
    builder.adjust(1)  # Кнопки в столбик
    return builder.as_markup()