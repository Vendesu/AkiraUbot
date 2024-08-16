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

        # Jika sudah terotorisasi, langsung buat string sesi
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
    async def get_response(prompt):
        await event.reply(prompt)
        response = await client.get_messages(event.chat_id, limit=1)
        return response[0].message

    try:
        api_id = await get_response("Silakan masukkan API ID:")
        api_hash = await get_response("Silakan masukkan API Hash:")
        telepon = await get_response("Silakan masukkan nomor telepon (format: +62xxxxxxxxxx):")

        await event.reply("Memproses...")
        new_client, result = await tambah_pengguna(api_id, api_hash, telepon)

        if result == "OTP_NEEDED":
            otp = await get_response("Kode OTP telah dikirim. Silakan masukkan kode OTP:")

            string_sesi, error = await verifikasi_otp(new_client, telepon, otp)
            if error:
                await event.reply(f"Error: {error}")
                return
            elif string_sesi == "2FA_NEEDED":
                pwd = await get_response("Akun ini menggunakan 2FA. Silakan masukkan kata sandi 2FA:")

                string_sesi, error = await verifikasi_2fa(new_client, pwd)
                if error:
                    await event.reply(f"Error: {error}")
                    return

        elif isinstance(result, str) and result.startswith("Error"):
            await event.reply(f"Terjadi kesalahan: {result}")
            return
        else:
            string_sesi = result

        # Simpan konfigurasi baru
        config = client.config  # Asumsikan client memiliki atribut config
        new_config = {
            "api_id": api_id,
            "api_hash": api_hash,
            "telepon": telepon,
            "string_sesi": string_sesi
        }
        config.append(new_config)
        client.save_config(config)  # Asumsikan client memiliki metode save_config

        await event.reply("Akun baru berhasil ditambahkan!")
    except Exception as e:
        await event.reply(f"Terjadi kesalahan: {str(e)}")

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