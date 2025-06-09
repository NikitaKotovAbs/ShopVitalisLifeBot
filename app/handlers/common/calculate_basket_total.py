from decimal import Decimal
from typing import Optional
import logging
from app.utils.db.operations.fetch_data import ProductFetcher
from app.utils.view_data import product_manager

logger = logging.getLogger(__name__)

async def calculate_basket_total(user_id: int) -> Optional[int]:
    """Вычисляет сумму корзины в копейках"""
    try:
        basket = product_manager.get_products(user_id)
        if not basket:
            return None

        items = ProductFetcher.get_juices_by_ids(list(basket.keys()))
        if not items:
            return None

        total = Decimal('0')
        for product_id, quantity in basket.items():
            if product_id in items:
                _, _, price, _ = items[product_id]
                total += Decimal(str(price)) * quantity

        return int(total * 100)  # Конвертируем в копейки
    except Exception as e:
        logger.error(f"Ошибка расчета суммы корзины: {e}")
        return None