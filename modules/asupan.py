from telethon import events
from telethon.tl.types import InputMessagesFilterVideo, InputMessagesFilterVoice
import random
from .utils import restricted_to_owner

# Daftar chat yang di-blacklist (opsional)
BLACKLIST_CHAT = []

async def get_random_media(client, channel, filter_type):
    media_list = [
        message
        async for message in client.iter_messages(
            channel, filter=filter_type
        )
    ]
    return random.choice(media_list) if media_list else None

def load(client):
    @client.on(events.NewMessage(pattern=r'\.asupan'))
    @restricted_to_owner
    async def asupan(event):
        xx = await event.reply("Tunggu Sebentar...")
        try:
            asupan_msg = await get_random_media(client, "@tedeasupancache", InputMessagesFilterVideo)
            if asupan_msg:
                await client.send_file(
                    event.chat_id,
                    file=asupan_msg,
                    reply_to=event.message.id
                )
                await xx.delete()
            else:
                await xx.edit("Tidak bisa menemukan video asupan.")
        except Exception as e:
            await xx.edit(f"Terjadi kesalahan: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.desahcewe'))
    @restricted_to_owner
    async def desahcewe(event):
        if event.chat_id in BLACKLIST_CHAT:
            return await event.reply("Perintah ini Dilarang digunakan di Group ini")
        
        xx = await event.reply("Tunggu Sebentar...")
        try:
            desah_msg = await get_random_media(client, "@desahancewesangesange", InputMessagesFilterVoice)
            if desah_msg:
                await client.send_file(
                    event.chat_id,
                    file=desah_msg,
                    reply_to=event.message.id
                )
                await xx.delete()
            else:
                await xx.edit("Tidak bisa menemukan desahan cewe.")
        except Exception as e:
            await xx.edit(f"Terjadi kesalahan: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.desahcowo'))
    @restricted_to_owner
    async def desahcowo(event):
        if event.chat_id in BLACKLIST_CHAT:
            return await event.reply("Perintah ini Dilarang digunakan di Group ini")
        
        xx = await event.reply("Tunggu Sebentar...")
        try:
            desah_msg = await get_random_media(client, "@desahancowokkkk", InputMessagesFilterVoice)
            if desah_msg:
                await client.send_file(
                    event.chat_id,
                    file=desah_msg,
                    reply_to=event.message.id
                )
                await xx.delete()
            else:
                await xx.edit("Tidak bisa menemukan desahan cowo.")
        except Exception as e:
            await xx.edit(f"Terjadi kesalahan: {str(e)}")

def add_commands(add_command):
    add_command('.asupan', 'Untuk Mengirim video asupan secara random')
    add_command('.desahcewe', 'Untuk Mengirim voice desah cewe secara random')
    add_command('.desahcowo', 'Untuk Mengirim voice desah cowo secara random')