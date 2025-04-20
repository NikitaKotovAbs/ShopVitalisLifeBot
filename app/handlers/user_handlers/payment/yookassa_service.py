import os
from yookassa import Configuration, Payment
from dotenv import load_dotenv

load_dotenv()

Configuration.account_id = os.getenv('YOOKASSA_SHOP_ID')
Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')


async def create_payment(amount, currency='RUB', description='Оплата заказа', return_url=None):
    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": currency
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url or "https://t.me/ShopVitalisLifeBot"
        },
        "capture": True,
        "description": description
    })

    return payment