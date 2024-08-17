from telethon import events, Button
from collections import defaultdict
from .utils import restricted_to_authorized
import math
import logging

logger = logging.getLogger(__name__)
command_list = defaultdict(list)

def load(client):
    @client.on(events.NewMessage(pattern=r'\.help(?: (.+))?'))
    @restricted_to_authorized
    async def help_command(event):
        try:
            command = event.pattern_match.group(1)
            if command:
                await show_command_help(event, command)
            else:
                await show_module_list(event, 0)
        except Exception as e:
            logger.error(f"Error in help_command: {str(e)}")
            await event.reply("An error occurred while processing the help command.")

    async def show_module_list(event, page):
        try:
            modules = sorted(command_list.keys())
            total_pages = math.ceil(len(modules) / 9)
            start = page * 9
            end = start + 9
            current_modules = modules[start:end]

            buttons = []
            for i in range(0, len(current_modules), 3):
                row = [Button.inline(module.capitalize(), f"module:{module}") for module in current_modules[i:i+3]]
                buttons.append(row)

            nav_buttons = []
            if page > 0:
                nav_buttons.append(Button.inline("⬅️ Prev", f"page:{page-1}"))
            if end < len(modules):
                nav_buttons.append(Button.inline("Next ➡️", f"page:{page+1}"))
            if nav_buttons:
                buttons.append(nav_buttons)

            text = f"📚 **Daftar Modul AkiraUBot** (Halaman {page+1}/{total_pages}):\n\n"
            text += "Pilih modul untuk melihat perintah yang tersedia."

            logger.info(f"Sending module list with {len(buttons)} button rows")
            await event.reply(text, buttons=buttons)
        except Exception as e:
            logger.error(f"Error in show_module_list: {str(e)}")
            await event.reply("An error occurred while displaying the module list.")

    @client.on(events.CallbackQuery(pattern=r"module:(.+)"))
    async def module_callback(event):
        try:
            module_name = event.data_match.group(1).decode()
            await show_module_commands(event, module_name)
        except Exception as e:
            logger.error(f"Error in module_callback: {str(e)}")
            await event.answer("An error occurred while processing your selection.")

    @client.on(events.CallbackQuery(pattern=r"page:(\d+)"))
    async def page_callback(event):
        try:
            page = int(event.data_match.group(1))
            await show_module_list(event, page)
        except Exception as e:
            logger.error(f"Error in page_callback: {str(e)}")
            await event.answer("An error occurred while changing the page.")

    async def show_module_commands(event, module_name):
        try:
            if module_name in command_list:
                text = f"📚 **Perintah dalam modul {module_name.capitalize()}:**\n\n"
                for cmd, desc in command_list[module_name]:
                    text += f"• `{cmd}`: {desc}\n\n"
                await event.edit(text, buttons=[Button.inline("🔙 Kembali", "back")])
            else:
                await event.edit(f"❌ Modul '{module_name}' tidak ditemukan.")
        except Exception as e:
            logger.error(f"Error in show_module_commands: {str(e)}")
            await event.edit("An error occurred while displaying module commands.")

    @client.on(events.CallbackQuery(pattern=r"back"))
    async def back_callback(event):
        try:
            await show_module_list(event, 0)
        except Exception as e:
            logger.error(f"Error in back_callback: {str(e)}")
            await event.answer("An error occurred while going back to the module list.")

    async def show_command_help(event, command):
        try:
            for module, commands in command_list.items():
                for cmd, desc in commands:
                    if cmd.split()[0] == command:
                        help_text = f"📌 **Perintah:** `{cmd}`\n"
                        help_text += f"📂 **Modul:** {module.capitalize()}\n"
                        help_text += f"📝 **Deskripsi:** {desc}"
                        await event.reply(help_text)
                        return
            await event.reply(f"❌ Perintah '{command}' tidak ditemukan.")
        except Exception as e:
            logger.error(f"Error in show_command_help: {str(e)}")
            await event.reply("An error occurred while displaying command help.")

def add_module_commands(add_command_func):
    module_name = add_command_func.__module__.split('.')[-1]
    add_command_func(lambda cmd, desc: command_list[module_name].append((cmd, desc)))

def add_commands(add_command):
    add_command('.help', '📚 Menampilkan daftar semua perintah')
    add_command('.help <perintah>', '🔍 Menampilkan informasi detail tentang perintah tertentu')