import logging
import os
import sqlite3


class ProductRemoved:
    @classmethod
    def remove_product_by_id(cls, product_id: int) -> bool:
        """
        Удаляет продукт из базы данных по ID
        :param product_id: ID продукта для удаления
        :return: True если запрос выполнен, False при ошибке
        """
        if not product_id:
            return False

        db_path = os.path.join('app', 'utils', 'db', 'shop.db')

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                return cursor.rowcount > 0  # Вернёт True если были удалены строки

        except Exception as e:
            logging.error(f"Ошибка удаления продукта {product_id}: {e}")
            return False