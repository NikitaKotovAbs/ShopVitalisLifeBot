import logging
import os
from decimal import Decimal
from typing import Optional, Dict
from aiogram import F, Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    LabeledPrice,
    PreCheckoutQuery,
    SuccessfulPayment,
    Message,
    ReplyKeyboardRemove
)
from app.keyboard.callback_data import ProductAction
from app.utils.db.operations.add_data import OrderManager
from app.utils.db.operations.fetch_data import ProductFetcher
from app.utils.view_data import product_manager

router = Router()
logger = logging.getLogger(__name__)


class OrderStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_payment_confirmation = State()


async def calculate_basket_total(user_id: int) -> Optional[int]:
    """Вычисляет сумму корзины в копейках"""
    try:
        basket = product_manager.get_products(user_id)
        if not basket:
            return None

        items = ProductFetcher.get_juices_by_ids(list(basket.keys()))
        if not items:
            return None

        total = Decimal('0')
        for product_id, quantity in basket.items():
            if product_id in items:
                _, _, price, _ = items[product_id]
                total += Decimal(str(price)) * quantity

        return int(total * 100)  # Конвертируем в копейки
    except Exception as e:
        logger.error(f"Ошибка расчета суммы корзины: {e}")
        return None


@router.callback_query(ProductAction.filter(F.action == "checkout"))
async def start_checkout_process(
        callback: types.CallbackQuery,
        bot: Bot,
        state: FSMContext
):
    try:
        user_id = callback.from_user.id
        total_kopecks = await calculate_basket_total(user_id)

        if total_kopecks is None or total_kopecks <= 0:
            await callback.answer("❌ Невозможно оформить пустой заказ")
            return

        await state.update_data({
            'user_id': user_id,
            'total_kopecks': total_kopecks,
            'message_to_delete': callback.message.message_id
        })

        await callback.message.answer(
            "📦 Введите адрес доставки:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(OrderStates.waiting_for_address)
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка в start_checkout_process: {e}")
        await callback.answer("⚠️ Ошибка при оформлении")
        await state.clear()


@router.message(OrderStates.waiting_for_address)
async def save_address(
        message: Message,
        bot: Bot,
        state: FSMContext
):
    try:
        if not message.text:
            await message.answer("❌ Пожалуйста, отправьте адрес текстом")
            return

        address = message.text.strip()
        if len(address) < 10:
            await message.answer("❌ Адрес слишком короткий (минимум 10 символов)")
            return

        # Сохраняем адрес и переходим к следующему шагу
        await state.update_data(address=address)

        data = await state.get_data()
        if 'message_to_delete' in data:
            try:
                await bot.delete_message(
                    chat_id=message.from_user.id,
                    message_id=data['message_to_delete']
                )
            except Exception:
                logger.warning("Не удалось удалить сообщение с корзиной")

        await message.answer("✅ Адрес сохранён. Подтвердите оплату:")
        await send_payment_invoice(message, bot, state)
        await state.set_state(OrderStates.waiting_for_payment_confirmation)

    except Exception as e:
        logger.error(f"Ошибка при сохранении адреса: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при обработке адреса")
        await state.clear()


async def send_payment_invoice(
        message: Message,
        bot: Bot,
        state: FSMContext
):
    """Отправка платежного инвойса"""
    if not os.getenv('YOOKASSA_PROVIDER_TOKEN'):
        await message.answer("⚠️ Платежная система временно недоступна")
        logger.error("YOOKASSA_PROVIDER_TOKEN не установлен")
        return

    try:
        data = await state.get_data()
        total_kopecks = data.get('total_kopecks')
        user_id = data.get('user_id')
        address = data.get('address')

        if not all([total_kopecks, user_id, address]):
            await message.answer("❌ Ошибка данных заказа. Начните заново.")
            await state.clear()
            return

        print(f"Сумма в копейках: {total_kopecks}")
        print(f"Тип суммы: {type(total_kopecks)}")

        if total_kopecks < 100:  # Минимум 1 рубль (100 копеек)
            raise ValueError("Сумма слишком мала для оплаты")

        provider_token = os.getenv('YOOKASSA_PROVIDER_TOKEN')
        print(f"Токен провайдера: {provider_token}")  # Проверьте что токен не None

        await bot.send_invoice(
            chat_id=user_id,
            title="Оплата заказа",
            description=f"Адрес: {address[:100]}",
            payload=f"{user_id}_{hash(address)}",
            provider_token=os.getenv('YOOKASSA_PROVIDER_TOKEN'),
            currency="RUB",
            prices=[LabeledPrice(label="Товары", amount=total_kopecks)],
            need_phone_number=True,
            provider_data = None
        )

    except Exception as e:
        print(f"Ошибка: {e}")
        print(f"Детали: сумма={total_kopecks}, тип={type(total_kopecks)}")
        logger.error(f"Ошибка при отправке инвойса: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при создании платежа")
        await state.clear()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    try:
        await bot.answer_pre_checkout_query(
            pre_checkout_query_id=pre_checkout_query.id,
            ok=True
        )
    except Exception as e:
        logger.error(f"Pre-checkout error: {e}")
        await bot.answer_pre_checkout_query(
            pre_checkout_query_id=pre_checkout_query.id,
            ok=False,
            error_message="Произошла ошибка при обработке платежа"
        )


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        user_id = data.get('user_id')
        address = data.get('address')

        if not address:
            raise ValueError("Адрес не найден в данных состояния")

        # Добавляем await перед вызовом асинхронного метода
        order_id = await OrderManager.create_order(
            user_id=user_id,
            products=product_manager.get_products(user_id),
            total_amount=message.successful_payment.total_amount // 100,
            address=address
        )

        product_manager.clear_products(user_id)

        await message.answer(
            f"✅ Платеж на сумму {message.successful_payment.total_amount // 100} ₽ получен!\n"
            f"Номер заказа: {order_id}\n"
            f"Адрес доставки: {address}"
        )
        await state.clear()

    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке платежа. Администратор уже уведомлен.")
        await state.clear()