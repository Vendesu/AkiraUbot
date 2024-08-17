from telethon import events, TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerSelf
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.sessions import StringSession
import asyncio

async def tambah_pengguna(api_id, api_hash, telepon):
    try:
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            await client.send_code_request(telepon)
            return client, "OTP_NEEDED"

        string_sesi = StringSession.save(client.session)
        return client, string_sesi
    except Exception as e:
        return None, str(e)

async def verifikasi_otp(client, telepon, kode_otp):
    try:
        await client.sign_in(telepon, kode_otp)
        string_sesi = StringSession.save(client.session)
        return string_sesi, None
    except PhoneCodeInvalidError:
        return None, "Kode OTP tidak valid. Silakan coba lagi."
    except SessionPasswordNeededError:
        return "2FA_NEEDED", None
    except Exception as e:
        return None, str(e)

async def verifikasi_2fa(client, kata_sandi):
    try:
        await client.sign_in(password=kata_sandi)
        string_sesi = StringSession.save(client.session)
        return string_sesi, None
    except Exception as e:
        return None, str(e)

async def interactive_add_user(event, client):
    chat = event.chat_id
    sender = event.sender_id

    async def get_reply(message):
        prompt = await client.send_message(chat, message)
        while True:
            try:
                response = await client.get_messages(chat, limit=1)
                if response and response[0].sender_id == sender and response[0].id > prompt.id:
                    return response[0].text
            except Exception as e:
                print(f"Error in get_reply: {e}")
            await asyncio.sleep(1)

    try:
        await client.send_message(chat, "Proses penambahan akun baru dimulai. Silakan ikuti langkah-langkah berikut:")

        api_id = await get_reply("Balas pesan ini dengan API ID:")
        print(f"Received API ID: {api_id}")
        api_hash = await get_reply("Balas pesan ini dengan API Hash:")
        print(f"Received API Hash: {api_hash}")
        telepon = await get_reply("Balas pesan ini dengan nomor telepon (format: +62xxxxxxxxxx):")
        print(f"Received Phone Number: {telepon}")

        await client.send_message(chat, "Memproses... Mengirim kode OTP.")
        new_client, result = await tambah_pengguna(api_id, api_hash, telepon)

        if result == "OTP_NEEDED":
            otp = await get_reply("Balas pesan ini dengan kode OTP yang telah dikirim ke nomor Anda:")
            print(f"Received OTP: {otp}")

            string_sesi, error = await verifikasi_otp(new_client, telepon, otp)
            if error:
                await client.send_message(chat, f"Error: {error}")
                return
            elif string_sesi == "2FA_NEEDED":
                pwd = await get_reply("Akun ini menggunakan 2FA. Balas pesan ini dengan kata sandi 2FA:")
                print(f"Received 2FA password")

                string_sesi, error = await verifikasi_2fa(new_client, pwd)
                if error:
                    await client.send_message(chat, f"Error: {error}")
                    return
        elif isinstance(result, str) and result.startswith("Error"):
            await client.send_message(chat, f"Terjadi kesalahan: {result}")
            return
        else:
            string_sesi = result

        # Simpan konfigurasi baru
        config = getattr(client, 'config', [])
        new_config = {
            "api_id": api_id,
            "api_hash": api_hash,
            "telepon": telepon,
            "string_sesi": string_sesi
        }
        config.append(new_config)
        
        if hasattr(client, 'save_config') and callable(client.save_config):
            client.save_config(config)
        else:
            client.config = config

        await client.send_message(chat, "Akun baru berhasil ditambahkan!")
    except Exception as e:
        await client.send_message(chat, f"Terjadi kesalahan: {str(e)}")
        print(f"Error in interactive_add_user: {e}")

def load(client):
    @client.on(events.NewMessage(pattern=r'\.adduser'))
    async def handle_adduser(event):
        sender = await event.get_sender()
        me = await client.get_me()
        if sender.id != me.id:
            return  # Hanya pemilik bot yang bisa menggunakan perintah ini

        await interactive_add_user(event, client)

def add_commands(add_command):
    add_command('.adduser', 'Menambahkan akun Telegram baru ke userbot')