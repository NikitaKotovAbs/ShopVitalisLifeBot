from aiogram import Router, types
from aiogram.filters import Command
import logging
from decimal import Decimal

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