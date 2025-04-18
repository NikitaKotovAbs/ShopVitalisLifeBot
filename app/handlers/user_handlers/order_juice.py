from aiogram import Router, types
from app.keyboard.callback_data import JuiceNavigation
from app.keyboard.inline import basket_keyboard, navigation_keyboard
from app.utils.db.operations.fetch_data import ProductFetcher
from app.utils.view_data import show_product
router = Router()

@router.message(lambda msg: msg.text == "🍹 Заказать сок")
async def juice_menu(message: types.Message):
    await show_product(
        target=message,
        index=0,
        fetch_data_func=ProductFetcher.all_juices,
        keyboard_func=navigation_keyboard
    )

@router.callback_query(JuiceNavigation.filter())
async def navigate_juices(
    callback: types.CallbackQuery,
    callback_data: JuiceNavigation
):
    await show_product(
        target=callback,
        index=callback_data.current_index + 1 if callback_data.action == "next" else callback_data.current_index - 1,
        fetch_data_func=ProductFetcher.all_juices,
        keyboard_func=navigation_keyboard,
        is_admin=callback_data.is_admin
    )
    await callback.answer()



# @router.callback_query(lambda c: c.data.startswith('order:'))
# async def process_order(callback: types.CallbackQuery):
#     index = int(callback.data.split(':')[1])
#     juices = ProductFetcher.all_juices()
#     title = juices[index][0] if juices and index < len(juices) else "неизвестный товар"
#     await callback.answer(f"Вы выбрали {title}! Оформим заказ?")