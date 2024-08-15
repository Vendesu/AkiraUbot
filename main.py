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

async def send_activation_message(client):
    me = await client.get_me()
    uname = platform.uname()
    memory = psutil.virtual_memory()
    
    message = "🚀 **Userbot Telah Aktif!**\n\n"
    message += f"**👤 Pengguna:** {me.first_name}\n"
    message += f"**🆔 User ID:** `{me.id}`\n"
    message += f"**💻 Sistem:** {uname.system} {uname.release}\n"
    message += f"**🧠 RAM:** {memory.percent}% terpakai\n"
    message += f"**⏰ Waktu Aktivasi:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    message += "Gunakan `.help` untuk melihat daftar perintah yang tersedia."
    
    await client.send_message('me', message)

async def main():
    print("Selamat datang di Userbot Telegram!")

    # Cek apakah file konfigurasi sudah ada
    if not os.path.exists(CONFIG_FILE):
        print("Konfigurasi tidak ditemukan. Silakan masukkan informasi berikut:")
        API_ID = update_env('API_ID', 'Masukkan API ID: ')
        API_HASH = update_env('API_HASH', 'Masukkan API Hash: ')
        PHONE_NUMBER = update_env('PHONE_NUMBER', 'Masukkan nomor telepon (dengan kode negara, contoh: +62xxx): ')
    else:
        API_ID = os.getenv('API_ID')
        API_HASH = os.getenv('API_HASH')
        PHONE_NUMBER = os.getenv('PHONE_NUMBER')

    # Cek apakah session string sudah ada
    SESSION_STRING = os.getenv('SESSION_STRING')

    if SESSION_STRING:
        print("Menggunakan sesi yang tersimpan.")
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    else:
        print("Membuat sesi baru.")
        client = TelegramClient(StringSession(), API_ID, API_HASH)

    try:
        print("Mencoba untuk terhubung...")
        await client.start(phone=PHONE_NUMBER)
        
        # Tambahkan kode berikut untuk mengatur ID pemilik
        me = await client.get_me()
        set_owner_id(me.id)
        print(f"ID pemilik diatur: {me.id}")

        if not SESSION_STRING:
            # Simpan string sesi baru ke .env
            session_string = client.session.save()
            set_key(CONFIG_FILE, 'SESSION_STRING', session_string)
            print("String sesi baru telah disimpan dalam file konfigurasi")
        
        print('Userbot telah aktif!')
        
        # Kirim pesan aktivasi ke Pesan Tersimpan
        await send_activation_message(client)
        
        # Load semua modul
        import modules
        modules.load_modules(client)
        
        print('Semua modul telah dimuat. Userbot siap digunakan!')
        print('Gunakan .help untuk melihat daftar perintah yang tersedia.')
        
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
        print("Pastikan Anda memasukkan API ID, API Hash, dan nomor telepon dengan benar.")
        # Jika terjadi kesalahan, hapus file konfigurasi agar pengguna dapat memasukkan informasi lagi
        os.remove(CONFIG_FILE)
        print("File konfigurasi telah dihapus. Silakan jalankan program kembali dan masukkan informasi yang benar.")

if __name__ == '__main__':
    asyncio.run(main())