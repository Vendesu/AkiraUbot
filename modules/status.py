from telethon import events, __version__ as telethon_version
import time
import psutil
import sys
import os
from .utils import restricted_to_authorized

FILE_VERSI = os.path.join(os.path.dirname(__file__), '..', 'version.txt')

LINK_GITHUB = "https://github.com/Vendesu/AkiraUBot"

def cek_versi():
    try:
        with open(FILE_VERSI, 'r') as berkas:
            return berkas.read().strip()
    except FileNotFoundError:
        return "Versi tidak diketahui"

def format_durasi(detik):
    menit, detik = divmod(detik, 60)
    jam, menit = divmod(menit, 60)
    hari, jam = divmod(jam, 24)
    
    hasil = []
    if hari > 0:
        hasil.append(f"{hari} hari")
    if jam > 0:
        hasil.append(f"{jam} jam")
    if menit > 0:
        hasil.append(f"{menit} menit")
    if detik > 0:
        hasil.append(f"{detik} detik")
    
    return ", ".join(hasil)

def hitung_umur_komputer():
    waktu_nyala = psutil.boot_time()
    lama_hidup = int(time.time() - waktu_nyala)
    return format_durasi(lama_hidup)

def load(client):
    @client.on(events.NewMessage(pattern=r'\.status'))
    @restricted_to_authorized
    async def tampilkan_status(event):
        versi_bot = cek_versi()
        umur_komputer = hitung_umur_komputer()
        versi_python = sys.version.split()[0]

        penggunaan_cpu = psutil.cpu_percent()
        penggunaan_ram = psutil.virtual_memory().percent
        penggunaan_disk = psutil.disk_usage('/').percent

        pesan_status = "🤖 **Hai! Ini Status AkiraUBot**\n\n"
        pesan_status += f"🚀 **Proyek:** AkiraUBot\n"
        pesan_status += f"🔢 **Versi:** {versi_bot}\n"
        pesan_status += f"🗣 **Bahasa:** Indonesia\n"
        pesan_status += f"💻 **Komputer sudah menyala selama:** {umur_komputer}\n"
        pesan_status += f"🐍 **Versi Python:** {versi_python}\n"
        pesan_status += f"📡 **Versi Telethon:** {telethon_version}\n\n"
        pesan_status += f"🖥️ **CPU lagi kerja:** {penggunaan_cpu}%\n"
        pesan_status += f"🧠 **RAM terpakai:** {penggunaan_ram}%\n"
        pesan_status += f"💽 **Disk penuh:** {penggunaan_disk}%\n\n"
        pesan_status += f"👨‍💻 **Dibuat dengan ❤️ oleh:** Pop Ice Taro\n"
        pesan_status += f"💬 **Mau ngobrol sama yang bikin?** @akiraneverdie\n"
        pesan_status += f"🚀 **Gabung grup pendukung:** @akiratunnel\n"
        pesan_status += f"📦 **Cek kode sumbernya di:** [GitHub AkiraUBot]({LINK_GITHUB})\n\n"
        pesan_status += "⚠️ **INGAT YA:**\n"
        pesan_status += "Bot ini GRATIS selamanya. Kalo ada yang jual, "
        pesan_status += "langsung laporin aja ke @akiraneverdie. Jangan mau ditipu!"

        await event.reply(pesan_status)

def add_commands(add_command):
    add_command('.status', '📊 Cek kondisi bot, lagi sehat atau nggak')