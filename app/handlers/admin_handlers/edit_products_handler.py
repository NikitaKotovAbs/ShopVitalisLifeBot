import logging

from aiogram.types import ReplyKeyboardRemove

from app.keyboard import kb_staff_menu
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.keyboard import kb_nav
from app.handlers.admin_handlers.add_product_handler import AddProductStates
from app.keyboard.callback_data import StaffAction
from app.utils.db.operations.fetch_data import ProductFetcher, UserFetcher
from app.utils.db.operations.remove_data import ProductRemoved
from app.utils.view_data import show_product

router = Router()

@router.callback_query(StaffAction.filter(F.action == "add"))
async def handle_add_product_callback(
    callback: types.CallbackQuery,
    state: FSMContext
):
    try:
        await callback.message.answer(
            "Введите название нового продукта:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(AddProductStates.waiting_for_title)
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка начала добавления продукта: {e}")
        await callback.answer("⚠️ Ошибка начала добавления продукта", show_alert=True)

@router.callback_query(StaffAction.filter(F.action == "delete"))
async def handle_delete_product_callback(
        callback: types.CallbackQuery,
        callback_data: StaffAction
):
    try:
        product_id = callback_data.product_id
        # Удаляем продукт
        success = ProductRemoved.remove_product_by_id(product_id)
        if success:
            # Получаем обновленный список продуктов
            products = ProductFetcher.all_juices()
            # Определяем новый индекс (либо 0, либо предыдущий - 1)
            new_index = 0  # или можно сохранить текущий индекс и скорректировать

            if products:  # Если остались продукты после удаления
                await show_product(
                    target=callback,
                    index=new_index,
                    fetch_data_func=ProductFetcher.all_juices,
                    keyboard_func=kb_nav,
                    is_admin=True
                )
                await callback.answer("✅ Продукт удален")
            else:
                # Если продукты закончились
                await callback.message.edit_text(
                    "🛒 Товары закончились",
                    reply_markup=kb_staff_menu(role="owner")  # Возврат в меню админа
                )
                await callback.answer("✅ Последний продукт удален")
        else:
            await callback.answer("⚠️ Не удалось удалить продукт", show_alert=True)

    except Exception as e:
        logging.error(f"Ошибка при удалении продукта: {e}")
        await callback.answer("⚠️ Ошибка при удалении продукта", show_alert=True)


@router.callback_query(StaffAction.filter(F.action == "back_staff_menu"))
async def handle_back_staff_menu_callback(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    user_data = UserFetcher.get_user_by_telegram_id(telegram_id)

    if not user_data:
        await callback.answer("Ошибка: данные пользователя не найдены", show_alert=True)
        return

    try:
        if user_data.get('is_owner'):
            # Удаляем предыдущее сообщение с кнопками (если нужно)
            await callback.message.delete()

            # Отправляем новое сообщение
            await callback.message.answer(
                "Вы зашли в панель персонала как Админ",
                reply_markup=ReplyKeyboardRemove()
            )

            # Отправляем inline-клавиатуру
            await callback.message.answer(
                "Выберите действие:",
                reply_markup=kb_staff_menu(role="owner")
            )

        elif user_data.get('is_staff'):
            await callback.message.delete()
            await callback.message.answer(
                "Вы зашли в панель персонала как Сотрудник",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await callback.message.delete()
            await callback.message.answer(
                "У вас нет доступа к staff-панели",
                reply_markup=ReplyKeyboardRemove()
            )

        await callback.answer()

    except Exception as e:
        logging.error(f"Ошибка входа в админ-панель: {e}")
        await callback.answer("⚠️ Ошибка входа в админ-панель", show_alert=True)