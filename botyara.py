from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

API_TOKEN = "7698963036:AAFWl5VxGu1B_Hdw3LQyNvZgWnHn6gvGzoY"
ADMIN_CHAT_ID = 375178639

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния FSM
class Booking(StatesGroup):
    choosing_restaurant = State()
    entering_datetime = State()

# Старт
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Спасибо, что принимаете участие в проекте по улучшению сервиса в ресторанах.")
    await message.answer(
        "Пожалуйста, выберите ресторан:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Ресторан 1", callback_data="restaurant_1")],
            [types.InlineKeyboardButton(text="Ресторан 2", callback_data="restaurant_2")],
            [types.InlineKeyboardButton(text="Ресторан 3", callback_data="restaurant_3")]
        ])
    )
    await state.set_state(Booking.choosing_restaurant)

# Обработка выбора ресторана
@dp.callback_query(Booking.choosing_restaurant)
async def handle_restaurant_choice(callback: CallbackQuery, state: FSMContext):
    await state.update_data(restaurant=callback.data)
    await callback.message.answer("Укажите дату и время, когда вы сможете посетить этот ресторан (в свободной форме):")
    await state.set_state(Booking.entering_datetime)
    await callback.answer()

# Обработка ввода даты и времени
@dp.message(Booking.entering_datetime)
async def handle_datetime_entry(message: Message, state: FSMContext):
    user_data = await state.get_data()
    restaurant = user_data.get("restaurant")
    date_time = message.text
    username = message.from_user.full_name or message.from_user.username

    # Отправка админу
    text = (
        f"📩 Новое бронирование\n"
        f"👤 Клиент: {username} (@{message.from_user.username})\n"
        f"🏢 Ресторан: {restaurant.replace('_', ' ').title()}\n"
        f"🕒 Дата и время: {date_time}"
    )
    await bot.send_message(ADMIN_CHAT_ID, text)

    await message.answer("Спасибо! Ваша заявка на посещение ресторана принята.")
    await state.clear()
