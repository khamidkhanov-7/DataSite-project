import os
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router
from dotenv import load_dotenv
import asyncio

# ===== ENV yuklash =====
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
API_URL = os.getenv("API_URL")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN topilmadi. Iltimos .env faylni tekshiring!")

if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)
else:
    ADMIN_ID = 0

# ===== BOT obyektlari =====
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# ===== FORM STATES =====
class Form(StatesGroup):
    name = State()
    phone = State()
    message = State()

# ===== START =====
@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "👋 Assalomu alaykum!\nNamanganmash kompaniyasining rasmiy botiga xush kelibsiz.\nTilni tanlang:",
        reply_markup=markup
    )

# ===== LANGUAGE SELECTION =====
@router.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def set_language(message: types.Message, state: FSMContext):
    lang = "uz" if "O'zbekcha" in message.text else "ru"
    await state.update_data(lang=lang)
    await show_menu(message, lang)

# ===== BACK TO LANGUAGE SELECTION =====
@router.message(F.text.in_(["🔙 Ortga", "🔙 Назад"]))
async def back_to_language(message: types.Message, state: FSMContext):
    await state.clear()
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True
    )
    await message.answer("⬅️ Tilni tanlang:", reply_markup=markup)

# ===== MENU =====
async def show_menu(message, lang):
    if lang == "uz":
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🏭 Zavod haqida"), KeyboardButton(text="🧾 Mahsulotlar")],
                [KeyboardButton(text="📰 Yangiliklar"), KeyboardButton(text="📞 Aloqa")],
                [KeyboardButton(text="📝 So‘rov yuborish"), KeyboardButton(text="🔙 Ortga")]
            ],
            resize_keyboard=True
        )
        await message.answer("Asosiy menyu:", reply_markup=markup)
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🏭 О заводе"), KeyboardButton(text="🧾 Продукция")],
                [KeyboardButton(text="📰 Новости"), KeyboardButton(text="📞 Контакты")],
                [KeyboardButton(text="📝 Отправить заявку"), KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
        await message.answer("Главное меню:", reply_markup=markup)

# ===== CONTACT =====
@router.message(F.text.in_(["📞 Aloqa", "📞 Контакты"]))
async def contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    if lang == "uz":
        await message.answer(
            "📍 Manzil: Namangan, O‘zbekiston\n📞 Tel: +998 (69) 123-45-67\n✉️ Email: info@namanganmash.uz"
        )
    else:
        await message.answer(
            "📍 Адрес: Наманган, Узбекистан\n📞 Тел: +998 (69) 123-45-67\n✉️ Почта: info@namanganmash.uz"
        )

# ===== REQUEST FORM =====
@router.message(F.text.in_(["📝 So‘rov yuborish", "📝 Отправить заявку"]))
async def request_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.name)
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Ortga")]],
        resize_keyboard=True
    )
    await message.answer("✍️ Ismingizni kiriting:", reply_markup=markup)

@router.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await state.clear()
        data = await state.get_data()
        lang = data.get("lang", "uz")
        await show_menu(message, lang)
        return

    await state.update_data(name=message.text)
    await state.set_state(Form.phone)
    await message.answer("📱 Telefon raqamingizni kiriting:")

@router.message(Form.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await state.set_state(Form.name)
        await message.answer("✍️ Ismingizni qayta kiriting:")
        return

    await state.update_data(phone=message.text)
    await state.set_state(Form.message)
    await message.answer("💬 Xabaringizni yozing:")

@router.message(Form.message)
async def get_message(message: types.Message, state: FSMContext):
    if message.text == "🔙 Ortga":
        await state.set_state(Form.phone)
        await message.answer("📱 Telefon raqamingizni qayta kiriting:")
        return

    await state.update_data(message=message.text)
    data = await state.get_data()

    name = data["name"]
    phone = data["phone"]
    text = data["message"]

    # Admin'ga yuborish
    admin_text = f"📩 Yangi so‘rov:\n\n👤 Ism: {name}\n📱 Telefon: {phone}\n💬 Xabar: {text}"
    try:
        await bot.send_message(ADMIN_ID, admin_text)
    except Exception as e:
        print("⚠️ Admin xatolik:", e)

    # Backend’ga yuborish
    if API_URL:
        try:
            requests.post(API_URL, json={
                "name": name,
                "phone": phone,
                "message": text
            })
        except Exception as e:
            print("❌ Backend xatosi:", e)

    await message.answer("✅ So‘rovingiz yuborildi! Tez orada siz bilan bog‘lanamiz.")
    await state.clear()
    lang = data.get("lang", "uz")
    await show_menu(message, lang)

# ===== DEFAULT =====
@router.message()
async def fallback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await show_menu(message, lang)

# ===== START BOT =====
async def main():
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
