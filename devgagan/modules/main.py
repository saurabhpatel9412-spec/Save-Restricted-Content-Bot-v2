# ---------------------------------------------------
# File Name: main.py
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
# More readable 
# ---------------------------------------------------
# devgagan package entrypoint - use `python -m devgagan` or your service runner.
import asyncio
import signal
import sys
from devgagan import start_clients, stop_clients

stop_event = asyncio.Event()

def _signal_handler():
    # set the event to stop the main loop
    stop_event.set()

async def _main():
    # start all clients
    await start_clients()
    # wait until stop signal is received
    await stop_event.wait()
    # on stop, gracefully shutdown clients
    await stop_clients()

def main():
    loop = asyncio.get_event_loop()
    # register signals
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            # Windows or platforms that do not support add_signal_handler
            pass
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        # fallback, ensure shutdown
        pass
    finally:
        # Ensure event is set so shutdown proceeds
        try:
            loop.run_until_complete(stop_clients())
        except Exception:
            pass

if __name__ == "__main__":
    main()
