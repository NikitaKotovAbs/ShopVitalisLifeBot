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
    role: str = "user"
):
    try:
        # Определяем контекст
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
        title, desc, price, image_blob = item_data[1:]

        # Формируем caption с учетом режима
        admin_prefix = "<b>🛠 Режим администратора</b>\n\n" if role in ("owner", "staff") else ""
        caption = f"{admin_prefix}<b>{title}</b>\n\n{desc}\n\n💰 Цена: {price} руб."

        # Для админки не нужно количество в корзине
        current_qty = 0 if role in ("owner", "staff") else product_manager.get_products(user_id).get(item_id, 0)

        logging.info(f"Showing product: role={role}, index={index}")

        # Создаем клавиатуру
        keyboard = keyboard_func(
            current_index=index,
            total_items=len(items),
            item_id=item_id,
            current_qty=current_qty,
            user_id=user_id,
            role=role
        )

        # Отображение
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


async def show_order_page(
    message: types.Message,
    orders: list,
    page: int,
    role: str = "user",
    edit_existing: bool = True
) -> types.Message:
    """
    Универсальная функция отображения заказа
    :param message: Объект сообщения Telegram
    :param orders: Список заказов
    :param page: Текущая страница
    :param role: Режим администратора (True/False)
    :param edit_existing: Редактировать существующее сообщение (True) или отправлять новое (False)
    :return: Объект сообщения
    """
    try:
        order = orders[page]
        total_orders = len(orders)

        # Формируем текст товаров
        products_text = "\n".join(
            f"➡️ {p['title']} x{p['quantity']} - {p['price']}₽"
            for p in order['products']
        )

        # Формируем основной текст в зависимости от режима
        if role == "staff" or role == "owner":
            order_text = (
                f"📦 Заказ #{order['id']}\n"
                f"👤 Пользователь: {order['user']['tag_telegram']}\n"
                f"📅 Дата: {order['created_at']}\n"
                f"🏠 Адрес: {order['address']}\n"
                f"🔄 Статус: {Notifier.get_status_display(order['status'])}\n"
                f"💳 Сумма: {order['total_price']}₽\n\n"
                f"🛒 Товары:\n{products_text}"
            )
        else:
            order_text = (
                f"📦 Ваш заказ #{order['id']} ({page + 1}/{total_orders})\n"
                f"📅 Дата: {order['created_at']}\n"
                f"🏠 Адрес: {order['address']}\n"
                f"🔄 Статус: {Notifier.get_status_display(order['status'])}\n"
                f"💳 Сумма: {order['total_price']}₽\n\n"
                f"🛒 Состав заказа:\n{products_text}"
            )

        # Получаем клавиатуру (должна поддерживать is_admin)
        keyboard = orders_keyboard(orders, page, role)

        # Выбираем метод отправки
        if edit_existing:
            await message.edit_text(
                text=order_text,
                reply_markup=keyboard
            )
            return message
        else:
            return await message.answer(
                text=order_text,
                reply_markup=keyboard
            )

    except IndexError:
        error_msg = "⚠️ Неверный номер заказа" if role == "staff" and role == "owner" else "⚠️ Ошибка отображения заказа"
        logging.error(f"IndexError: page={page}, orders_count={len(orders)}")
    except Exception as e:
        error_msg = "⚠️ Ошибка загрузки заказа" if role == "staff" and role == "owner" else "⚠️ Произошла ошибка"
        logging.error(f"Error showing order: {e}")

    return await message.answer(error_msg)