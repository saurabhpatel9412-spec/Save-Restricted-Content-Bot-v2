# ---------------------------------------------------
# File Name: __init__.py
# Description: A Pyrogram bot for downloading files from Telegram channels or groups 
#              and uploading them back to Telegram.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# ---------------------------------------------------


# Modified parts: create TelegramClient instances but don't .start() them at import time.
# Start them inside restrict_bot() with try/except to avoid FloodWait crash.

import asyncio
import logging
import time
from pyrogram import Client
from pyrogram.enums import ParseMode 
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION
from telethon import TelegramClient, errors as telethon_errors
from motor.motor_asyncio import AsyncIOMotorClient

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

botStartTime = time.time()

app = Client(
    "pyrobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=100,
    parse_mode=ParseMode.MARKDOWN
)

# Do NOT call .start(bot_token=...) at import time for Telethon.
# Create TelegramClient instances; start them later inside an async function with proper error handling.
sex = TelegramClient('sexrepo', API_ID, API_HASH)  # do not .start() here
telethon_client = TelegramClient('telethon_session', API_ID, API_HASH)  # do not .start() here

if STRING:
    pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
else:
    pro = None

if DEFAULT_SESSION:
    userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH, session_string=DEFAULT_SESSION)
else:
    userrbot = None

# MongoDB setup
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]  # Your database
token = tdb["tokens"]  # Your tokens collection

# TTL index stuff remains the same
async def create_ttl_index():
    """Ensure the TTL index exists for the `tokens` collection."""
    await token.create_index("expires_at", expireAfterSeconds=0)

async def setup_database():
    await create_ttl_index()
    print("MongoDB TTL index created.")

async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await setup_database()
    await app.start()
    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    BOT_NAME = f"{getme.first_name} {getme.last_name}" if getme.last_name else getme.first_name
    
    # Start pyrogram-based clients if present
    if pro:
        await pro.start()
    if userrbot:
        await userrbot.start()

    # Start Telethon clients safely, catch FloodWaitError so it doesn't crash the whole app
    try:
        await sex.start(bot_token=BOT_TOKEN)
        print("Telethon 'sex' client started.")
    except telethon_errors.FloodWaitError as e:
        print(f"Telethon FloodWait when starting 'sex' client: wait for {e.seconds} seconds. Skipping start to avoid crash.")
    except Exception as e:
        print(f"Failed to start Telethon 'sex' client: {e}")

    try:
        await telethon_client.start(bot_token=BOT_TOKEN)
        print("Telethon 'telethon_client' started.")
    except telethon_errors.FloodWaitError as e:
        print(f"Telethon FloodWait when starting 'telethon_client': wait for {e.seconds} seconds. Skipping start to avoid crash.")
    except Exception as e:
        print(f"Failed to start Telethon 'telethon_client': {e}")

loop.run_until_complete(restrict_bot())
