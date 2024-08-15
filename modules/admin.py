from telethon import events, functions, types
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from .utils import restricted_to_owner
import asyncio
import json
import os

WARNS_FILE = 'user_warns.json'

MAX_WARNS = 3

def load_warns():
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_warns(warns):
    with open(WARNS_FILE, 'w') as f:
        json.dump(warns, f)

user_warns = load_warns()

def load(client):
    @client.on(events.NewMessage(pattern=r'\.ban'))
    @restricted_to_owner
    async def ban_user(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            chat = await event.get_chat()
            try:
                await client(EditBannedRequest(
                    channel=chat.id,
                    user_id=reply.sender_id,
                    banned_rights=ChatBannedRights(until_date=None, view_messages=True)
                ))
                await event.edit("✅ Pengguna berhasil dibanned.")
            except Exception as e:
                await event.edit(f"❌ Gagal melakukan ban: {str(e)}")
        else:
            await event.edit("🔔 Mohon balas ke pesan pengguna yang ingin di-ban.")

    @client.on(events.NewMessage(pattern=r'\.unban'))
    @restricted_to_owner
    async def unban_user(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            chat = await event.get_chat()
            try:
                await client(EditBannedRequest(
                    channel=chat.id,
                    user_id=reply.sender_id,
                    banned_rights=ChatBannedRights(until_date=None, view_messages=False)
                ))
                await event.edit("✅ Pengguna berhasil di-unban.")
            except Exception as e:
                await event.edit(f"❌ Gagal melakukan unban: {str(e)}")
        else:
            await event.edit("🔔 Mohon balas ke pesan pengguna yang ingin di-unban.")

    @client.on(events.NewMessage(pattern=r'\.kick'))
    @restricted_to_owner
    async def kick_user(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            chat = await event.get_chat()
            try:
                await client.kick_participant(chat.id, reply.sender_id)
                await event.edit("👢 Pengguna berhasil dikeluarkan dari grup.")
            except Exception as e:
                await event.edit(f"❌ Gagal mengeluarkan pengguna: {str(e)}")
        else:
            await event.edit("🔔 Mohon balas ke pesan pengguna yang ingin dikeluarkan.")

    @client.on(events.NewMessage(pattern=r'\.mute'))
    @restricted_to_owner
    async def mute_user(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            chat = await event.get_chat()
            try:
                await client(EditBannedRequest(
                    channel=chat.id,
                    user_id=reply.sender_id,
                    banned_rights=ChatBannedRights(until_date=None, send_messages=True)
                ))
                await event.edit("🔇 Pengguna berhasil di-mute.")
            except Exception as e:
                await event.edit(f"❌ Gagal melakukan mute: {str(e)}")
        else:
            await event.edit("🔔 Mohon balas ke pesan pengguna yang ingin di-mute.")

    @client.on(events.NewMessage(pattern=r'\.unmute'))
    @restricted_to_owner
    async def unmute_user(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            chat = await event.get_chat()
            try:
                await client(EditBannedRequest(
                    channel=chat.id,
                    user_id=reply.sender_id,
                    banned_rights=ChatBannedRights(until_date=None, send_messages=False)
                ))
                await event.edit("🔊 Pengguna berhasil di-unmute.")
            except Exception as e:
                await event.edit(f"❌ Gagal melakukan unmute: {str(e)}")
        else:
            await event.edit("🔔 Mohon balas ke pesan pengguna yang ingin di-unmute.")

    @client.on(events.NewMessage(pattern=r'\.warn'))
    @restricted_to_owner
    async def warn_user(event):
        global user_warns
        if event.is_reply:
            reply = await event.get_reply_message()
            chat = await event.get_chat()
            user_id = str(reply.sender_id)
            chat_id = str(chat.id)
            
            if chat_id not in user_warns:
                user_warns[chat_id] = {}
            if user_id not in user_warns[chat_id]:
                user_warns[chat_id][user_id] = 0
            
            user_warns[chat_id][user_id] += 1
            warn_count = user_warns[chat_id][user_id]
            
            save_warns(user_warns)
            
            if warn_count >= MAX_WARNS:
                try:
                    await client(EditBannedRequest(
                        channel=chat.id,
                        user_id=reply.sender_id,
                        banned_rights=ChatBannedRights(until_date=None, view_messages=True)
                    ))
                    await event.edit(f"⚠️ Pengguna telah mencapai batas peringatan ({MAX_WARNS}) dan telah dibanned.")
                    del user_warns[chat_id][user_id]
                    save_warns(user_warns)
                except Exception as e:
                    await event.edit(f"❌ Gagal melakukan ban otomatis: {str(e)}")
            else:
                await event.edit(f"⚠️ Pengguna telah diberikan peringatan ({warn_count}/{MAX_WARNS}).")
        else:
            await event.edit("🔔 Mohon balas ke pesan pengguna yang ingin diberi peringatan.")

    @client.on(events.NewMessage(pattern=r'\.unwarn'))
    @restricted_to_owner
    async def unwarn_user(event):
        global user_warns
        if event.is_reply:
            reply = await event.get_reply_message()
            chat = await event.get_chat()
            user_id = str(reply.sender_id)
            chat_id = str(chat.id)
            
            if chat_id in user_warns and user_id in user_warns[chat_id]:
                user_warns[chat_id][user_id] = max(0, user_warns[chat_id][user_id] - 1)
                warn_count = user_warns[chat_id][user_id]
                save_warns(user_warns)
                await event.edit(f"✅ Satu peringatan telah dihapus. Peringatan saat ini: {warn_count}/{MAX_WARNS}.")
            else:
                await event.edit("👍 Pengguna ini tidak memiliki peringatan.")
        else:
            await event.edit("🔔 Mohon balas ke pesan pengguna yang ingin dihapus peringatannya.")

    @client.on(events.NewMessage(pattern=r'\.warns'))
    @restricted_to_owner
    async def check_warns(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            chat = await event.get_chat()
            user_id = str(reply.sender_id)
            chat_id = str(chat.id)
            
            if chat_id in user_warns and user_id in user_warns[chat_id]:
                warn_count = user_warns[chat_id][user_id]
                await event.edit(f"ℹ️ Pengguna ini memiliki {warn_count}/{MAX_WARNS} peringatan.")
            else:
                await event.edit("👍 Pengguna ini tidak memiliki peringatan.")
        else:
            await event.edit("🔔 Mohon balas ke pesan pengguna yang ingin diperiksa peringatannya.")

    @client.on(events.NewMessage(pattern=r'\.resetwarns'))
    @restricted_to_owner
    async def reset_warns(event):
        global user_warns
        if event.is_reply:
            reply = await event.get_reply_message()
            chat = await event.get_chat()
            user_id = str(reply.sender_id)
            chat_id = str(chat.id)
            
            if chat_id in user_warns and user_id in user_warns[chat_id]:
                del user_warns[chat_id][user_id]
                save_warns(user_warns)
                await event.edit("🔄 Semua peringatan untuk pengguna ini telah direset.")
            else:
                await event.edit("👍 Pengguna ini tidak memiliki peringatan.")
        else:
            await event.edit("🔔 Mohon balas ke pesan pengguna yang ingin direset peringatannya.")

    @client.on(events.NewMessage(pattern=r'\.pin'))
    @restricted_to_owner
    async def pin_message(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            try:
                await client.pin_message(event.chat_id, reply.id, notify=True)
                await event.edit("📌 Pesan berhasil dipinned.")
            except Exception as e:
                await event.edit(f"❌ Gagal melakukan pin: {str(e)}")
        else:
            await event.edit("🔔 Mohon balas ke pesan yang ingin di-pin.")

    @client.on(events.NewMessage(pattern=r'\.unpin'))
    @restricted_to_owner
    async def unpin_message(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            try:
                await client.unpin_message(event.chat_id, reply.id)
                await event.edit("📌 Pesan berhasil di-unpin.")
            except Exception as e:
                await event.edit(f"❌ Gagal melakukan unpin: {str(e)}")
        else:
            try:
                await client.unpin_message(event.chat_id)
                await event.edit("📌 Pesan terakhir yang di-pin berhasil di-unpin.")
            except Exception as e:
                await event.edit(f"❌ Gagal melakukan unpin: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.purge'))
    @restricted_to_owner
    async def purge_messages(event):
        if event.is_reply:
            chat = await event.get_chat()
            messages = []
            count = 0
            async for message in client.iter_messages(chat, min_id=event.reply_to_msg_id):
                messages.append(message)
                count += 1
                if len(messages) == 100:
                    await client.delete_messages(chat, messages)
                    messages = []
            
            if messages:
                await client.delete_messages(chat, messages)
            
            await event.edit(f"🗑️ Berhasil menghapus {count} pesan.")
        else:
            await event.edit("🔔 Mohon balas ke pesan untuk mulai menghapus.")

def add_commands(add_command):
    add_command('.ban', '🚫 Mem-ban pengguna dari grup (balas ke pesan pengguna)')
    add_command('.unban', '✅ Membatalkan ban pengguna dari grup (balas ke pesan pengguna)')
    add_command('.kick', '👢 Mengeluarkan pengguna dari grup (balas ke pesan pengguna)')
    add_command('.mute', '🔇 Membisukan pengguna dalam grup (balas ke pesan pengguna)')
    add_command('.unmute', '🔊 Membatalkan bisukan pengguna dalam grup (balas ke pesan pengguna)')
    add_command('.warn', '⚠️ Memberikan peringatan kepada pengguna (balas ke pesan pengguna)')
    add_command('.unwarn', '🔙 Menghapus satu peringatan dari pengguna (balas ke pesan pengguna)')
    add_command('.warns', 'ℹ️ Memeriksa jumlah peringatan pengguna (balas ke pesan pengguna)')
    add_command('.resetwarns', '🔄 Mereset semua peringatan pengguna (balas ke pesan pengguna)')
    add_command('.pin', '📌 Menyematkan pesan dalam grup (balas ke pesan)')
    add_command('.unpin', '📌 Membatalkan sematan pesan dalam grup (balas ke pesan atau gunakan tanpa balasan untuk unpin pesan terakhir)')
    add_command('.purge', '🗑️ Menghapus semua pesan dari pesan yang dibalas hingga pesan terbaru')