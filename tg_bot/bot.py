import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from tg_bot.handlers import cmd_router, cb_router, msg_router
import database.db as db
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.environ["TOKEN"]
bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    await db.async_db_connect()
    dp.include_router(msg_router)
    dp.include_router(cmd_router)
    dp.include_router(cb_router)
    await dp.start_polling(bot)

print('ready')
asyncio.run(main())
