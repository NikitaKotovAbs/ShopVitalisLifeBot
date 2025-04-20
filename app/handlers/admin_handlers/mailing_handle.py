from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.keyboard.inline import staff_menu
from app.utils.db.operations.fetch_data import UserFetcher
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


class MailingStates(StatesGroup):
    waiting_for_message = State()
    confirm_mailing = State()


@router.message(MailingStates.waiting_for_message)
async def process_mailing_message(message: types.Message, state: FSMContext):
    """Обработка введенного сообщения для рассылки"""
    await state.update_data(mailing_text=message.text)
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Начать рассылку", callback_data="confirm_mailing")
    builder.button(text="❌ Отменить", callback_data="cancel_mailing")

    await message.answer(
        f"Подтвердите рассылку:\n\n{message.text}",
        reply_markup=builder.as_markup()
    )
    await state.set_state(MailingStates.confirm_mailing)


@router.callback_query(F.data == "confirm_mailing", MailingStates.confirm_mailing)
async def confirm_mailing(
        callback: types.CallbackQuery,
        state: FSMContext,
        bot: Bot  # Добавляем бота в зависимости
):
    """Подтверждение и запуск рассылки"""
    data = await state.get_data()
    mailing_text = data['mailing_text']
    role = data.get('role')
    await callback.message.edit_text("🔄 Начинаю рассылку...")

    users = UserFetcher.get_all_users()
    success = 0
    failed = 0

    for user in users:
        try:
            await bot.send_message(
                chat_id=user['id_telegram'],
                text=mailing_text
            )
            success += 1
        except Exception as e:
            logging.error(f"Ошибка отправки: {e}")
            failed += 1

    await callback.message.edit_text(
        f"✅ Рассылка завершена!\nУспешно: {success}\nНе удалось: {failed}"
    )

    # Отправляем меню персонала
    await callback.message.answer(
        "Панель управления:",
        reply_markup=staff_menu(role=role)  # Или передавайте реальную роль пользователя
    )

    await state.clear()


@router.callback_query(F.data == "cancel_mailing", MailingStates.confirm_mailing)
async def cancel_mailing(callback: types.CallbackQuery, state: FSMContext):
    """Отмена рассылки"""
    await callback.message.edit_text("❌ Рассылка отменена")
    await state.clear()
    await callback.answer()
