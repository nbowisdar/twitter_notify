import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from dotenv import load_dotenv
from twscrape import Tweet

from bot.db import get_db, save_db
from bot.loader import PARSING_INTERVAL_SEC, TOKEN
from bot.proxy import check_proxy
from bot.utils import extract_username, get_command_args
from bot.x_parser import XManager, XParser

# Load environment variables from .env file
load_dotenv()


logging.basicConfig(level=logging.INFO)


dp = Dispatcher()
x_parser = XParser()
x_manager = XManager(x_parser, int(PARSING_INTERVAL_SEC))


# Handler for /start command
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Hi! I'm a twitter bot. Use /help to see what I can do!")


# Handler for /help command
@dp.message(Command("help"))
async def send_help(message: types.Message):
    help_text = """
        <b>📋 Twitter Bot Commands</b>\n\n
        Here's what I can do:\n
        🔹 <b>/start</b> - Start the bot and get a welcome message.
        🔹 <b>/help</b> - Show this help message with all available commands.
        🔹 <b>/set_proxy &lt;proxy&gt;</b> - Set a proxy for the Twitter parser.
           Example: <code>/set_proxy http://login:pass@example.com:8080</code>
        🔹 <b>/users</b> - List all tracked Twitter users.
        🔹 <b>/add_user &lt;username or URL&gt;</b> - Add a Twitter user to track.
           Example: <code>/add_user elonmusk</code> or <code>/add_user https://twitter.com/elonmusk</code>
        🔹 <b>/delete_user &lt;username or URL&gt;</b> - Remove a tracked Twitter user.
           Example: <code>/delete_user elonmusk</code>
        🔹 <b>/activate_parser</b> - Start the parser to monitor tweets from tracked users.
        🔹 <b>/stop_parser</b> - Stop the tweet parser.
    """
    await message.reply(help_text)


@dp.message(Command("set_proxy"))
async def _(message: types.Message):
    # Extract proxy details from command arguments
    proxy = await get_command_args(message)
    await message.reply(f"Adding proxy {proxy}...")

    if await check_proxy(proxy):
        x_manager.set_proxy(proxy)
        await message.answer(
            f"✅ Parser set to use proxy {proxy}... Need to /activate_parser"
        )
    else:
        await message.answer(f"❌ Proxy {proxy} is not working. Or wrong format.")


# USERS
@dp.message(Command("users"))
async def _(message: types.Message):
    # Extract proxy details from command arguments
    db = get_db()
    await message.reply(f"Users: {"\n".join(db['users'])}\n")


@dp.message(Command("add_user"))
async def _(message: types.Message):
    db = get_db()
    link = await get_command_args(message)
    username = extract_username(link)
    if username in db["users"].keys():
        await message.reply(f"User {username} already exists!")
        return
    x_user_id = await x_manager.x_parser.get_user_id_by_username(username)
    db["users"][username] = x_user_id
    save_db(db)

    await message.reply(f"✅ Adding user {username}...")


@dp.message(Command("delete_user"))
async def _(message: types.Message):
    db = get_db()
    link = await get_command_args(message)
    username = extract_username(link)
    try:
        del db["users"][username]
    except KeyError:
        await message.reply(f"User {username} does not exist!")
        return
    save_db(db)
    await message.reply(f"✅ Deleting user {username}...")


# management
@dp.message(Command("activate_parser"))
async def _(message: types.Message):
    await message.reply("✅ Activating parser...")

    async def on_new_tweet(tweets: list[Tweet]):
        for tweet in tweets:
            from_name = tweet.user.displayname
            tweet_type = "📝 Tweet"
            if tweet.retweetedTweet:
                tweet_type = "🎥🔄 Retweet"
            if tweet.quotedTweet:
                tweet_type = "💬 Quote"
            msg = f"""
{tweet_type} by {from_name}:\n
{tweet.rawContent}\n
            """
            try:
                photo_url = tweet.media.photos[0].url
            except Exception:
                photo_url = None
            if photo_url:
                try:
                    await message.answer_photo(photo_url, caption=msg)
                except Exception:
                    await message.answer(msg)
            else:
                await message.answer(msg)

    x_manager.on_new_tweet_cb = on_new_tweet
    await x_manager.active()


# management
@dp.message(Command("stop_parser"))
async def _(message: types.Message):
    await message.reply("✅ Stopping parser...")
    await x_manager.stop()


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
