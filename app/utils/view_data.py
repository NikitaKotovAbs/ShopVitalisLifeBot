import logging
from aiogram import Router, types, F
from aiogram.types import BufferedInputFile, InputMediaPhoto, Message, Chat, CallbackQuery
from aiogram import Bot
from app.keyboard import kb_order
from app.keyboard.inline import orders_keyboard
from app.product_manage import ProductManager
from app.keyboard.callback_data import ProductAction
from app.utils.notify import Notifier

product_manager = ProductManager()

async def show_product(
    target: Message | CallbackQuery | Chat,
    index: int,
    fetch_data_func: callable,
    keyboard_func: callable,
    bot: Bot = None,
    is_admin: bool = False  # Новый параметр для режима админки
):
    try:
        # Определяем контекст (остается без изменений)
        if isinstance(target, CallbackQuery):
            message = target.message
            chat = message.chat
            user_id = target.from_user.id
        elif isinstance(target, Message):
            message = target
            chat = target.chat
            user_id = target.from_user.id
        else:  # Chat
            message = None
            chat = target
            user_id = None
            if bot is None:
                raise ValueError("Bot instance required when target is Chat")

        # Получаем данные
        items = fetch_data_func()
        if not items:
            if message:
                await message.answer("🍹 Товары закончились!")
            else:
                await bot.send_message(chat.id, "🍹 Товары закончились!")
            return

        # Проверка границ индекса
        index = max(0, min(index, len(items) - 1))
        item_data = items[index]

        # Предполагаем, что первый элемент - ID товара
        item_id = item_data[0]
        title, desc, price, image_blob = item_data[1:]  # Остальные данные

        # Формируем caption с учетом режима
        caption = (
            f"<b>🛠 Режим администратора</b>\n\n<b>{title}</b>\n\n{desc}\n\n💰 Цена: {price} руб.\n" if is_admin else "" +
            f"<b>{title}</b>\n\n{desc}\n\n💰 Цена: {price} руб."
        )

        # Для админки не нужно количество в корзине
        current_qty = 0 if is_admin else product_manager.get_products(user_id).get(item_id, 0)

        logging.info(f"Showing product: is_admin={is_admin}, index={index}")

        # Создаем соответствующую клавиатуру
        keyboard = keyboard_func(
            current_index=index,
            total_items=len(items),
            item_id=item_id,
            current_qty=current_qty,
            user_id=user_id,
            is_admin=is_admin  # Передаем флаг в генератор клавиатуры
        )

        # Остальная логика отображения (без изменений)
        if image_blob:
            if message and message.photo:
                await message.edit_media(
                    media=InputMediaPhoto(
                        media=BufferedInputFile(image_blob, filename="product.png"),
                        caption=caption,
                        parse_mode="HTML"
                    ),
                    reply_markup=keyboard
                )
            else:
                sender = message.answer_photo if message else bot.send_photo
                await sender(
                    photo=BufferedInputFile(image_blob, filename="product.png"),
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
        else:
            if message:
                await message.edit_text(
                    text=caption,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await bot.send_message(
                    chat_id=chat.id,
                    text=caption,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )

    except Exception as e:
        logging.error(f"Ошибка показа товара: {e}", exc_info=True)
        if message:
            await message.answer("⚠️ Ошибка при загрузке товара")
        else:
            await bot.send_message(chat.id, "⚠️ Ошибка при загрузке товара")


async def show_order_page(message: types.Message, orders: list, page: int):
    order = orders[page]

    products_text = "\n".join(
        f"➡️ {p['title']} x{p['quantity']} - {p['price']}₽"
        for p in order['products']
    )

    order_text = (
        f"📦 Заказ #{order['id']}\n"
        f"👤 Пользователь: {order['user']['tag_telegram']}\n"
        f"📅 Дата: {order['created_at']}\n"
        f"🏠 Адрес: {order['address']}\n"
        f"🔄 Статус: {Notifier.get_status_display(order['status'])}\n"
        f"💳 Сумма: {order['total_price']}₽\n\n"
        f"🛒 Товары:\n{products_text}"
    )

    await message.edit_text(
        text=order_text,
        reply_markup=orders_keyboard(orders, page)
    )

async def show_user_order(
        message: types.Message,
        orders: list,
        page: int
) -> types.Message:
    """Отображает заказ пользователя и возвращает объект сообщения"""
    try:
        order = orders[page]
        total_orders = len(orders)

        products_text = "\n".join(
            f"➡️ {p['title']} x{p['quantity']} - {p['price']}₽"
            for p in order['products']
        )

        order_text = (
            f"📦 Ваш заказ #{order['id']} ({page + 1}/{total_orders})\n"
            f"📅 Дата: {order['created_at']}\n"
            f"🏠 Адрес: {order['address']}\n"
            f"🔄 Статус: {Notifier.get_status_display(order['status'])}\n"
            f"💳 Сумма: {order['total_price']}₽\n\n"
            f"🛒 Состав заказа:\n{products_text}"
        )

        keyboard = orders_keyboard(orders, page)

        # Всегда отправляем новое сообщение
        return await message.answer(
            text=order_text,
            reply_markup=keyboard
        )

    except IndexError:
        logging.error(f"Неверный индекс заказа: {page}")
        return await message.answer("⚠️ Ошибка отображения заказа")
    except Exception as e:
        logging.error(f"Ошибка отображения заказа: {e}")
        return await message.answer("⚠️ Произошла ошибка")