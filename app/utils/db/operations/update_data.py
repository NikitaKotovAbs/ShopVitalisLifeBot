import logging
import os
import sqlite3


class OrderEdit:
    @classmethod
    def update_order_status(cls, order_id: int, new_status: str) -> bool:
        if not order_id:
            return False

        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE orders SET status = ? WHERE id = ?",
                (new_status, order_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Ошибка обновления статуса заказа {order_id}: {e}")
            return False
        finally:
            conn.close()

class UserEdit:
    @classmethod
    def set_user_job_title(cls, role: str, username: str) -> bool:
        if not role and username:
            return False

        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET role = ? WHERE tag_telegram = ?",
                (role, username)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Ошибка обновления должности: {e}")
            return False
        finally:
            conn.close()