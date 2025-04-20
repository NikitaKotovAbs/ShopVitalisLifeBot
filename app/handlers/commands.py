from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboard import kb_menu
from app.utils.db.operations.add_data import UserAdd
from app.utils.db.operations.fetch_data import UserFetcher
from app.keyboard import kb_staff_menu
router = Router(name="commands_router")


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    telegram_id = message.from_user.id
    telegram_tag = f"@{message.from_user.username}" if message.from_user.username else None
    user_data = UserFetcher.get_user_by_telegram_id(telegram_id)

    if user_data:
        welcome_text = (
            f"С возвращением, {message.from_user.full_name}!\n"
            f"Ваш статус: {'Админ' if user_data['role'] == 'owner' else 'Персонал' if user_data['role'] == 'staff' else 'Пользователь'}"
        )
    else:
        # Новый пользователь
        UserAdd.init_user(telegram_id, telegram_tag)
        welcome_text = (
            f"Добро пожаловать, {message.from_user.full_name}!\n"
            "Вы были зарегистрированы в системе!"
        )
    await message.answer(welcome_text, reply_markup=kb_menu())

from aiogram.types import ReplyKeyboardRemove

@router.message(Command("staff"))
async def staff_panel(
        message: types.Message,
        state: FSMContext
):
    await state.clear()
    role = UserFetcher.get_role_by_telegram_id(message.from_user.id)

    await state.update_data(role=role)
    if not role:
        await message.answer("Ошибка: данные пользователя не найдены", reply_markup=ReplyKeyboardRemove())
        return
    print(role)
    if role == "owner" or role == "staff":
        await message.answer(
            "Вы зашли в панель персонала",
            reply_markup=ReplyKeyboardRemove()  # Сначала закрываем Reply-клавиатуру
        )
        # Затем отправляем сообщение с Inline-клавиатурой
        await message.answer(
            "Выберите действие:",
            reply_markup=kb_staff_menu(role=role)
        )
    else:
        await message.answer(
            "У вас нет доступа к staff-панели",
            reply_markup=ReplyKeyboardRemove()  # Закрываем reply-клавиатуру
        )
