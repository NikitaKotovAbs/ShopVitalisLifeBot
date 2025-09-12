from aiogram import Router, types

router = Router()

@router.message(lambda msg: msg.text == "📖 Рецепты")
async def order_list(message: types.Message):
    recipes_text = """
<b>🍽️ Рецепты для вашего здоровья и vitality!</b>

Здесь вы найдете коллекцию полезных и вкусных рецептов, которые помогут вам поддерживать здоровый образ жизни и наполнять организм энергией.

📚 <b>Все рецепты доступны на нашем сайте:</b>
👉 <a href="https://vitalis-life.ru/рецепты">Vitalis Life Рецепты</a>

✨ <i>Откройте для себя мир вкусного и полезного питания!</i> ✨
"""
    await message.answer(recipes_text, parse_mode="HTML")