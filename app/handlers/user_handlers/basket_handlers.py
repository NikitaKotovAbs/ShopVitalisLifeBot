from aiogram import Router, types, F
from aiogram.filters import Command
import logging
from decimal import Decimal

from app.keyboard.callback_data import ProductAction
from app.product_manage import ProductManager
from app.keyboard.inline import basket_keyboard
from app.utils.db.operations.fetch_data import ProductFetcher

router = Router()
product_manager = ProductManager()

async def show_basket(message: types.Message, user_id: int):
    try:
        products = product_manager.get_products(user_id)
        if not products:
            await message.answer("🛒 Ваша корзина пуста")
            return

        items = ProductFetcher.get_juices_by_ids(list(products.keys()))
        if not items:
            await message.answer("⚠️ Не удалось загрузить информацию о товарах")
            return

        total = Decimal('0')
        text = "🛒 *Ваша корзина*\n\n"

        for product_id, quantity in products.items():
            if product_id not in items:
                continue

            title, _, price, _ = items[product_id]
            item_total = Decimal(str(price)) * quantity
            total += item_total
            text += f"▪️ {title}\n   {quantity} × {float(price):.2f}₽ = {float(item_total):.2f}₽\n"

        text += f"\n💵 *Итого: {float(total):.2f}₽*"

        await message.answer(
            text=text,
            reply_markup=basket_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Ошибка отображения корзины: {e}")
        await message.answer("⚠️ Не удалось загрузить корзину")

@router.message(Command("basket"))
async def basket_command(message: types.Message):
    await show_basket(message, message.from_user.id)


# @router.callback_query(ProductAction.filter(F.action == "checkout"))
# async def process_order(callback: types.CallbackQuery):
#     print("Я вошёл в обработчик")
#     try:
#         print("Я вошёл в обработчик")
#         # 1. Сначала отвечаем на callback (обязательно)
#         await callback.answer("🔄 Начинаем оформление заказа...")
#
#         # 2. Редактируем текущее сообщение с корзиной
#         await callback.message.edit_text(
#             "✅ Заказ принят в обработку!\n\n"
#             "Мы готовим ваш заказ к отправке. Ожидайте уведомления.",
#             reply_markup=None  # Убираем клавиатуру после оформления
#         )
#
#         # 3. Дополнительно можно отправить новое сообщение с деталями
#         # await callback.message.answer("Детали заказа: ...")
#
#     except Exception as e:
#         logging.error(f"Ошибка при оформлении заказа: {e}")
#         await callback.answer("⚠️ Ошибка оформления", show_alert=True)