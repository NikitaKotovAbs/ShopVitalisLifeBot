import logging
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from app.product_manage import ProductManager
from app.keyboard.inline import navigation_keyboard
from app.keyboard.callback_data import ProductAction
from app.utils.db.operations.fetch_data import ProductFetcher
from .basket_handlers import show_basket
from ...utils.view_data import show_product

router = Router()
product_manager = ProductManager()


async def validate_product(callback: types.CallbackQuery, product_id: int) -> bool:
    """Проверяет существование товара"""
    juices = ProductFetcher.all_juices()
    if not juices:
        await callback.answer("Товары временно недоступны")
        return False

    if not next((juice for juice in juices if juice[0] == product_id), None):
        await callback.answer("Товар не найден")
        return False

    return True


async def update_product_keyboard(
        message: types.Message,
        product_id: int,
        user_id: int,
        bot: Bot
):
    """Обновляет клавиатуру товара"""
    juices = ProductFetcher.all_juices()
    current_qty = product_manager.get_products(user_id).get(product_id, 0)
    current_index = next((i for i, juice in enumerate(juices) if juice[0] == product_id), 0)

    try:
        await message.edit_reply_markup(
            reply_markup=navigation_keyboard(
                current_index=current_index,
                total_items=len(juices),
                item_id=product_id,
                current_qty=current_qty,
                user_id=user_id
            )
        )
    except Exception as e:
        logging.error(f"Ошибка обновления клавиатуры: {e}")
        await message.answer("Обновите сообщение")


@router.callback_query(ProductAction.filter(F.action == "add"))
async def add_product_handler(
        callback: types.CallbackQuery,
        callback_data: ProductAction,
        bot: Bot
):
    """Добавление товара в корзину"""
    if not await validate_product(callback, callback_data.product_id):
        return

    product_manager.add_product(callback.from_user.id, callback_data.product_id)
    await callback.answer("✅ Товар добавлен в корзину")
    await update_product_keyboard(callback.message, callback_data.product_id, callback.from_user.id, bot)


@router.callback_query(ProductAction.filter(F.action == "remove"))
async def remove_product_handler(
        callback: types.CallbackQuery,
        callback_data: ProductAction,
        bot: Bot
):
    """Удаление товара из корзины"""
    if not await validate_product(callback, callback_data.product_id):
        return

    product_manager.remove_product(callback.from_user.id, callback_data.product_id)
    await callback.answer("❌ Товар удалён из корзины")
    await update_product_keyboard(callback.message, callback_data.product_id, callback.from_user.id, bot)


@router.callback_query(ProductAction.filter(F.action == "view"))
async def view_basket_handler(
        callback: types.CallbackQuery,
        bot: Bot
):
    """Просмотр корзины"""
    await callback.message.delete()
    await show_basket(callback.message, callback.from_user.id)


@router.callback_query(ProductAction.filter(F.action == "clear"))
async def clear_basket_handler(
        callback: types.CallbackQuery,
        bot: Bot
):
    """Очистка корзины"""
    user_id = callback.from_user.id
    product_manager.clear_products(user_id)
    await callback.message.delete()
    await callback.message.answer("🛒 Корзина очищена")
    await show_product(
        target=callback,
        index=0,
        fetch_data_func=ProductFetcher.all_juices,
        keyboard_func=navigation_keyboard,
        bot=bot
    )


@router.callback_query(ProductAction.filter(F.action == "close_basket"))
async def close_basket_handler(
        callback: types.CallbackQuery,
        bot: Bot
):
    """Закрытие корзины"""
    await callback.message.delete()
    await callback.answer("Возвращаемся к товарам")
    await show_product(
        target=callback,
        index=0,
        fetch_data_func=ProductFetcher.all_juices,
        keyboard_func=navigation_keyboard,
        bot=bot
    )