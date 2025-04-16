from aiogram import Bot, Dispatcher
from app.handlers import router as main_router
import logging
import asyncio
from config import Config

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

# Регистрируем все роутер
dp.include_router(main_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")