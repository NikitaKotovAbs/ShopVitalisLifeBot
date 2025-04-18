import logging

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext

from app.keyboard.callback_data import OrderNavigation
from app.keyboard.inline import status_keyboard
from app.utils.db.operations.fetch_data import ProductFetcher, OrderFetcher
from app.utils.db.operations.update_data import OrderEdit
from app.utils.notify import Notifier
from app.utils.view_data import show_order_page

router = Router()


@router.callback_query(OrderNavigation.filter(F.action == "view_order"))
async def handle_view_order(
        callback: types.CallbackQuery,
        callback_data: OrderNavigation,
        state: FSMContext
):
    try:

        print(f"Получен callback: {callback_data}")  # Проверьте action и page
        data = await state.get_data()
        print(f"Данные в state: {data}")  # Убедитесь, что orders есть
        orders = data.get('all_orders', [])

        # Проверяем и корректируем page
        page = max(0, min(callback_data.page, len(orders) - 1))

        await show_order_page(callback.message, orders, page)
        await state.update_data(current_page=page)
        await callback.answer()

    except Exception as e:
        logging.error(f"Ошибка навигации: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка навигации", show_alert=True)


@router.callback_query(OrderNavigation.filter(F.action == "change_status"))
async def handle_change_status(
        callback: types.CallbackQuery,
        callback_data: OrderNavigation,
        state: FSMContext
):
    try:
        if not callback_data.order_id:
            await callback.answer("⚠️ ID заказа не указан", show_alert=True)
            return

        # Получаем текущие данные из состояния
        data = await state.get_data()
        orders = data.get('all_orders', [])

        # Проверяем, что заказ существует
        order_exists = any(order['id'] == callback_data.order_id for order in orders)
        if not order_exists:
            await callback.answer("⚠️ Заказ не найден в текущем списке", show_alert=True)
            return

        await callback.message.edit_reply_markup(
            reply_markup=status_keyboard(callback_data.order_id)
        )
        await callback.answer()

    except Exception as e:
        logging.error(f"Ошибка при изменении статуса: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка при изменении статуса", show_alert=True)


@router.callback_query(OrderNavigation.filter(F.action == "set_status"))
async def handle_set_status(
        callback: types.CallbackQuery,
        callback_data: OrderNavigation,
        state: FSMContext,
        bot: Bot
):
    try:
        if not callback_data.order_id or not callback_data.status:
            await callback.answer("⚠️ Не указаны ID заказа или статус", show_alert=True)
            return

        data = await state.get_data()
        orders = data.get('all_orders', [])
        current_page = data.get('current_page', 0)

        # Находим заказ в локальном списке
        current_order = next(
            (order for order in orders if order['id'] == callback_data.order_id),
            None
        )

        if not current_order:
            await callback.answer("⚠️ Заказ не найден в локальных данных", show_alert=True)
            return

        # Получаем информацию о заказе из БД
        order_info = OrderFetcher.get_order_user_info(callback_data.order_id)
        if not order_info:
            await callback.answer("⚠️ Заказ не найден в базе данных", show_alert=True)
            return

        # Сохраняем старый статус
        old_status = current_order['status']

        # Обновляем статус в БД
        if not OrderEdit.update_order_status(callback_data.order_id, callback_data.status):
            await callback.answer("⚠️ Не удалось изменить статус в БД", show_alert=True)
            return

        # Обновляем локальные данные
        current_order['status'] = callback_data.status
        await state.update_data(all_orders=orders)

        # Отправляем уведомление
        await Notifier.notify_order_status_changed(
            bot=bot,
            user_id=order_info['user_id'],
            order_id=callback_data.order_id,
            old_status=old_status,  # Используем локальный старый статус
            new_status=callback_data.status
        )

        # Обновляем сообщение
        await show_order_page(callback.message, orders, current_page)
        await callback.answer(f"Статус изменен на: {callback_data.status}")

    except Exception as e:
        logging.error(f"Ошибка установки статуса: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка изменения статуса", show_alert=True)


@router.callback_query(OrderNavigation.filter(F.action == "back_order"))
async def handle_back_order(
        callback: types.CallbackQuery,
        state: FSMContext
):
    try:
        # Получаем сохраненные заказы из состояния
        data = await state.get_data()
        orders = data.get('all_orders', [])

        # Если заказов нет в состоянии, загружаем заново
        if not orders:
            orders = ProductFetcher.get_all_orders()
            await state.update_data(all_orders=orders)

        # Редактируем текущее сообщение, показывая первый заказ
        await show_order_page(callback.message, orders, 0)
        await callback.answer()

    except Exception as e:
        logging.error(f"Ошибка при возврате к списку заказов: {e}")
        await callback.answer("⚠️ Ошибка при возврате к списку заказов", show_alert=True)