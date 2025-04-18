import sqlite3
import logging
import os
from typing import Optional, Union

class UserAdd:
    @classmethod
    def init_user(cls, telegram_id, telegram_tag):
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO users (id_telegram, tag_telegram)
                   VALUES(?, ?)""",
                (telegram_id, telegram_tag)
            )
            conn.commit()
        except Exception as e:
            logging.error(f"Ошибка добавления пользователя: {e}")
        finally:
            conn.close()





class ProductAdd:
    @classmethod
    def add_new_product(
            cls,
            title: str,
            description: str,
            price: float,
            image: Optional[Union[bytes, bytearray]] = None
    ) -> int:
        """
        Добавляет новый продукт в базу данных

        :param title: Название продукта
        :param description: Описание продукта
        :param price: Цена продукта
        :param image: Бинарные данные изображения (опционально)
        :return: ID добавленного продукта или -1 при ошибке
        """
        if not title or not description or price <= 0:
            logging.error("Некорректные данные продукта")
            return -1

        db_path = os.path.join('app', 'utils', 'db', 'shop.db')

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Вставляем новый продукт
                cursor.execute(
                    """
                    INSERT INTO products (title, description, price, image)
                    VALUES (?, ?, ?, ?)
                    """,
                    (title, description, price, image)
                )

                # Получаем ID добавленного продукта
                product_id = cursor.lastrowid
                conn.commit()

                logging.info(f"Добавлен новый продукт ID: {product_id}")
                return product_id

        except sqlite3.Error as e:
            logging.error(f"Ошибка добавления продукта: {e}")
            return -1
        except Exception as e:
            logging.error(f"Неожиданная ошибка: {e}")
            return -1
