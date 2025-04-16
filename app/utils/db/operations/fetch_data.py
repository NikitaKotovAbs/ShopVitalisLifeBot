import logging
import os
import sqlite3


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
                    is_staff, 
                    is_owner 
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