from aiogram import Bot
from typing import Optional
import logging


class Notifier:
    _status_names = {
        "new": "🆕 Новый",
        "processing": "🔄 В обработке",
        "delivering": "🚚 В доставке",
        "delivered": "📦 Доставлен",
        "completed": "✅ Выполнен",
        "cancelled": "❌ Отменен"
    }

    @classmethod
    def get_status_display(cls, status: str) -> str:
        """Возвращает красивое отображение статуса"""
        return cls._status_names.get(status, status)

    @classmethod
    async def notify_order_status_changed(
            cls,
            bot: Bot,
            user_id: int,
            order_id: int,
            old_status: str,
            new_status: str
    ) -> bool:
        """Отправляет уведомление пользователю об изменении статуса заказа"""
        try:
            message = (
                f"📢 Статус вашего заказа #{order_id} изменен:\n"
                f"🔹 Было: {cls.get_status_display(old_status)}\n"
                f"🔸 Стало: {cls.get_status_display(new_status)}\n\n"
                f"Спасибо за использование нашего сервиса!"
            )

            await bot.send_message(
                chat_id=user_id,
                text=message
            )
            return True
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
            return False