from aiogram import types

from app.utils.db.operations.fetch_data import ProductFetcher


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