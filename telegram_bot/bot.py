import os
import re
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

# ===== VALIDATION FUNCTIONS =====
def validate_full_name(name: str) -> bool:
    """Ism va familiya borligini tekshiradi"""
    words = name.strip().split()
    return len(words) >= 2 and all(len(word) >= 2 for word in words)

def validate_phone(phone: str) -> bool:
    """Telefon raqam formatini tekshiradi: +998(XX)XXX-XX-XX yoki +998XXXXXXXXX"""
    # Faqat raqam, +, (, ), - belgilarini qoldirish
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # +998 bilan boshlanishi va 12 ta raqam bo'lishi kerak
    if cleaned.startswith('+998') and len(cleaned) == 13:
        return True
    return False

# ===== START =====
@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await show_language_menu(message)

# ===== TIL TANLASH MENYUSI =====
async def show_language_menu(message: types.Message):
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
    await state.update_data(lang=lang, in_menu=True)
    await show_menu(message, lang)

# ===== MENU =====
async def show_menu(message, lang):
    if lang == "uz":
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🏭 Zavod haqida"), KeyboardButton(text="📦 Mahsulotlar")],
                [KeyboardButton(text="📰 Yangiliklar"), KeyboardButton(text="📞 Aloqa")],
                [KeyboardButton(text="📨 Buyurtma (Zayavka)"), KeyboardButton(text="🔙 Ortga")]
            ],
            resize_keyboard=True
        )
        await message.answer("📋 Asosiy menyu:", reply_markup=markup)
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🏭 О заводе"), KeyboardButton(text="📦 Продукция")],
                [KeyboardButton(text="📰 Новости"), KeyboardButton(text="📞 Контакты")],
                [KeyboardButton(text="📨 Заказать (Заявка)"), KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
        await message.answer("📋 Главное меню:", reply_markup=markup)

# ===== BACK HANDLER =====
@router.message(F.text.in_(["🔙 Ortga", "🔙 Назад"]))
async def back_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    in_menu = data.get("in_menu", False)

    if in_menu:
        await state.clear()
        await show_language_menu(message)
    else:
        await state.update_data(in_menu=True)
        await show_menu(message, lang)

# ===== ISHLAMAYDIGAN BO'LIMLAR =====
@router.message(F.text.in_([
    "🏭 Zavod haqida", "📦 Mahsulotlar", "📰 Yangiliklar",
    "🏭 О заводе", "📦 Продукция", "📰 Новости"
]))
async def under_development(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(in_menu=False)

    if lang == "uz":
        text = "❗ Uzr, bot hali to'liq ishga tushmagan."
        back_btn = "🔙 Ortga"
    else:
        text = "❗ Извините, бот ещё не полностью запущен."
        back_btn = "🔙 Назад"

    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=back_btn)]],
        resize_keyboard=True
    )
    await message.answer(text, reply_markup=markup)

# ===== ALOQA =====
@router.message(F.text.in_(["📞 Aloqa", "📞 Контакты"]))
async def contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(in_menu=False)
    
    back_btn = "🔙 Ortga" if lang == "uz" else "🔙 Назад"
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=back_btn)]],
        resize_keyboard=True
    )
    
    if lang == "uz":
        await message.answer(
            "📍 Manzil: Namangan, O'zbekiston\n📞 Tel: +998 (69) 123-45-67\n✉️ Email: info@namanganmash.uz",
            reply_markup=markup
        )
    else:
        await message.answer(
            "📍 Адрес: Наманган, Узбекистан\n📞 Тел: +998 (69) 123-45-67\n✉️ Почта: info@namanganmash.uz",
            reply_markup=markup
        )

# ===== BUYURTMA (ZAYAVKA) =====
@router.message(F.text.in_(["📨 Buyurtma (Zayavka)", "📨 Заказать (Заявка)"]))
async def request_start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(in_menu=False)

    await state.set_state(Form.name)
    back_btn = "🔙 Ortga" if lang == "uz" else "🔙 Назад"

    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=back_btn)]],
        resize_keyboard=True
    )

    if lang == "uz":
        await message.answer(
            "✍️ Ism va familiyangizni to'liq kiriting:\n\n"
            "Misol: Alisher Navoiy",
            reply_markup=markup
        )
    else:
        await message.answer(
            "✍️ Введите ваше имя и фамилию полностью:\n\n"
            "Пример: Алишер Навои",
            reply_markup=markup
        )

@router.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    if message.text in ["🔙 Ortga", "🔙 Назад"]:
        data = await state.get_data()
        lang = data.get("lang", "uz")
        await state.clear()
        await state.update_data(lang=lang, in_menu=True)
        await show_menu(message, lang)
        return

    data = await state.get_data()
    lang = data.get("lang", "uz")

    # Ism va familiya validatsiyasi
    if not validate_full_name(message.text):
        if lang == "uz":
            await message.answer(
                "❌ Iltimos, ism va familiyangizni to'liq kiriting!\n\n"
                "Misol: Alisher Navoiy"
            )
        else:
            await message.answer(
                "❌ Пожалуйста, введите имя и фамилию полностью!\n\n"
                "Пример: Алишер Навои"
            )
        return

    await state.update_data(name=message.text)
    await state.set_state(Form.phone)
    
    if lang == "uz":
        text = (
            "📱 Telefon raqamingizni to'liq kiriting:\n\n"
            "Format: +998(XX)XXX-XX-XX\n"
            "Misol: +998(90)123-45-67"
        )
    else:
        text = (
            "📱 Введите номер телефона полностью:\n\n"
            "Формат: +998(XX)XXX-XX-XX\n"
            "Пример: +998(90)123-45-67"
        )
    
    await message.answer(text)

@router.message(Form.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if message.text in ["🔙 Ortga", "🔙 Назад"]:
        await state.set_state(Form.name)
        data = await state.get_data()
        lang = data.get("lang", "uz")
        if lang == "uz":
            text = "✍️ Ism va familiyangizni qayta kiriting:"
        else:
            text = "✍️ Введите ваше имя и фамилию заново:"
        await message.answer(text)
        return

    data = await state.get_data()
    lang = data.get("lang", "uz")

    # Telefon raqam validatsiyasi
    if not validate_phone(message.text):
        if lang == "uz":
            await message.answer(
                "❌ Telefon raqam noto'g'ri formatda!\n\n"
                "To'g'ri format: +998(XX)XXX-XX-XX\n"
                "Misol: +998(90)123-45-67"
            )
        else:
            await message.answer(
                "❌ Неверный формат номера телефона!\n\n"
                "Правильный формат: +998(XX)XXX-XX-XX\n"
                "Пример: +998(90)123-45-67"
            )
        return

    await state.update_data(phone=message.text)
    await state.set_state(Form.message)
    
    text = "💬 Xabaringizni yozing:" if lang == "uz" else "💬 Напишите ваше сообщение:"
    await message.answer(text)

@router.message(Form.message)
async def get_message(message: types.Message, state: FSMContext):
    if message.text in ["🔙 Ortga", "🔙 Назад"]:
        await state.set_state(Form.phone)
        data = await state.get_data()
        lang = data.get("lang", "uz")
        if lang == "uz":
            text = "📱 Telefon raqamingizni qayta kiriting:"
        else:
            text = "📱 Введите номер телефона заново:"
        await message.answer(text)
        return

    await state.update_data(message=message.text)
    data = await state.get_data()

    name = data["name"]
    phone = data["phone"]
    text = data["message"]
    lang = data.get("lang", "uz")

    # Admin'ga yuborish
    admin_text = f"📩 Yangi buyurtma:\n\n👤 Ism: {name}\n📱 Telefon: {phone}\n💬 Xabar: {text}"
    try:
        await bot.send_message(ADMIN_ID, admin_text)
    except Exception as e:
        print("⚠️ Admin xatolik:", e)

    # Backend'ga yuborish
    if API_URL:
        try:
            requests.post(API_URL, json={
                "name": name,
                "phone": phone,
                "message": text
            })
        except Exception as e:
            print("❌ Backend xatosi:", e)

    if lang == "uz":
        success_text = "✅ Buyurtmangiz yuborildi! Tez orada siz bilan bog'lanamiz."
    else:
        success_text = "✅ Ваша заявка отправлена! Скоро свяжемся с вами."
    
    await message.answer(success_text)
    await state.clear()
    await state.update_data(lang=lang, in_menu=True)
    await show_menu(message, lang)

@router.message()
async def fallback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(in_menu=True)
    await show_menu(message, lang)


async def main():
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())