from aiogram import Router, types

router = Router(name="messages_router")
@router.message()
async def echo(message: types.Message):
    await message.answer("Вы написали: " + message.text)