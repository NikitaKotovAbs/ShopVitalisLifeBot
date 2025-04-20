import sqlite3
import logging
import os
from datetime import datetime
from typing import Optional, Union, Dict
import logging

logger = logging.getLogger(__name__)

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


class OrderManager:
    @staticmethod
    async def create_order(
            user_id: int,
            products: Dict[int, int],
            total_amount: float,
            address: str = "Не указан",
            status: str = "new"
    ) -> int:
        """Создает заказ в БД и возвращает его ID"""
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")

            # Получаем внутренний ID пользователя
            cursor.execute(
                "SELECT id FROM users WHERE id_telegram = ?",
                (user_id,)
            )
            user_db_id = cursor.fetchone()
            if not user_db_id:
                raise ValueError(f"Пользователь {user_id} не найден в БД")

            # Создаем заказ
            cursor.execute(
                """INSERT INTO orders (address, total_price, user_id, status)
                VALUES (?, ?, ?, ?)""",
                (address, total_amount, user_db_id[0], status)
            )
            order_id = cursor.lastrowid

            # Добавляем товары
            for product_id, quantity in products.items():
                cursor.execute(
                    """INSERT INTO order_products (product_id, order_id, quantity)
                    VALUES (?, ?, ?)""",
                    (product_id, order_id, quantity)
                )

            conn.commit()
            return order_id

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"SQL error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
        finally:
            if conn:
                conn.close()