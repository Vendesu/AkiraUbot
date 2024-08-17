from telethon import events
import time
import psutil
import platform
from .utils import restricted_to_authorized, get_readable_time, humanbytes

def load(client):
    @client.on(events.NewMessage(pattern=r'\.ping'))
    @restricted_to_authorized
    async def ping(event):
        start = time.time()
        message = await event.edit("Pong!")
        end = time.time()
        duration = (end - start) * 1000
        
        # Get system information
        uname = platform.uname()
        boot_time = psutil.boot_time()
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        info = "**🖥️ System Information**\n\n"
        info += f"**System:** {uname.system}\n"
        info += f"**Node Name:** {uname.node}\n"
        info += f"**Release:** {uname.release}\n"
        info += f"**Version:** {uname.version}\n"
        info += f"**Machine:** {uname.machine}\n"
        info += f"**Processor:** {uname.processor}\n\n"
        
        info += f"**Boot Time:** {get_readable_time(int(time.time() - boot_time))}\n\n"
        
        info += "**🧠 CPU Info**\n"
        info += f"**Physical cores:** {psutil.cpu_count(logical=False)}\n"
        info += f"**Total cores:** {psutil.cpu_count(logical=True)}\n"
        info += f"**Max Frequency:** {cpu_freq.max:.2f}Mhz\n"
        info += f"**Min Frequency:** {cpu_freq.min:.2f}Mhz\n"
        info += f"**Current Frequency:** {cpu_freq.current:.2f}Mhz\n"
        info += f"**CPU Usage:** {psutil.cpu_percent()}%\n\n"
        
        info += "**🗄️ Memory Info**\n"
        info += f"**Total:** {humanbytes(memory.total)}\n"
        info += f"**Available:** {humanbytes(memory.available)}\n"
        info += f"**Used:** {humanbytes(memory.used)}\n"
        info += f"**Percentage:** {memory.percent}%\n\n"
        
        info += "**💽 Disk Info**\n"
        info += f"**Total:** {humanbytes(disk.total)}\n"
        info += f"**Used:** {humanbytes(disk.used)}\n"
        info += f"**Free:** {humanbytes(disk.free)}\n"
        info += f"**Percentage:** {disk.percent}%\n\n"
        
        info += f"**🏓 Ping:** `{duration:.2f}ms`"
        
        await message.edit(info)

def add_commands(add_command):
    add_command('.ping', 'Menampilkan informasi sistem dan ping')