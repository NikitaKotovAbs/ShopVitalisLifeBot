import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.keyboard import kb_staff_menu
from app.keyboard.inline import staff_menu
from app.utils.db.operations.update_data import UserEdit

router = Router()


class AddStaffStates(StatesGroup):
    waiting_for_username = State()
    confirm_add_role = State()


ROLE_ACTIONS = {
    "set_owner": ("owner", "👑 Администратора"),
    "set_staff": ("staff", "👔 Персонала"),
    "set_user": ("user", "👤 Пользователя")
}


@router.message(AddStaffStates.waiting_for_username)
async def handle_username_input(message: types.Message, state: FSMContext):
    """Обработка введенного username и предложение выбора роли"""
    await state.update_data(username=message.text.strip(), role="owner")  # Сохраняем роль текущего пользователя

    builder = InlineKeyboardBuilder()
    buttons = [
        ("👑 Администратор", "set_owner"),
        ("👔 Персонал", "set_staff"),
        ("🚫 Забрать права", "set_user")
    ]

    for text, callback_data in buttons:
        builder.button(text=text, callback_data=callback_data)

    builder.adjust(1)  # Все кнопки в столбик для лучшего восприятия

    await message.answer(
        f"🔘 <b>Выберите роль для пользователя:</b>\n\n"
        f"👤 {message.text}\n\n"
        f"Укажите уровень доступа:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(AddStaffStates.confirm_add_role)


@router.callback_query(
    AddStaffStates.confirm_add_role,
    F.data.in_(ROLE_ACTIONS.keys())
)
async def handle_role_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбранной роли и применение изменений"""
    data = await state.get_data()
    username = data['username']
    current_user_role = data['role']
    role_data = callback.data

    role, role_name = ROLE_ACTIONS[role_data]

    try:
        UserEdit.set_user_job_title(role, username)

        await callback.message.edit_text(
            f"✅ <b>Права успешно обновлены!</b>\n\n"
            f"👤 Пользователь: {username}\n"
            f"🎚 Новый уровень: {role_name}",
            parse_mode="HTML"
        )

        # Возвращаем в меню управления
        await callback.message.answer(
            "📌 <b>Панель управления персоналом</b>",
            reply_markup=staff_menu(role=current_user_role),
            parse_mode="HTML"
        )

    except Exception as e:
        await callback.message.edit_text(
            "⚠️ <b>Ошибка при обновлении прав!</b>\n\n"
            f"Попробуйте позже или обратитесь к разработчику.",
            parse_mode="HTML"
        )
        logging.error(f"Ошибка изменения прав: {e}")

    await state.clear()


@router.callback_query(AddStaffStates.confirm_add_role)
async def handle_unknown_role_action(callback: types.CallbackQuery):
    await callback.answer("🔴 Неизвестное действие!", show_alert=True)