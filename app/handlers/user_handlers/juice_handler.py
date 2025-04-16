from aiogram import Router, types

router = Router()

@router.message(lambda msg: msg.text == "🔬 Польза и состав")
async def juice_list(message: types.Message):
    await message.answer("------Польза и состав ------")