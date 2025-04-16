import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    CHAT_ID = os.getenv('CHAT_ID')

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("Отсутствует TOKEN_BOT")
        if not cls.BOT_TOKEN:
            raise ValueError("Отсутствует CHAT_ID")



Config.validate()