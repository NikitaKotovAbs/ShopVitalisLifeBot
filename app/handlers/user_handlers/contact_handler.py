from aiogram import Router, types

router = Router()

@router.message(lambda msg: msg.text == "📞 Контакты")
async def order_list(message: types.Message):
    contact_text = """
🌟 *Vitalis Life* — это ваш путь к гармонии, здоровью и осознанной жизни. 

Мы всегда рядом, чтобы ответить на вопросы и помочь вам на пути к вашим целям. Свяжитесь с нами, и вместе мы создадим вашу историю успеха и благополучия.

📧 *Почта:* vitalis-life.rus@mail.ru
📞 *Телефон:* +7(925) 333-77-07
📍 *Адрес:* Московская обл, г. Красногорск, мкр. Опалиха, аллея Золотая, д. 1

💫 *Ждем вас!* 💫
"""
    await message.answer(contact_text, parse_mode="Markdown")