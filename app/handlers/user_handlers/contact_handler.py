from aiogram import Router, types

router = Router()

@router.message(lambda msg: msg.text == "📞 Контакты")
async def order_list(message: types.Message):
    await message.answer("------Контакты ------")