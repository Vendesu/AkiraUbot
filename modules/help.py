from telethon import events, Button
from collections import defaultdict
import math

HELP_COMMANDS = {}

def paginate_modules(page_n, module_dict, prefix):
    modules = sorted(list(module_dict.keys()))
    items_per_page = 8
    start_index = page_n * items_per_page
    end_index = (page_n + 1) * items_per_page
    page_modules = modules[start_index:end_index]

    buttons = []
    for module in page_modules:
        buttons.append([Button.inline(module.capitalize(), f"help_module({module})")])

    if start_index > 0:
        buttons.append([Button.inline("⬅️ Sebelumnya", f"help_prev({page_n - 1})")])
    if end_index < len(modules):
        buttons.append([Button.inline("Selanjutnya ➡️", f"help_next({page_n + 1})")])

    return buttons

def load(client):
    @client.on(events.NewMessage(pattern=r'\.help(?: (.+))?'))
    async def help_cmd(event):
        if not event.pattern_match.group(1):
            message = f"<b>✣ Daftar Modul AkiraUBot:</b>\n\n"
            message += f"<b>• Jumlah Modul: {len(HELP_COMMANDS)}</b>\n\n"
            message += "Pilih modul di bawah ini untuk melihat perintah yang tersedia:"
            buttons = paginate_modules(0, HELP_COMMANDS, "help")
            await event.reply(message, buttons=buttons)
        else:
            module = event.pattern_match.group(1).lower()
            if module in HELP_COMMANDS:
                await event.reply(HELP_COMMANDS[module].__doc__)
            else:
                await event.reply(f"Modul '{module}' tidak ditemukan.")

    @client.on(events.CallbackQuery(pattern=r"help_module\((.+?)\)"))
    async def help_module(event):
        modul = event.data_match.group(1).decode("utf-8")
        if modul in HELP_COMMANDS:
            text = f"<b>Perintah untuk modul {modul.capitalize()}:</b>\n\n"
            text += HELP_COMMANDS[modul].__doc__ or "Tidak ada dokumentasi untuk modul ini."
            await event.edit(text, buttons=[[Button.inline("🔙 Kembali", "help_back")]])
        else:
            await event.answer(f"Modul '{modul}' tidak ditemukan.", alert=True)

    @client.on(events.CallbackQuery(pattern=r"help_(prev|next)\((\d+)\)"))
    async def help_pagination(event):
        direction = event.data_match.group(1).decode("utf-8")
        page = int(event.data_match.group(2))
        page = page - 1 if direction == "prev" else page + 1
        buttons = paginate_modules(page, HELP_COMMANDS, "help")
        await event.edit(buttons=buttons)

    @client.on(events.CallbackQuery(pattern=r"help_back"))
    async def help_back(event):
        message = f"<b>✣ Daftar Modul AkiraUBot:</b>\n\n"
        message += f"<b>• Jumlah Modul: {len(HELP_COMMANDS)}</b>\n\n"
        message += "Pilih modul di bawah ini untuk melihat perintah yang tersedia:"
        buttons = paginate_modules(0, HELP_COMMANDS, "help")
        await event.edit(message, buttons=buttons)

def add_module_commands(module):
    HELP_COMMANDS[module.__name__.split('.')[-1]] = module

def add_command(cmd, description):
    module = cmd.module
    if not hasattr(module, '__doc__'):
        module.__doc__ = ''
    module.__doc__ += f"\n• <code>{cmd}</code>: {description}"

def add_commands(add_command):
    add_command('.help', 'Menampilkan daftar semua perintah')
    add_command('.help <nama_modul>', 'Menampilkan perintah untuk modul tertentu')