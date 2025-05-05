import asyncio
import json
import logging
import os
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from dotenv import load_dotenv

from bot.utils import extract_username, get_command_args

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
TOKEN = os.getenv("BOT_TOKEN")  # Load token from .env

dp = Dispatcher()


def get_db() -> dict:
    with open("db.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data: dict):
    with open("db.json", "w", encoding="utf-8") as f:
        json.dump(data, f)


# Handler for /start command
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Hi! I'm a twitter bot. Use /help to see what I can do!")


# Handler for /help command
@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.reply(
        "I can:\n- Respond to /start\n- Respond to /help\n- Echo any text you send me!"
    )


@dp.message(Command("add_proxy"))
async def _(message: types.Message):
    # Extract proxy details from command arguments
    proxy = await get_command_args(message)
    await message.reply(f"✅ Adding proxy {proxy}...")


@dp.message(Command("users"))
async def _(message: types.Message):
    # Extract proxy details from command arguments
    db = get_db()
    await message.reply(f"Users: {"\n".join(db['users'])}\n")


@dp.message(Command("add_user"))
async def _(message: types.Message):
    db = get_db()
    link = await get_command_args(message)
    user = extract_username(link)
    if user in db["users"]:
        await message.reply(f"User {user} already exists!")
        return
    db["users"].append(user)
    save_db(db)
    await message.reply(f"✅ Adding user {user}...")


@dp.message(Command("delete_user"))
async def _(message: types.Message):
    db = get_db()
    link = await get_command_args(message)
    user = extract_username(link)
    db["users"].remove(user)
    save_db(db)
    await message.reply(f"✅ Deleting user {user}...")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
