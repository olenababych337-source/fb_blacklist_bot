import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from database import load_cache
from bot import setup_router

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

async def main():
    cache = load_cache()
    print(f"  ✓ Завантажено {len(cache)} URL з чорного списку в кеш")

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher()

    router = setup_router(cache)
    dp.include_router(router)

    print("  ✓ Бот запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
