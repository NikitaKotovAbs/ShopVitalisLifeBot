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
    def set_user_job_title(cls, type_job_title: str, username: str) -> bool:
        if not type_job_title and username:
            return False

        db_path = os.path.join('app', 'utils', 'db', 'shop.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            match type_job_title:
                case "owner":
                    cursor.execute(
                        "UPDATE users SET is_owner = ? WHERE tag_telegram = ?",
                        (True, username)
                    )
                    conn.commit()
                case "staff":
                    cursor.execute(
                        "UPDATE users SET is_staff = ? WHERE tag_telegram = ?",
                        (True, username)
                    )
                    conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Ошибка обновления должности: {e}")
            return False
        finally:
            conn.close()