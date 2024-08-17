import os
import sys
import asyncio
import json
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from modules import load_modules

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konfigurasi file
CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return []

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

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
            load_modules(client)  # Load modules for each client

    logger.info(f"Userbot running for {len(clients)} account(s).")

    # Keep the script running
    await asyncio.gather(*(client.run_until_disconnected() for client in clients))

if __name__ == '__main__':
    asyncio.run(main())

def add_user_to_config(api_id, api_hash, phone, string_session):
    configs = load_config()
    new_config = {
        "api_id": api_id,
        "api_hash": api_hash,
        "telepon": phone,
        "string_sesi": string_session
    }
    configs.append(new_config)
    save_config(configs)
    logger.info(f"New user {phone} added to config.")

# This function will be called from adduser.py
def start_new_client(api_id, api_hash, string_session):
    asyncio.create_task(start_and_load_client(api_id, api_hash, string_session))

async def start_and_load_client(api_id, api_hash, string_session):
    client = await start_client(string_session, api_id, api_hash)
    if client:
        load_modules(client)
        logger.info(f"New client started and modules loaded.")
        await client.run_until_disconnected()