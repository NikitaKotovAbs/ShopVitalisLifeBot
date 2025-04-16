from aiogram import Router, types

router = Router()

@router.message(lambda msg: msg.text == "📖 Рецепты")
async def order_list(message: types.Message):
    await message.answer("------Выберите мои Рецепты------")