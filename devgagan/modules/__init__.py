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

# devgagan package init — no event loop operations at import time.
import logging
import time
import os
from pyrogram import Client
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION
from telethon import TelegramClient, errors as telethon_errors
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

botStartTime = time.time()

# Pyrogram bot client (do NOT .run() or .start() here)
app = Client(
    "pyrobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=100,
    parse_mode=ParseMode.MARKDOWN
)

# Telethon clients: create but DO NOT start them here.
sex = TelegramClient('sexrepo', API_ID, API_HASH)
telethon_client = TelegramClient('telethon_session', API_ID, API_HASH)

# Optional pyrogram user/client instances (do not start here)
pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING) if STRING else None
userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH, session_string=DEFAULT_SESSION) if DEFAULT_SESSION else None

# MongoDB setup (shared)
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]

# Startup/shutdown helpers (to be called from a single async entrypoint)
async def start_clients():
    """Start pyrogram/telethon clients safely from one async context."""
    # Start Pyrogram main app
    await app.start()
    # start optional pyrogram clients
    if pro:
        try:
            await pro.start()
        except Exception as e:
            print(f"Warning: failed to start pro client: {e}")
    if userrbot:
        try:
            await userrbot.start()
        except Exception as e:
            print(f"Warning: failed to start userrbot: {e}")

    # Start Telethon clients with error handling to avoid crashing on FloodWait
    try:
        await sex.start(bot_token=BOT_TOKEN)
    except telethon_errors.FloodWaitError as e:
        print(f"Telethon FloodWait for 'sex' client: {e.seconds}s — skipping start for now.")
    except Exception as e:
        print(f"Failed to start Telethon 'sex' client: {e}")

    try:
        await telethon_client.start(bot_token=BOT_TOKEN)
    except telethon_errors.FloodWaitError as e:
        print(f"Telethon FloodWait for 'telethon_client': {e.seconds}s — skipping start for now.")
    except Exception as e:
        print(f"Failed to start Telethon 'telethon_client': {e}")

async def stop_clients():
    """Stop/shutdown clients cleanly."""
    try:
        if telethon_client.is_connected():
            await telethon_client.disconnect()
    except Exception as e:
        print(f"Error disconnecting telethon_client: {e}")
    try:
        if sex.is_connected():
            await sex.disconnect()
    except Exception as e:
        print(f"Error disconnecting sex client: {e}")
    try:
        if pro:
            await pro.stop()
    except Exception as e:
        print(f"Error stopping pro: {e}")
    try:
        if userrbot:
            await userrbot.stop()
    except Exception as e:
        print(f"Error stopping userrbot: {e}")
    try:
        await app.stop()
    except Exception as e:
        print(f"Error stopping app: {e}")
