from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import os
from dotenv import load_dotenv, set_key
from modules.utils import set_owner_id
import platform
import psutil

# Fungsi untuk meminta input dari pengguna dan memperbarui .env
def update_env(key, prompt):
    value = input(prompt)
    set_key('.env', key, value)
    return value

# Memuat variabel lingkungan
load_dotenv()

# File untuk menyimpan konfigurasi
CONFIG_FILE = '.env'

import os
import sys
from telethon import TelegramClient, events
from telethon.tl.types import InputPeerUser
from telethon.errors import SessionPasswordNeededError
import asyncio
from modules import load_modules
import json
from telethon.sessions import StringSession
import threading
import platform
import psutil
import datetime

# File konfigurasi untuk menyimpan informasi akun
CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return []

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

async def send_activation_message(client):
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

async def start_client(api_id, api_hash, phone_or_string):
    if phone_or_string.startswith('+'):  # Ini adalah nomor telepon
        session = f'session_{phone_or_string}'
        client = TelegramClient(session, api_id, api_hash)
        await client.start()
        
        if not await client.is_user_authorized():
            try:
                await client.send_code_request(phone_or_string)
                code = input(f"Masukkan kode verifikasi untuk {phone_or_string}: ")
                await client.sign_in(phone_or_string, code)
            except SessionPasswordNeededError:
                password = input(f"Masukkan password 2FA untuk {phone_or_string}: ")
                await client.sign_in(password=password)
        
        # Setelah login berhasil, generate dan simpan session string
        string_session = StringSession.save(client.session)
        print(f"Session string untuk {phone_or_string}: {string_session}")
        
        # Update konfigurasi dengan session string
        configs = load_config()
        for config in configs:
            if config.get('phone') == phone_or_string:
                config['session_string'] = string_session
                save_config(configs)
                break
    
    else:  # Ini adalah session string
        client = TelegramClient(StringSession(phone_or_string), api_id, api_hash)
        await client.start()
    
    # Kirim pesan aktivasi
    await send_activation_message(client)
    
    return client

async def add_new_account():
    api_id = input("Masukkan API ID: ")
    api_hash = input("Masukkan API Hash: ")
    use_phone = input("Gunakan nomor telepon? (y/n): ").lower() == 'y'
    
    if use_phone:
        phone = input("Masukkan nomor telepon: ")
        new_config = {
            "api_id": api_id,
            "api_hash": api_hash,
            "phone": phone
        }
    else:
        session_string = input("Masukkan session string: ")
        new_config = {
            "api_id": api_id,
            "api_hash": api_hash,
            "session_string": session_string
        }
    
    configs = load_config()
    configs.append(new_config)
    save_config(configs)
    
    client = await start_client(api_id, api_hash, phone if use_phone else session_string)
    load_modules(client)
    print(f"Akun baru berhasil ditambahkan dan dimulai.")
    return client

def input_thread(loop):
    while True:
        command = input("Ketik 'add' untuk menambahkan akun baru, atau 'exit' untuk keluar: ")
        if command.lower() == 'add':
            loop.create_task(add_new_account())
        elif command.lower() == 'exit':
            print("Menutup program...")
            loop.stop()
            break

async def main():
    configs = load_config()
    
    if not configs:
        print("Tidak ada konfigurasi akun. Tambahkan akun baru.")
        await add_new_account()
        configs = load_config()
    
    clients = []
    for config in configs:
        phone_or_string = config.get('phone') or config.get('session_string')
        client = await start_client(config['api_id'], config['api_hash'], phone_or_string)
        clients.append(client)
        print(f"Client untuk {phone_or_string} berhasil dimulai.")
    
    for client in clients:
        load_modules(client)
    
    print(f"Userbot berjalan pada {len(clients)} akun.")
    
    # Memulai thread untuk input pengguna
    loop = asyncio.get_event_loop()
    input_thread_instance = threading.Thread(target=input_thread, args=(loop,))
    input_thread_instance.start()
    
    try:
        await asyncio.gather(*(client.run_until_disconnected() for client in clients))
    finally:
        input_thread_instance.join()

if __name__ == '__main__':
    asyncio.run(main())