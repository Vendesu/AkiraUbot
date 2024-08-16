import os
import sys
import asyncio
import json
import logging
import random
import signal
import platform
import psutil
import datetime
from telethon import TelegramClient, events
from telethon.tl.types import InputPeerUser
from telethon.errors import SessionPasswordNeededError, FloodWaitError, PhoneCodeInvalidError
from telethon.sessions import StringSession
import threading
import sqlite3
from modules import load_modules

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konfigurasi file
CONFIG_FILE = 'config.json'
LOG_FILE = 'userbot.log'

# Tambahkan file handler ke logger
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding {CONFIG_FILE}. File might be corrupted.")
        return []
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return []

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")

async def send_activation_message(client):
    try:
        me = await client.get_me()
        uname = platform.uname()
        memory = psutil.virtual_memory()
        
        message = "🚀 **Userbot Telah Aktif!**\n\n"
        message += f"**👤 Pengguna:** {me.first_name}\n"
        message += f"**🆔 User ID:** `{me.id}`\n"
        message += f"**💻 Sistem:** {uname.system} {uname.release}\n"
        message += f"**🧠 RAM:** {memory.percent}% terpakai\n"
        message += f"**⏰ Waktu Aktivasi:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        message += "Gunakan `.help` untuk melihat daftar perintah yang tersedia."
        
        await client.send_message('me', message)
        logger.info(f"Activation message sent for user {me.id}")
    except Exception as e:
        logger.error(f"Error sending activation message: {str(e)}")

async def start_client(api_id, api_hash, phone_or_string, max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        try:
            if phone_or_string.startswith('+'):  # This is a phone number
                session = f'session_{phone_or_string}'
                client = TelegramClient(session, api_id, api_hash)
                await client.start()
                
                if not await client.is_user_authorized():
                    try:
                        await client.send_code_request(phone_or_string)
                        code = input(f"Enter the verification code for {phone_or_string}: ")
                        await client.sign_in(phone_or_string, code)
                    except SessionPasswordNeededError:
                        password = input(f"Enter the 2FA password for {phone_or_string}: ")
                        await client.sign_in(password=password)
                
                # After successful login, generate and save session string
                string_session = StringSession.save(client.session)
                logger.info(f"Session string generated for {phone_or_string}")
                
                # Update configuration with session string
                configs = load_config()
                for config in configs:
                    if config.get('phone') == phone_or_string:
                        config['session_string'] = string_session
                        save_config(configs)
                        break
            
            else:  # This is a session string
                client = TelegramClient(StringSession(phone_or_string), api_id, api_hash)
                await client.start()
            
            # Add save_config method to client
            client.save_config = save_config
            client.config = load_config()
            
            # Send activation message
            await send_activation_message(client)
            
            return client
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                attempt += 1
                wait_time = random.uniform(1, 5)  # Random wait between 1 to 5 seconds
                logger.warning(f"Database locked. Retrying in {wait_time:.2f} seconds... (Attempt {attempt}/{max_attempts})")
                await asyncio.sleep(wait_time)
            else:
                raise  # If it's a different sqlite error, raise it
        except FloodWaitError as e:
            logger.error(f"FloodWaitError: {str(e)}")
            logger.info(f"Waiting for {e.seconds} seconds before retrying...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"Error starting client: {str(e)}")
            attempt += 1
            if attempt >= max_attempts:
                logger.error(f"Failed to start client after {max_attempts} attempts.")
                return None
            wait_time = random.uniform(1, 5)
            logger.info(f"Retrying in {wait_time:.2f} seconds... (Attempt {attempt}/{max_attempts})")
            await asyncio.sleep(wait_time)

    logger.error(f"Failed to start client after {max_attempts} attempts.")
    return None

async def add_new_account():
    try:
        api_id = input("Enter API ID: ")
        api_hash = input("Enter API Hash: ")
        phone = input("Enter phone number (format: +62xxxxxxxxxx): ")

        client = TelegramClient(f'session_{phone}', api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            try:
                await client.send_code_request(phone)
                code = input(f"Enter the OTP sent to {phone}: ")
                await client.sign_in(phone, code)
            except PhoneCodeInvalidError:
                logger.error("Invalid OTP. Please try again.")
                return None
            except SessionPasswordNeededError:
                password = input("Enter 2FA password: ")
                await client.sign_in(password=password)

        # After successful login, generate and save session string
        string_session = StringSession.save(client.session)
        logger.info(f"Session string created for {phone}")

        new_config = {
            "api_id": api_id,
            "api_hash": api_hash,
            "phone": phone,
            "session_string": string_session
        }

        configs = load_config()
        configs.append(new_config)
        save_config(configs)

        load_modules(client)
        logger.info(f"New account successfully added and started.")
        return client
    except Exception as e:
        logger.error(f"Error adding new account: {str(e)}")
        return None

def input_thread(loop):
    while True:
        command = input("Type 'add' to add a new account, 'list' to show active accounts, or 'exit' to quit: ")
        if command.lower() == 'add':
            loop.create_task(add_new_account())
        elif command.lower() == 'list':
            loop.create_task(list_active_accounts())
        elif command.lower() == 'exit':
            logger.info("Closing program...")
            loop.stop()
            break

async def list_active_accounts():
    try:
        configs = load_config()
        logger.info("Active accounts:")
        for i, config in enumerate(configs, 1):
            identifier = config.get('phone') or f"Session {i}"
            logger.info(f"{i}. {identifier}")
    except Exception as e:
        logger.error(f"Error listing active accounts: {str(e)}")

def signal_handler(sig, frame):
    logger.info("Received signal to terminate. Closing gracefully...")
    for task in asyncio.all_tasks():
        task.cancel()
    loop = asyncio.get_event_loop()
    loop.stop()

async def main():
    configs = load_config()
    
    if not configs:
        logger.info("No account configurations found. Adding a new account.")
        await add_new_account()
        configs = load_config()
    
    clients = []
    for config in configs:
        phone_or_string = config.get('phone') or config.get('session_string')
        client = await start_client(config['api_id'], config['api_hash'], phone_or_string)
        if client:
            clients.append(client)
            logger.info(f"Client for {phone_or_string} successfully started.")
        else:
            logger.error(f"Failed to start client for {phone_or_string}.")
    
    for client in clients:
        load_modules(client)
    
    logger.info(f"Userbot running on {len(clients)} account(s).")
    
    # Start thread for user input
    loop = asyncio.get_event_loop()
    input_thread_instance = threading.Thread(target=input_thread, args=(loop,))
    input_thread_instance.start()
    
    # Set up signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(loop, s)))
    
    try:
        await asyncio.gather(*(client.run_until_disconnected() for client in clients))
    finally:
        input_thread_instance.join()

async def shutdown(loop, signal):
    logger.info(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Exiting...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        logger.info("Program terminated.")