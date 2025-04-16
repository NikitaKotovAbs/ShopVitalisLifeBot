from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главное меню
def main_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🍹 Заказать сок")],
        [KeyboardButton(text="🔬 Польза и состав")],
        [KeyboardButton(text="⏱ Режим приёма")],
        [KeyboardButton(text="📖 Рецепты")],
        [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="🛒 Мои заказы")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел👇"
    )

# Кнопки для выбора категорий
def back_basket() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

