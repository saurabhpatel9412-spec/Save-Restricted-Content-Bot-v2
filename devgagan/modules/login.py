# ---------------------------------------------------
# File Name: login.py
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
# Replace the top of file or the generate_session handler to use shared DB and avoid creating a new motor client.

import os
from datetime import datetime, timezone

from pyrogram import Client, filters
from pyrogram.errors import (ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid,
                             PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid)

# Use the shared DB from devgagan package instead of creating a new motor client here.
# devgagan/__init__.py defines: tclient, tdb, token
from devgagan import tdb

# get premium collection from the shared database (tdb)
_premium_coll = None
if tdb is not None:
    try:
        _premium_coll = tdb.get_collection("premium")
    except Exception:
        _premium_coll = None

@app.on_message(filters.command("login"))
async def generate_session(_, message):
    joined = await subscribe(_, message)
    if joined == 1:
        return

    user_id = message.chat.id

    # --- PREMIUM CHECK: if not premium, block login with message ---
    try:
        if _premium_coll is None:
            # If DB not configured or collection not available, block by default
            await message.reply("❌ This feature is only available for premium users. Please upgrade to premium to use login.")
            return

        prem_doc = await _premium_coll.find_one({"user_id": int(user_id)})
        if not prem_doc:
            await message.reply("❌ This feature is only available for premium users. Please upgrade to premium to use login.")
            return

        expires = prem_doc.get("expires_at")
        if expires is not None:
            # Accept both datetime and ISO string formats
            if isinstance(expires, str):
                try:
                    expires_dt = datetime.fromisoformat(expires)
                except Exception:
                    await message.reply("❌ This feature is only available for premium users. Please upgrade to premium to use login.")
                    return
            else:
                expires_dt = expires

            now = datetime.now(timezone.utc)
            if expires_dt.tzinfo is None:
                expires_dt = expires_dt.replace(tzinfo=timezone.utc)

            if expires_dt <= now:
                await message.reply("❌ This feature is only available for premium users. Please upgrade to premium to use login.")
                return
    except Exception:
        # On DB errors, be conservative and block access
        await message.reply("❌ This feature is only available for premium users. Please upgrade to premium to use login.")
        return
    # --- END PREMIUM CHECK ---

    # Existing login flow continues (unchanged)...
    number = await _.ask(user_id, 'Please enter your phone number along with the country code. \nExample: +19876543210', filters=filters.text)   
    phone_number = number.text
    try:
        await message.reply("📲 Sending OTP in Telegram.....")
        client = Client(f"session_{user_id}", api_id, api_hash)
        
        await client.connect()
    except Exception as e:
        await message.reply(f"❌ Failed to send OTP {e}. Please wait and try again later.")
        return
    try:
        code = await client.send_code(phone_number)
    except ApiIdInvalid:
        await message.reply('❌ Invalid combination of API ID and API HASH. Please restart the session.')
        return
    except PhoneNumberInvalid:
        await message.reply('❌ Invalid phone number. Please restart the session.')
        return
    try:
        otp_code = await _.ask(user_id, "Please check for an OTP in your official Telegram account. Once received, enter the OTP in the following format: \nIf the OTP is `12345`, please enter it as `1 2 3 4 5`.", filters=filters.text, timeout=600)
    except TimeoutError:
        await message.reply('⏰ Time limit of 10 minutes exceeded. Please restart the session.')
        return
    phone_code = otp_code.text.replace(" ", "")
    try:
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
                
    except PhoneCodeInvalid:
        await message.reply('❌ Invalid OTP. Please restart the session.')
        return
    except PhoneCodeExpired:
        await message.reply('❌ Expired OTP. Please restart the session.')
        return
    except SessionPasswordNeeded:
        try:
            two_step_msg = await _.ask(user_id, 'Your account has two-step verification enabled. Please enter your password.', filters=filters.text, timeout=300)
        except TimeoutError:
            await message.reply('⏰ Time limit of 5 minutes exceeded. Please restart the session.')
            return
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('❌ Invalid password. Please restart the session.')
            return
    string_session = await client.export_session_string()
    await db.set_session(user_id, string_session)
    await client.disconnect()
    await otp_code.reply("✅ Login successful!")
