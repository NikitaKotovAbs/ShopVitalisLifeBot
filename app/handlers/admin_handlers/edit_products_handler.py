from aiogram import Router, types

router = Router()

@router.message(lambda msg: msg.text == "Товары")
async def juice_list(message: types.Message):
    await message.answer("------Режим приёма ------")