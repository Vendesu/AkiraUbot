from telethon import events, TelegramClient
from telethon.tl.types import User
import asyncio
from .utils import restricted_to_authorized
import json
import os

WELCOMED_USERS_FILE = 'welcomed_users_{}.json'
WELCOME_MESSAGE_FILE = 'welcome_message_{}.json'

def load_welcomed_users(user_id):
    file_name = WELCOMED_USERS_FILE.format(user_id)
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return json.load(f)
    return {}

def save_welcomed_users(user_id, welcomed_users):
    file_name = WELCOMED_USERS_FILE.format(user_id)
    with open(file_name, 'w') as f:
        json.dump(welcomed_users, f)

def load_welcome_message(user_id):
    file_name = WELCOME_MESSAGE_FILE.format(user_id)
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return json.load(f)
    return None

def save_welcome_message(user_id, message):
    file_name = WELCOME_MESSAGE_FILE.format(user_id)
    with open(file_name, 'w') as f:
        json.dump(message, f)

def load(client: TelegramClient):
    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def welcome_message(event):
        sender = await event.get_sender()
        if not isinstance(sender, User):
            return

        me = await client.get_me()
        if event.sender_id == me.id:
            return 

        welcomed_users = load_welcomed_users(me.id)
        if str(event.sender_id) in welcomed_users:
            return
       
        welcome_text = load_welcome_message(me.id)
        if not welcome_text:
            welcome_text = (
                "Selamat datang! 👋\n\n"
                "Terima kasih telah menghubungi saya. "
                "Mohon tunggu sebentar, saya akan segera merespon pesan Anda.\n\n"
                "Sementara itu, Anda dapat memberikan detail lebih lanjut tentang pertanyaan atau masalah Anda."
            )
        
        await asyncio.sleep(1)
        await event.reply(welcome_text)
        
        welcomed_users[str(event.sender_id)] = True
        save_welcomed_users(me.id, welcomed_users)
        
        await client.send_message(
            me.id,
            f"Ada pesan baru dari {sender.first_name} (ID: {sender.id}):\n\n{event.text}"
        )

    @client.on(events.NewMessage(pattern=r'\.setwelcome'))
    @restricted_to_authorized
    async def set_welcome_message(event):
        new_welcome = event.text.split(maxsplit=1)
        if len(new_welcome) < 2:
            await event.reply("Silakan berikan pesan selamat datang baru setelah command.")
            return
        
        me = await client.get_me()
        welcome_text = new_welcome[1]
        save_welcome_message(me.id, welcome_text)
        await event.reply("Pesan selamat datang berhasil diperbarui.")

    @client.on(events.NewMessage(pattern=r'\.clearwelcomed'))
    @restricted_to_authorized
    async def clear_welcomed_users(event):
        me = await client.get_me()
        welcomed_users = {}
        save_welcomed_users(me.id, welcomed_users)
        await event.reply("Daftar pengguna yang sudah menerima pesan selamat datang telah dihapus.")

def add_commands(add_command):
    add_command('.setwelcome', 'Mengatur pesan selamat datang baru')
    add_command('.clearwelcomed', 'Menghapus daftar pengguna yang sudah menerima pesan selamat datang')