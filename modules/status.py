from telethon import events, __version__ as telethon_version
import time
import psutil
import sys
import aiohttp
import os
from .utils import restricted_to_owner, get_readable_time

START_TIME_FILE = "bot_start_time.txt"

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

async def get_isp_info():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.ipify.org') as response:
                ip = await response.text()

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://ipapi.co/{ip}/json/') as response:
                data = await response.json()
                return data.get('org', 'Tidak dapat mengambil informasi ISP')
    except:
        return "Tidak dapat mengambil informasi ISP"

def load(client):
    @client.on(events.NewMessage(pattern=r'\.status'))
    @restricted_to_owner
    async def status(event):
        await event.edit("__Mengambil status...__")
        
        start_time = time.time()
        
        bot_uptime = get_bot_uptime()
        
        boot_time = psutil.boot_time()
        server_uptime = get_readable_time(int(time.time() - boot_time))
               
        python_version = sys.version.split()[0]
                
        isp_info = await get_isp_info()
        
        end_time = time.time()
               
        rtt = (end_time - start_time) * 1000
        
        status_message = "🤖 **System Status**\n\n"
        status_message += f"🚀 **Userbot Project:** AkiraUBot\n"
        status_message += f"🔢 **Version:** 1.0\n"
        status_message += f"🗣 **Bahasa:** Indonesia\n"
        status_message += f"⚡ **RTT:** {rtt:.2f}ms\n"
        status_message += f"🕒 **Bot uptime:** {bot_uptime}\n"
        status_message += f"💻 **Server uptime:** {server_uptime}\n"
        status_message += f"🌐 **ISP:** {isp_info}\n\n"
        status_message += f"📡 **Telethon version:** {telethon_version}\n"
        status_message += f"🐍 **Python version:** {python_version}\n"
        status_message += "👨‍💻 **Code by Pop Ice Taro**\n"        
        status_message += "💬 Chat Akira: @akiraneverdie\n"
        status_message += "🚀 Join Grup Akira: @akiratunnel\n\n"
        status_message += "⚠️ **PERHATIAN**:\n"
        status_message += "Bot ini 100% GRATIS. Jika ada yang menjual, "
        status_message += "silakan laporkan ke @akiraneverdie"
        
        await event.edit(status_message)

def add_commands(add_command):
    add_command('.status', 'Menampilkan status sistem dan bot')