import asyncio
import os
try:
    from aiogram import Bot
    AIORAM_OK = True
except ImportError:
    print("🧵 PereshivkaLab | aiogram НЕТ — тест Render OK!")
    AIORAM_OK = False
    while True:
        pass

if not AIORAM_OK:
    exit()
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from database import add_product_admin, get_all_products, get_products, init_db

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

class AdminStates(StatesGroup):
    waiting_photo = State()
    waiting_details = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # ← ДОБАВИЛ storage!

@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🔧 Админка", callback_data="admin")]
    ])
    await message.answer("🧵 PereshivkaLab | Vintage Stone Island готов!", reply_markup=kb)

@dp.message(F.text == "/admin")
async def admin_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ только для админа")
        return
        
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product")],
        [InlineKeyboardButton(text="📋 Все товары", callback_data="show_all")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])
    await message.answer("🔧 **АДМИН-ПАНЕЛЬ**\nВыберите действие:", 
                        reply_markup=kb, parse_mode="Markdown")
@dp.callback_query(F.data == "add_product")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Только для админа!", show_alert=True)
        return
        
    await callback.message.edit_text("📸 **Отправьте фото товара**")
    await state.set_state(AdminStates.waiting_photo)
    await callback.answer()
@dp.message(AdminStates.waiting_photo)
async def process_photo(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
        
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await message.answer("✍️ **Формат**:\n`Название | Цена | Размеры`\n\n*Пример*: `Куртка | 15000 | M,L`", 
                        parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_details)
@dp.message(AdminStates.waiting_details)
async def process_details(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        # 1. Получаем photo_id из FSM состояния
        data = await state.get_data()
        photo_id = data['photo']
        
        # 2. Парсим "Название | Цена | Размеры"
        parts = message.text.split('|')
        if len(parts) != 3:
            await message.answer("❌ **Неверный формат!**\n`Куртка | 15к | M,L`", parse_mode="Markdown")
            return
            
        name, price_str, sizes = [p.strip() for p in parts]
        # "15к" → 15000
        price = int(price_str.replace(' ', '').replace('к', '000').replace('₽', ''))
        
        # 3. СОХРАНЯЕМ В БАЗУ ДАННЫХ
        product_id = add_product_admin(name, price, sizes, photo_id)
        
        # 4. Подтверждение
        await message.answer(f"✅ **Товар добавлен!**\n"
                           f"🆔 `{product_id}`\n"
                           f"📛 {name}\n"
                           f"💰 {price:,}₽\n"
                           f"📏 {sizes}", parse_mode="Markdown")
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ **Ошибка**: {str(e)[:50]}")
        await state.clear()
@dp.callback_query(F.data == "catalog")
async def catalog_callback(callback: CallbackQuery):
    await show_catalog(callback.message)
    await callback.answer()

async def show_catalog(message):
    products = get_products()  # Синхронная функция из database.py
    if not products:
        await message.answer("📦 Товаров пока нет")
        return
    
    for product in products:
        product_id, name, price, sizes, photo_id = product
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Купить", callback_data=f"buy_{product_id}")],
            [InlineKeyboardButton(text="📏 Размеры", callback_data=f"sizes_{product_id}")]
        ])
        
        await message.answer_photo(
            photo=photo_id,
            caption=f"🧵 **{name}**\\n💰 {price:,}₽\\n📏 {sizes} | PereshivkaLab",
            reply_markup=kb,
            parse_mode="Markdown"
        )
@dp.callback_query(F.data.startswith("sold_"))
async def sold_callback(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    
    # Помечаем товар как проданный (убираем из каталога)
    from database import mark_sold
    mark_sold(product_id)
    
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ **ТОВАР ПРОДАН!** 🎉",
        parse_mode="Markdown"
    )
    await callback.answer("✅ Продажа завершена!")

@dp.callback_query(F.data.startswith("cancel_"))
async def cancel_callback(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=callback.message.caption.replace("👆 **Админ, подтверди продажу!**", ""),
        parse_mode="Markdown"
    )
    await callback.answer("❌ Отмена")
# Кнопка "✅ Продано"
@dp.callback_query(F.data.startswith("sold_"))
async def sold_callback(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    
    # Помечаем как проданный (убираем из каталога)
    from database import mark_sold
    mark_sold(product_id)
    
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ **ТОВАР ПРОДАН!** 🎉",
        parse_mode="Markdown"
    )
    await callback.answer("✅ Продажа завершена!")

# Кнопка "❌ Отмена" 
@dp.callback_query(F.data.startswith("cancel_"))
async def cancel_callback(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=callback.message.caption.replace("👆 **Админ, подтверди продажу!**", ""),
        parse_mode="Markdown"
    )
    await callback.answer("❌ Отмена")
@dp.callback_query(F.data.startswith("buy_"))
async def buy_callback(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Продано", callback_data=f"sold_{product_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_{product_id}")]
    ])
    
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n👆 **Админ, подтверди продажу!**",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await callback.answer("Ожидаем подтверждения...")

async def main():
    init_db()
    print("🚀 Бот запущен! Тестируем /admin")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

