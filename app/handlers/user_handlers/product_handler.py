from aiogram import Router, types
import logging
from app.product_manage import ProductManager
from app.keyboard.inline import navigation_keyboard
from app.keyboard.callback_data import ProductAction
from app.utils.db.operations.fetch_data import ProductFetcher
from aiogram import Bot
from .basket_handlers import show_basket
from ...utils.view_products import show_product

router = Router()
product_manager = ProductManager()

@router.callback_query(ProductAction.filter())
async def handle_product_actions(
        callback: types.CallbackQuery,
        callback_data: ProductAction,
        bot: Bot
):
    try:
        user_id = callback.from_user.id
        message = callback.message

        # Перенесите проверку только для действий, требующих product_id
        if callback_data.action in ["add", "remove"]:  # Только эти действия нуждаются в проверке товара
            juices = ProductFetcher.all_juices()
            if not juices:
                await callback.answer("Товары временно недоступны")
                return

            current_item = next((juice for juice in juices if juice[0] == callback_data.product_id), None)
            if not current_item:
                await callback.answer("Товар не найден")
                return

        match callback_data.action:
            case "add":
                product_manager.add_product(user_id, callback_data.product_id)
                await callback.answer("✅ Товар добавлен в корзину")

            case "remove":
                product_manager.remove_product(user_id, callback_data.product_id)
                await callback.answer("❌ Товар удалён из корзины")

            case "view":
                await message.delete()
                await show_basket(message, user_id)
                return

            case "clear":
                product_manager.clear_products(user_id)
                await message.delete()
                await message.answer("🛒 Корзина очищена")
                await show_product(
                    target=callback,
                    index=0,  # Показываем первый товар
                    fetch_data_func=ProductFetcher.all_juices,
                    keyboard_func=navigation_keyboard,
                    bot=bot  # Нужно передать экземпляр бота
                )
                return

            case "close_basket":
                await message.delete()
                await callback.answer("Возвращаемся к товарам")
                await show_product(
                    target=callback,
                    index=0,  # Показываем первый товар
                    fetch_data_func=ProductFetcher.all_juices,
                    keyboard_func=navigation_keyboard,
                    bot=bot  # Нужно передать экземпляр бота
                )
                return

            # case "checkout":
            #     await process_checkout(message, user_id)
            #     await callback.answer()
            #     return

        # Обновление клавиатуры только для add/remove
        if callback_data.action in ["add", "remove"]:
            juices = juices or ProductFetcher.all_juices()
            current_qty = product_manager.get_products(user_id).get(callback_data.product_id, 0)
            current_index = next((i for i, juice in enumerate(juices) if juice[0] == callback_data.product_id), 0)

            try:
                await message.edit_reply_markup(
                    reply_markup=navigation_keyboard(
                        current_index=current_index,
                        total_items=len(juices),
                        item_id=callback_data.product_id,
                        current_qty=current_qty,
                        user_id=user_id
                    )
                )
            except Exception as e:
                logging.error(f"Ошибка обновления клавиатуры: {e}")
                await callback.answer("Обновите сообщение")

    except Exception as e:
        logging.error(f"Ошибка обработки действия: {e}", exc_info=True)
        await callback.answer("⚠️ Произошла ошибка, попробуйте позже")