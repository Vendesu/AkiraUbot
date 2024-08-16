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
        try:
            response = await client.get_messages(event.chat_id, limit=1)
            return response[0].message
        except:
            return None

    try:
        await event.reply("Proses penambahan akun baru dimulai. Silakan ikuti langkah-langkah berikut:")
        
        api_id = await get_response("Langkah 1/4: Masukkan API ID:")
        api_hash = await get_response("Langkah 2/4: Masukkan API Hash:")
        telepon = await get_response("Langkah 3/4: Masukkan nomor telepon (format: +62xxxxxxxxxx):")

        if not all([api_id, api_hash, telepon]):
            await event.reply("Proses dibatalkan karena input tidak lengkap.")
            return

        await event.reply("Memproses... Mengirim kode OTP.")
        new_client, result = await tambah_pengguna(api_id, api_hash, telepon)

        if result == "OTP_NEEDED":
            otp = await get_response("Langkah 4/4: Masukkan kode OTP yang telah dikirim ke nomor Anda:")

            if not otp:
                await event.reply("Proses dibatalkan karena OTP tidak dimasukkan.")
                return

            string_sesi, error = await verifikasi_otp(new_client, telepon, otp)
            if error:
                await event.reply(f"Error: {error}")
                return
            elif string_sesi == "2FA_NEEDED":
                pwd = await get_response("Akun ini menggunakan 2FA. Masukkan kata sandi 2FA:")

                if not pwd:
                    await event.reply("Proses dibatalkan karena kata sandi 2FA tidak dimasukkan.")
                    return

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
        config = getattr(client, 'config', [])  # Gunakan list kosong jika tidak ada atribut config
        new_config = {
            "api_id": api_id,
            "api_hash": api_hash,
            "telepon": telepon,
            "string_sesi": string_sesi
        }
        config.append(new_config)
        
        # Cek apakah client memiliki metode save_config
        if hasattr(client, 'save_config') and callable(client.save_config):
            client.save_config(config)
        else:
            # Jika tidak ada metode save_config, kita hanya menyimpan ke atribut config
            client.config = config

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