import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from app.handlers.admin_handlers.add_product_handler import AddProductStates
from app.keyboard import kb_staff_menu
from app.keyboard import kb_menu
from app.handlers.admin_handlers.mailing_handle import MailingStates
from app.keyboard.inline import staff_menu
from app.keyboard.callback_data import StaffAction, JuiceNavigation, OrderNavigation
from app.utils.db.operations.fetch_data import ProductFetcher, UserFetcher
from app.utils.db.operations.remove_data import ProductRemoved
from app.utils.view_data import show_product, show_order_page
from app.keyboard import kb_nav
from app.keyboard import kb_order
router = Router()

@router.callback_query(StaffAction.filter(F.action == "mailing"))
async def handle_mailing_callback(
    callback: types.CallbackQuery,
    state: FSMContext
):
    try:
        await callback.message.delete()  # Удаляем сообщение с кнопками
        await callback.message.answer(
            "✉️ Введите сообщение для рассылки:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(MailingStates.waiting_for_message)
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка запуска рассылки: {e}")
        await callback.answer("⚠️ Ошибка запуска рассылки", show_alert=True)


@router.callback_query(StaffAction.filter(F.action == "back_main_menu"))
async def handle_mailing_callback(
    callback: types.CallbackQuery
):
    try:
        await callback.message.delete()  # Удаляем сообщение с кнопками
        await callback.message.answer(
            "✉️ Выход в главное меню",
            reply_markup=kb_menu()
        )
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка при выходе в главное меню: {e}")
        await callback.answer("⚠️ Ошибка при выходе в главное меню", show_alert=True)

@router.callback_query(StaffAction.filter(F.action == "edit_products"))
async def handle_edit_product_callback(callback: types.CallbackQuery):
    try:
        await show_product(
            target=callback,
            index=0,
            fetch_data_func=ProductFetcher.all_juices,
            keyboard_func=kb_nav,
            is_admin=True  # Устанавливаем флаг при входе в админку
        )
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка входа в админ-панель: {e}")
        await callback.answer("⚠️ Ошибка входа в админ-панель", show_alert=True)



# -----------------------------------------------------------------------------------------
@router.callback_query(StaffAction.filter(F.action == "orders"))
async def handle_orders_callback(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await state.clear()
    try:
        orders = ProductFetcher.get_all_orders()

        if not orders:
            await callback.answer("Нет доступных заказов", show_alert=True)
            return

        # Сохраняем заказы и текущую страницу в состоянии
        await state.update_data(
            all_orders=orders,
            current_page=0,
            is_admin=True
        )
        print(await state.get_data())  # Убедитесь, что данные есть

        # Отображаем первый заказ
        await show_order_page(
            callback.message,
            orders,
            0,
            is_admin=True
        )
        await callback.answer()

    except Exception as e:
        logging.error(f"Ошибка при загрузке заказов: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка загрузки заказов", show_alert=True)
# -----------------------------------------------------------------------------------------




