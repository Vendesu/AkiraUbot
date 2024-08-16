from telethon import events, TelegramClient
from telethon.tl.types import InputPeerUser
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

def load(client):
    @client.on(events.NewMessage(pattern=r'\.adduser'))
    async def handle_adduser(event):
        sender = await event.get_sender()
        me = await client.get_me()
        if sender.id != me.id:
            return  # Hanya pemilik bot yang bisa menggunakan perintah ini

        chat = await event.get_chat()
        async with client.conversation(chat) as conv:
            await conv.send_message("Silakan masukkan API ID:")
            api_id_msg = await conv.get_response()
            api_id = api_id_msg.text

            await conv.send_message("Silakan masukkan API Hash:")
            api_hash_msg = await conv.get_response()
            api_hash = api_hash_msg.text

            await conv.send_message("Silakan masukkan nomor telepon (format: +62xxxxxxxxxx):")
            telepon_msg = await conv.get_response()
            telepon = telepon_msg.text

            await conv.send_message("Memproses...")
            new_client, result = await tambah_pengguna(api_id, api_hash, telepon)

            if result == "OTP_NEEDED":
                await conv.send_message("Kode OTP telah dikirim. Silakan masukkan kode OTP:")
                otp_msg = await conv.get_response()
                otp = otp_msg.text

                string_sesi, error = await verifikasi_otp(new_client, telepon, otp)
                if error:
                    await conv.send_message(f"Error: {error}")
                    return
                elif string_sesi == "2FA_NEEDED":
                    await conv.send_message("Akun ini menggunakan 2FA. Silakan masukkan kata sandi 2FA:")
                    pwd_msg = await conv.get_response()
                    pwd = pwd_msg.text

                    string_sesi, error = await verifikasi_2fa(new_client, pwd)
                    if error:
                        await conv.send_message(f"Error: {error}")
                        return

            elif isinstance(result, str) and result.startswith("Error"):
                await conv.send_message(f"Terjadi kesalahan: {result}")
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

            await conv.send_message("Akun baru berhasil ditambahkan!")

def add_commands(add_command):
    add_command('.adduser', 'Menambahkan akun Telegram baru ke userbot')