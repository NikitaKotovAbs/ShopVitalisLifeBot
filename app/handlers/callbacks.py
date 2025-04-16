from aiogram import Router, types, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery


router = Router(name="callbacks_router")

# class JuiceNavigation(CallbackData, prefix="juice"):
#     action: str  # "prev" или "next"
#     current_index: int

# @router.callback_query()
# async def handle_callback(callback: types.CallbackQuery):
#     await callback.answer("Кнопка нажата!")
#
# @router.callback_query(JuiceNavigation.filter(F.action == "next"))
# async def next_item(callback: CallbackQuery, callback_data: JuiceNavigation):
#     """Обработка кнопки 'Вперёд'"""
#     new_index = callback_data.current_index + 1
#     await show_juice(callback.message, new_index)
#     await callback.answer()  # Убираем часики на кнопке

# @router.callback_query(JuiceNavigation.filter(F.action == "prev"))
# async def prev_item(callback: CallbackQuery, callback_data: JuiceNavigation):
#     """Обработка кнопки 'Назад'"""
#     new_index = callback_data.current_index - 1
#     await show_juice(callback.message, new_index)
#     await callback.answer()