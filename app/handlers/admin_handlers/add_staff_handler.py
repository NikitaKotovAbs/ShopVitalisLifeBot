from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.utils.db.operations.update_data import UserEdit

router = Router()

class AddStaffStates(StatesGroup):
    waiting_for_username = State()
    confirm_add_staff = State()

@router.message(AddStaffStates.waiting_for_username)
async def process_add_staff_username(message: types.Message, state: FSMContext):
    """Обработка введенного сообщения при добавлении персонала"""
    await state.update_data(username_text=message.text)

    builder = InlineKeyboardBuilder()
    builder.button(text="Админ", callback_data="add_staff")
    builder.button(text="Персонал", callback_data="add_owner")

    await message.answer(
        f"Выберите роль какую хотите выдать:\n\n{message.text}",
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddStaffStates.confirm_add_staff)

@router.callback_query(AddStaffStates.confirm_add_staff)
async def process_add_staff_role(
        callback: types.CallbackQuery,
        state: FSMContext
):
    data = await state.get_data()
    username = data['username_text']

    match F.data:
        case "add_staff":
            UserEdit.set_user_job_title("staff", username)
        case "add_owner":
            UserEdit.set_user_job_title("owner", username)
        case _:
            await callback.answer("Отсутствует callback_data: добавление персонала", show_alert=True)


    await state.set_state(AddStaffStates.waiting_for_role)