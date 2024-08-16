import os
import sys
import asyncio
import json
import logging
import random
import signal
import platform
import psutil
import datetime
from telethon import TelegramClient, events
from telethon.tl.types import InputPeerUser
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.sessions import StringSession
import threading
import sqlite3

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konfigurasi file
CONFIG_FILE = 'config.json'
LOG_FILE = 'userbot.log'

# Tambahkan file handler ke logger
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def muat_konfigurasi():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return []
    except json.JSONDecodeError:
        logger.error(f"Kesalahan mendekode {CONFIG_FILE}. File mungkin rusak.")
        return []
    except Exception as e:
        logger.error(f"Kesalahan memuat konfigurasi: {str(e)}")
        return []

def simpan_konfigurasi(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Kesalahan menyimpan konfigurasi: {str(e)}")

async def kirim_pesan_aktivasi(client):
    try:
        me = await client.get_me()
        uname = platform.uname()
        memory = psutil.virtual_memory()
        
        pesan = "🚀 **Userbot Telah Aktif!**\n\n"
        pesan += f"**👤 Pengguna:** {me.first_name}\n"
        pesan += f"**🆔 ID Pengguna:** `{me.id}`\n"
        pesan += f"**💻 Sistem:** {uname.system} {uname.release}\n"
        pesan += f"**🧠 RAM:** {memory.percent}% terpakai\n"
        pesan += f"**⏰ Waktu Aktivasi:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        pesan += "Gunakan `.help` untuk melihat daftar perintah yang tersedia."
        
        await client.send_message('me', pesan)
        logger.info(f"Pesan aktivasi dikirim untuk pengguna {me.id}")
    except Exception as e:
        logger.error(f"Kesalahan mengirim pesan aktivasi: {str(e)}")

async def mulai_client(api_id, api_hash, telepon_atau_string, maksimum_percobaan=5):
    percobaan = 0
    while percobaan < maksimum_percobaan:
        try:
            if telepon_atau_string.startswith('+'):  # Ini adalah nomor telepon
                sesi = f'sesi_{telepon_atau_string}'
                client = TelegramClient(sesi, api_id, api_hash)
                await client.start()
                
                if not await client.is_user_authorized():
                    try:
                        await client.send_code_request(telepon_atau_string)
                        kode = input(f"Masukkan kode verifikasi untuk {telepon_atau_string}: ")
                        await client.sign_in(telepon_atau_string, kode)
                    except SessionPasswordNeededError:
                        kata_sandi = input(f"Masukkan kata sandi 2FA untuk {telepon_atau_string}: ")
                        await client.sign_in(password=kata_sandi)
                
                # Setelah login berhasil, generate dan simpan string sesi
                string_sesi = StringSession.save(client.session)
                logger.info(f"String sesi dibuat untuk {telepon_atau_string}")
                
                # Perbarui konfigurasi dengan string sesi
                konfigurasi = muat_konfigurasi()
                for config in konfigurasi:
                    if config.get('telepon') == telepon_atau_string:
                        config['string_sesi'] = string_sesi
                        simpan_konfigurasi(konfigurasi)
                        break
            
            else:  # Ini adalah string sesi
                client = TelegramClient(StringSession(telepon_atau_string), api_id, api_hash)
                await client.start()
            
            # Kirim pesan aktivasi
            await kirim_pesan_aktivasi(client)
            
            return client
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                percobaan += 1
                waktu_tunggu = random.uniform(1, 5)  # Tunggu acak antara 1 sampai 5 detik
                logger.warning(f"Database terkunci. Mencoba lagi dalam {waktu_tunggu:.2f} detik... (Percobaan {percobaan}/{maksimum_percobaan})")
                await asyncio.sleep(waktu_tunggu)
            else:
                raise  # Jika ini adalah error sqlite yang berbeda, raise error
        except FloodWaitError as e:
            logger.error(f"FloodWaitError: {str(e)}")
            logger.info(f"Menunggu selama {e.seconds} detik sebelum mencoba lagi...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"Kesalahan memulai client: {str(e)}")
            percobaan += 1
            if percobaan >= maksimum_percobaan:
                logger.error(f"Gagal memulai client setelah {maksimum_percobaan} percobaan.")
                return None
            waktu_tunggu = random.uniform(1, 5)
            logger.info(f"Mencoba lagi dalam {waktu_tunggu:.2f} detik... (Percobaan {percobaan}/{maksimum_percobaan})")
            await asyncio.sleep(waktu_tunggu)

    logger.error(f"Gagal memulai client setelah {maksimum_percobaan} percobaan.")
    return None

async def tambah_akun_baru():
    try:
        api_id = input("Masukkan API ID: ")
        api_hash = input("Masukkan API Hash: ")
        gunakan_telepon = input("Gunakan nomor telepon? (y/n): ").lower() == 'y'
        
        if gunakan_telepon:
            telepon = input("Masukkan nomor telepon: ")
            konfigurasi_baru = {
                "api_id": api_id,
                "api_hash": api_hash,
                "telepon": telepon
            }
        else:
            string_sesi = input("Masukkan string sesi: ")
            konfigurasi_baru = {
                "api_id": api_id,
                "api_hash": api_hash,
                "string_sesi": string_sesi
            }
        
        konfigurasi = muat_konfigurasi()
        konfigurasi.append(konfigurasi_baru)
        simpan_konfigurasi(konfigurasi)
        
        client = await mulai_client(api_id, api_hash, telepon if gunakan_telepon else string_sesi)
        if client:
            load_modules(client)
            logger.info(f"Akun baru berhasil ditambahkan dan dimulai.")
            return client
        else:
            logger.error("Gagal menambahkan akun baru.")
            return None
    except Exception as e:
        logger.error(f"Kesalahan menambahkan akun baru: {str(e)}")
        return None

def thread_input(loop):
    while True:
        perintah = input("Ketik 'tambah' untuk menambah akun baru, 'daftar' untuk menampilkan akun aktif, atau 'keluar' untuk mengakhiri: ")
        if perintah.lower() == 'tambah':
            loop.create_task(tambah_akun_baru())
        elif perintah.lower() == 'daftar':
            loop.create_task(daftar_akun_aktif())
        elif perintah.lower() == 'keluar':
            logger.info("Menutup program...")
            loop.stop()
            break

async def daftar_akun_aktif():
    try:
        konfigurasi = muat_konfigurasi()
        logger.info("Akun aktif:")
        for i, config in enumerate(konfigurasi, 1):
            identifikasi = config.get('telepon') or f"Sesi {i}"
            logger.info(f"{i}. {identifikasi}")
    except Exception as e:
        logger.error(f"Kesalahan menampilkan daftar akun aktif: {str(e)}")

def penangan_sinyal(sig, frame):
    logger.info("Menerima sinyal untuk mengakhiri. Menutup dengan aman...")
    for tugas in asyncio.all_tasks():
        tugas.cancel()
    loop = asyncio.get_event_loop()
    loop.stop()

async def main():
    konfigurasi = muat_konfigurasi()
    
    if not konfigurasi:
        logger.info("Tidak ada konfigurasi akun ditemukan. Menambahkan akun baru.")
        await tambah_akun_baru()
        konfigurasi = muat_konfigurasi()
    
    clients = []
    for config in konfigurasi:
        telepon_atau_string = config.get('telepon') or config.get('string_sesi')
        client = await mulai_client(config['api_id'], config['api_hash'], telepon_atau_string)
        if client:
            clients.append(client)
            logger.info(f"Client untuk {telepon_atau_string} berhasil dimulai.")
        else:
            logger.error(f"Gagal memulai client untuk {telepon_atau_string}.")
    
    for client in clients:
        load_modules(client)
    
    logger.info(f"Userbot berjalan pada {len(clients)} akun.")
    
    # Mulai thread untuk input pengguna
    loop = asyncio.get_event_loop()
    thread_input_instance = threading.Thread(target=thread_input, args=(loop,))
    thread_input_instance.start()
    
    # Atur penangan sinyal
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(loop, s)))
    
    try:
        await asyncio.gather(*(client.run_until_disconnected() for client in clients))
    finally:
        thread_input_instance.join()

async def shutdown(loop, signal):
    logger.info(f"Menerima sinyal keluar {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, penangan_sinyal)
    signal.signal(signal.SIGTERM, penangan_sinyal)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program diinterupsi oleh pengguna. Keluar...")
    except Exception as e:
        logger.error(f"Kesalahan tak terduga: {str(e)}")
    finally:
        logger.info("Program berakhir.")