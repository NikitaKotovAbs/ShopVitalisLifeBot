from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboard.callback_data import OrderNavigation
from app.keyboard.inline import orders_keyboard
from app.utils.db.operations.fetch_data import UserFetcher
from app.utils.notify import Notifier
import logging

from app.utils.view_data import show_order_page

router = Router()


@router.message(F.text == "🛒 Мои заказы")
async def handle_my_orders(
        message: types.Message,
        state: FSMContext
):
    try:
        # Полностью очищаем состояние
        await state.clear()

        orders = UserFetcher.get_orders_by_telegram_id(message.from_user.id)

        if not orders:
            await message.answer("📭 У вас пока нет заказов.")
            return

        await state.update_data(
            my_orders=orders,
            current_page=0,
             # Явно указываем режим пользователя
        )

        await show_order_page(
            message,
            orders,
            0,

        )

    except Exception as e:
        logging.error(f"Ошибка при загрузке заказов: {e}")
        await message.answer("⚠️ Не удалось загрузить ваши заказы")


# @router.callback_query(OrderNavigation.filter())
# async def handle_order_navigation(
#         callback: types.CallbackQuery,
#         callback_data: OrderNavigation,
#         state: FSMContext
# ):
#     try:
#         data = await state.get_data()
#
#
#         # Выбираем правильный список заказов
#         orders = data.get('my_orders', [])
#         last_message_id = data.get('last_message_id')
#
#         if not orders:
#             await callback.answer("Заказы не найдены", show_alert=True)
#             return
#
#         new_page = callback_data.page
#
#         if 0 <= new_page < len(orders):
#             try:
#                 if last_message_id:
#                     await callback.bot.delete_message(
#                         chat_id=callback.message.chat.id,
#                         message_id=last_message_id
#                     )
#             except Exception as e:
#                 logging.warning(f"Не удалось удалить сообщение: {e}")
#
#             sent_message = await show_order_page(
#                 callback.message,
#                 orders,
#                 new_page,
#
#             )
#
#             await state.update_data(
#                 current_page=new_page,
#                 last_message_id=sent_message.message_id
#             )
#         else:
#             await callback.answer("Достигнут край списка")
#
#         await callback.answer()
#     except Exception as e:
#         logging.error(f"Ошибка навигации: {e}")
#         await callback.answer("⚠️ Ошибка перехода", show_alert=True)