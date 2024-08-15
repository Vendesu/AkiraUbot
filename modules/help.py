from telethon import events
from collections import defaultdict
from .utils import restricted_to_owner

command_list = defaultdict(list)

def load(client):
    @client.on(events.NewMessage(pattern=r'\.help(?: (.+))?'))
    @restricted_to_owner
    async def help_command(event):
        command = event.pattern_match.group(1)
        if command:
            await show_command_help(event, command)
        else:
            await show_all_commands(event)

    async def show_all_commands(event):
        total_commands = sum(len(commands) for commands in command_list.values())
        help_text = f"📚 **Daftar Perintah AkiraUBot:**\n"
        help_text += f"💡 Total Perintah: {total_commands}\n\n"
        
        for module, commands in sorted(command_list.items()):
            if commands: 
                help_text += f"**{module.capitalize()}**\n"
                for cmd, desc in commands:
                    help_text += f"  • `{cmd}`: {desc}\n"
                help_text += "\n"
        help_text += "Gunakan `.help <perintah>` untuk informasi lebih detail tentang perintah tertentu."
                
        if len(help_text) > 4096:
            parts = [help_text[i:i+4096] for i in range(0, len(help_text), 4096)]
            for part in parts:
                await event.edit(part)
        else:
            await event.edit(help_text)

    async def show_command_help(event, command):
        for module, commands in command_list.items():
            for cmd, desc in commands:
                if cmd.split()[0] == command:
                    help_text = f"📌 **Perintah:** `{cmd}`\n"
                    help_text += f"📂 **Modul:** {module.capitalize()}\n"
                    help_text += f"📝 **Deskripsi:** {desc}"
                    await event.edit(help_text)
                    return
        await event.edit(f"❌ Perintah '{command}' tidak ditemukan.")

def add_module_commands(add_command_func):
    module_name = add_command_func.__module__.split('.')[-1]
    add_command_func(lambda cmd, desc: command_list[module_name].append((cmd, desc)))

def add_commands(add_command):
    add_command('.help', '📚 Menampilkan daftar semua perintah')
    add_command('.help <perintah>', '🔍 Menampilkan informasi detail tentang perintah tertentu')