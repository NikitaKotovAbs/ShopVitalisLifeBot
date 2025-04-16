from aiogram import F, Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ContentType
from app.keyboard.callback_data import StaffAction
from app.keyboard import kb_staff_menu
import logging

from app.utils.db.operations.add_data import ProductAdd

router = Router()

class AddProductStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_image = State()

@router.message(AddProductStates.waiting_for_title)
async def process_product_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание продукта:")
    await state.set_state(AddProductStates.waiting_for_description)

@router.message(AddProductStates.waiting_for_description)
async def process_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите цену продукта (только число):")
    await state.set_state(AddProductStates.waiting_for_price)

@router.message(AddProductStates.waiting_for_price)
async def process_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError
        await state.update_data(price=price)
        await message.answer("Отправьте изображение продукта:")
        await state.set_state(AddProductStates.waiting_for_image)
    except (ValueError, TypeError):
        await message.answer("❌ Неверный формат цены. Введите число больше 0:")

@router.message(AddProductStates.waiting_for_image, F.content_type == ContentType.PHOTO)
async def process_product_image(message: Message, state: FSMContext, bot: Bot):
    try:
        # Получаем фото с максимальным качеством
        photo = message.photo[-1]

        # Скачиваем файл через bot.download
        file = await bot.get_file(photo.file_id)
        image_bytes = await bot.download_file(file.file_path)

        # Читаем содержимое файла
        image_data = image_bytes.read()

        data = await state.get_data()

        product_id = ProductAdd.add_new_product(
            title=data['title'],
            description=data['description'],
            price=data['price'],
            image=image_data
        )

        if product_id > 0:
            await message.answer(
                f"✅ Продукт успешно добавлен (ID: {product_id})",
                reply_markup=kb_staff_menu(role="owner")
            )
        else:
            await message.answer(
                "❌ Ошибка при добавлении продукта",
                reply_markup=kb_staff_menu(role="owner")
            )

        await state.clear()

    except Exception as e:
        logging.error(f"Ошибка добавления продукта: {e}", exc_info=True)
        await message.answer(
            "⚠️ Произошла ошибка при добавлении продукта",
            reply_markup=kb_staff_menu(role="owner")
        )
        await state.clear()

@router.message(AddProductStates.waiting_for_image)
async def process_wrong_image(message: Message):
    await message.answer("Пожалуйста, отправьте изображение в формате фото (не документ)")