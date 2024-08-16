from telethon import events, __version__ as telethon_version
import time
import psutil
import sys
import os
from .utils import restricted_to_owner, get_readable_time

# File untuk menyimpan waktu mulai bot
START_TIME_FILE = "bot_start_time.txt"
# File untuk menyimpan versi
VERSION_FILE = os.path.join(os.path.dirname(__file__), '..', 'version.txt')

def save_start_time():
    with open(START_TIME_FILE, "w") as f:
        f.write(str(time.time()))

def get_bot_uptime():
    try:
        with open(START_TIME_FILE, "r") as f:
            start_time = float(f.read())
        return get_readable_time(int(time.time() - start_time))
    except:
        return "Tidak tersedia"

def get_version():
    try:
        with open(VERSION_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Versi tidak diketahui"

def get_server_uptime():
    boot_time = psutil.boot_time()
    uptime = time.time() - boot_time
    return get_readable_time(int(uptime))

def load(client):
    @client.on(events.NewMessage(pattern=r'\.status'))
    @restricted_to_owner
    async def status(event):
        version = get_version()
        bot_uptime = get_bot_uptime()
        server_uptime = get_server_uptime()
        python_version = sys.version.split()[0]

        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        status_message = "🤖 **Status AkiraUBot**\n\n"
        status_message += f"🔢 **Versi Bot:** {version}\n"
        status_message += f"🕒 **Uptime Bot:** {bot_uptime}\n"
        status_message += f"💻 **Uptime Server:** {server_uptime}\n"
        status_message += f"🐍 **Versi Python:** {python_version}\n"
        status_message += f"📡 **Versi Telethon:** {telethon_version}\n\n"
        status_message += f"🖥️ **Penggunaan CPU:** {cpu_usage}%\n"
        status_message += f"🧠 **Penggunaan RAM:** {ram_usage}%\n"
        status_message += f"💽 **Penggunaan Disk:** {disk_usage}%\n"

        await event.reply(status_message)

def add_commands(add_command):
    add_command('.status', '📊 Menampilkan status bot termasuk versi, uptime, dan penggunaan sistem')