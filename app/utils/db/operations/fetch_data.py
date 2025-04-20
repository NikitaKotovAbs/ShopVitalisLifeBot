import logging
import os
import sqlite3
from typing import Optional, Dict


class ProductFetcher:
    @classmethod
    def all_juices(cls):
        """Возвращает список всех соков в формате (id, title, desc, price, image_blob)"""
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description, price, image FROM products")
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при загрузке соков: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def get_juices_by_ids(cls, item_ids: list[int]):
        """Получает товары по списку ID"""
        if not item_ids:
            return {}

        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            placeholders = ','.join(['?'] * len(item_ids))
            query = f"SELECT id, title, description, price, image FROM products WHERE id IN ({placeholders})"
            cursor.execute(query, item_ids)
            return {row[0]: row[1:] for row in cursor.fetchall()}
        except Exception as e:
            logging.error(f"Ошибка при загрузке товаров: {e}")
            return {}
        finally:
            conn.close()

    @classmethod
    def get_all_orders(cls):
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()

            # Изменяем сортировку - старые заказы сначала
            cursor.execute('''
                SELECT 
                    o.id AS order_id,
                    o.address,
                    o.total_price,
                    o.status,
                    o.created_at AS order_created,
                    u.id_telegram,
                    u.tag_telegram,
                    p.id AS product_id,
                    p.title,
                    p.description,
                    p.price,
                    op.quantity
                FROM orders o
                JOIN users u ON o.user_id = u.id
                LEFT JOIN order_products op ON o.id = op.order_id
                LEFT JOIN products p ON op.product_id = p.id
                ORDER BY o.created_at ASC, o.id, p.id
            ''')

            orders = {}
            for row in cursor.fetchall():
                order_id = row[0]

                if order_id not in orders:
                    orders[order_id] = {
                        'id': order_id,
                        'address': row[1],
                        'total_price': row[2],
                        'status': row[3],
                        'created_at': row[4],
                        'user': {
                            'id_telegram': row[5],
                            'tag_telegram': row[6]
                        },
                        'products': []
                    }

                if row[7]:  # product_id
                    orders[order_id]['products'].append({
                        'id': row[7],
                        'title': row[8],
                        'description': row[9],
                        'price': row[10],
                        'quantity': row[11]
                    })

            # Просто преобразуем в список, не сортируем дополнительно
            return list(orders.values())

        except Exception as e:
            logging.error(f"Ошибка при загрузке заказов: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def get_product_by_id(cls, product_id: int) -> Dict:
        """Возвращает данные товара по его ID в формате словаря."""
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Исправленный SQL-запрос (убрана лишняя запятая)
            cursor.execute("""
                    SELECT 
                        id,
                        title,
                        description,
                        price
                    FROM products
                    WHERE id = ?
                """, (product_id,))

            result = cursor.fetchone()
            return dict(result) if result else {}

        except sqlite3.Error as e:
            logging.error(f"SQL error in get_product_by_id: {e}")
            return {}
        except Exception as e:
            logging.error(f"Error in get_product_by_id: {e}")
            return {}
        finally:
            conn.close()


class UserFetcher:
    @classmethod
    def get_user_by_telegram_id(cls, telegram_id: int) -> dict | None:
        """Возвращает данные пользователя или None если не найден"""
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            conn.row_factory = sqlite3.Row  # Для доступа к полям по имени
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id_telegram, 
                    tag_telegram, 
                    role 
                FROM users 
                WHERE id_telegram = ?
            """, (telegram_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logging.error(f"Ошибка получения пользователя: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_role_by_telegram_id(cls, telegram_id: int) -> str | None:
        """Возвращает роль пользователя (admin/staff/user) или None если не найден"""
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role 
                FROM users 
                WHERE id_telegram = ?
            """, (telegram_id,))
            result = cursor.fetchone()
            return result[0] if result else None  # Возвращаем только роль (первый элемент кортежа)
        except Exception as e:
            logging.error(f"Ошибка получения роли пользователя: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_all_users(cls):
        """Возвращает список всех пользователей"""
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id_telegram FROM users")
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка получения пользователей: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def get_orders_by_telegram_id(cls, telegram_id: int) -> list[dict]:
        """Получает все заказы пользователя по Telegram ID"""
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    o.id,
                    o.address,
                    o.total_price,
                    o.status,
                    o.created_at,
                    p.id,
                    p.title,
                    p.description,
                    p.price,
                    op.quantity
                FROM orders o
                JOIN users u ON o.user_id = u.id
                LEFT JOIN order_products op ON o.id = op.order_id
                LEFT JOIN products p ON op.product_id = p.id
                WHERE u.id_telegram = ?
                ORDER BY o.created_at DESC
            ''', (telegram_id,))

            orders = {}
            for row in cursor.fetchall():
                order_id = row[0]
                if order_id not in orders:
                    orders[order_id] = {
                        'id': order_id,
                        'address': row[1],
                        'total_price': row[2],
                        'status': row[3],
                        'created_at': row[4],
                        'products': []
                    }
                if row[5]:  # Если есть товар
                    orders[order_id]['products'].append({
                        'id': row[5],
                        'title': row[6],
                        'description': row[7],
                        'price': row[8],
                        'quantity': row[9]
                    })

            return list(orders.values())

        except Exception as e:
            logging.error(f"Ошибка получения заказов для пользователя {telegram_id}: {e}")
            return []
        finally:
            conn.close()

class OrderFetcher:
    @classmethod
    def get_order_user_info(cls, order_id: int) -> Optional[dict]:
        """Получает информацию о пользователе по ID заказа"""
        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                    SELECT 
                        u.id_telegram,
                        o.status as old_status
                    FROM orders o
                    JOIN users u ON o.user_id = u.id
                    WHERE o.id = ?
                """, (order_id,))
            result = cursor.fetchone()
            return {
                'user_id': result[0],
                'old_status': result[1]
            } if result else None
        except Exception as e:
            logging.error(f"Ошибка получения пользователя для заказа {order_id}: {e}")
            return None
        finally:
            conn.close()
