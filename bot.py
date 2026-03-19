from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import is_in_blacklist, add_to_blacklist, supabase

router = Router()

FB_MARKETPLACE = "facebook.com/marketplace/profile"

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📊 Статистика"),
            KeyboardButton(text="❓ Допомога"),
        ]
    ],
    resize_keyboard=True
)


def is_valid_url(url: str) -> bool:
    return FB_MARKETPLACE in url.lower()


def setup_router(cache):

    @router.message(Command("start"))
    async def handle_start(message: Message):
        await message.answer(
            "👋 Привіт!\n\n"
            "Надішли посилання на профіль продавця Facebook Marketplace "
            "і я перевірю чи є він у чорному списку.\n\n"
            "Приклад:\n"
            "https://www.facebook.com/marketplace/profile/100001057606892/",
            reply_markup=menu
        )

    @router.message(Command("help"))
    async def handle_help(message: Message):
        await message.answer(
            "❓ <b>Як користуватись ботом:</b>\n\n"
            "1️⃣ Скопіюй посилання на профіль продавця з Facebook Marketplace\n\n"
            "2️⃣ Надішли його в цей чат\n\n"
            "3️⃣ Якщо продавець вже є у чорному списку — бот повідомить тебе 🚫\n\n"
            "4️⃣ Якщо продавця немає у списку — посилання буде автоматично додано ✅\n\n"
            "📌 <b>Команди:</b>\n"
            "/stats — статистика чорного списку\n"
            "/help — ця довідка",
            parse_mode="HTML",
            reply_markup=menu
        )

    @router.message(Command("stats"))
    async def handle_stats(message: Message):
        result = supabase.table("blacklist").select(
            "url, date"
        ).order("date", desc=True).limit(5).execute()

        total = supabase.table("blacklist").select(
            "*", count="exact"
        ).execute().count

        text = "📊 <b>Статистика чорного списку:</b>\n\n"
        text += f"🔴 Всього у списку: <b>{total}</b>\n\n"

        if result.data:
            text += "🕐 <b>Останні 5 доданих:</b>\n"
            for row in result.data:
                text += f"• <code>{row['url']}</code>\n  <i>{row['date']}</i>\n\n"

        await message.answer(text, parse_mode="HTML", reply_markup=menu)

    @router.message(F.text == "📊 Статистика")
    async def handle_stats_btn(message: Message):
        await handle_stats(message)

    @router.message(F.text == "❓ Допомога")
    async def handle_help_btn(message: Message):
        await handle_help(message)

    @router.message(F.text)
    async def handle_message(message: Message):
        text = message.text.strip()

        if not is_valid_url(text):
            await message.answer(
                "⚠️ Надішліть посилання на профіль продавця\n\n"
                "Приклад:\n"
                "https://www.facebook.com/marketplace/profile/100001057606892/",
                reply_markup=menu
            )
            return

        if is_in_blacklist(cache, text):
            await message.answer(
                "🚫 Посилання є у чорному списку!",
                reply_markup=menu
            )
        else:
            added = add_to_blacklist(cache, text, message.from_user.id)
            if added:
                await message.answer(
                    "✅ Посилання додано до чорного списку!",
                    reply_markup=menu
                )
            else:
                await message.answer(
                    "🚫 Посилання є у чорному списку!",
                    reply_markup=menu
                )

    return router