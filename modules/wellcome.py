from telethon import events, TelegramClient
from telethon.tl.types import User
import asyncio
from .utils import restricted_to_owner
import json
import os

WELCOMED_USERS_FILE = 'welcomed_users.json'

welcomed_users = {}

def load(client: TelegramClient):
    global welcomed_users
        
    if os.path.exists(WELCOMED_USERS_FILE):
        with open(WELCOMED_USERS_FILE, 'r') as f:
            welcomed_users = json.load(f)

    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def welcome_message(event):
        sender = await event.get_sender()
        if not isinstance(sender, User):
            return

        me = await client.get_me()
        if event.sender_id == me.id:
            return 

        if str(event.sender_id) in welcomed_users:
            return
       
        welcome_text = (
            "Selamat datang! 👋\n\n"
            "Terima kasih telah menghubungi saya. "
            "Mohon tunggu sebentar, saya akan segera merespon pesan Anda.\n\n"
            "Sementara itu, Anda dapat memberikan detail lebih lanjut tentang pertanyaan atau masalah Anda."
        )
        
        await asyncio.sleep(1)
        await event.reply(welcome_text)
        
        welcomed_users[str(event.sender_id)] = True
        with open(WELCOMED_USERS_FILE, 'w') as f:
            json.dump(welcomed_users, f)
        
        await client.send_message(
            me.id,
            f"Ada pesan baru dari {sender.first_name} (ID: {sender.id}):\n\n{event.text}"
        )

    @client.on(events.NewMessage(pattern=r'\.setwelcome'))
    @restricted_to_owner
    async def set_welcome_message(event):       
        new_welcome = event.text.split(maxsplit=1)
        if len(new_welcome) < 2:
            await event.reply("Silakan berikan pesan selamat datang baru setelah command.")
            return
        
        global welcome_text
        welcome_text = new_welcome[1]
        await event.reply("Pesan selamat datang berhasil diperbarui.")

    @client.on(events.NewMessage(pattern=r'\.clearwelcomed'))
    @restricted_to_owner
    async def clear_welcomed_users(event):
        global welcomed_users
        welcomed_users.clear()
        with open(WELCOMED_USERS_FILE, 'w') as f:
            json.dump(welcomed_users, f)
        await event.reply("Daftar pengguna yang sudah menerima pesan selamat datang telah dihapus.")

def add_commands(add_command):
    add_command('.setwelcome', 'Mengatur pesan selamat datang baru')
    add_command('.clearwelcomed', 'Menghapus daftar pengguna yang sudah menerima pesan selamat datang')