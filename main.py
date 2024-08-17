import os
import sys
import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from config_manager import load_config

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start_client(session, api_id, api_hash):
    client = TelegramClient(StringSession(session), api_id, api_hash)
    try:
        await client.start()
        return client
    except Exception as e:
        logger.error(f"Error starting client: {str(e)}")
        return None

async def main():
    configs = load_config()
    clients = []

    for config in configs:
        client = await start_client(config['string_sesi'], config['api_id'], config['api_hash'])
        if client:
            clients.append(client)
            logger.info(f"Client for {config['telepon']} started successfully.")
            # Load modules for each client
            from modules import load_modules
            load_modules(client)

    logger.info(f"Userbot running for {len(clients)} account(s).")

    # Keep the script running
    await asyncio.gather(*(client.run_until_disconnected() for client in clients))

if __name__ == '__main__':
    asyncio.run(main())

# These functions will be called from adduser.py
def start_new_client(api_id, api_hash, string_session):
    asyncio.create_task(start_and_load_client(api_id, api_hash, string_session))

async def start_and_load_client(api_id, api_hash, string_session):
    client = await start_client(string_session, api_id, api_hash)
    if client:
        from modules import load_modules
        load_modules(client)
        logger.info(f"New client started and modules loaded.")
        await client.run_until_disconnected()