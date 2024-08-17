from telethon import events, Button
from collections import defaultdict
import math

HELP_COMMANDS = {}

def paginate_commands(page_n, cmd_dict, prefix):
    commands = sorted(list(cmd_dict.keys()))
    items_per_page = 8
    start_index = page_n * items_per_page
    end_index = (page_n + 1) * items_per_page
    page_commands = commands[start_index:end_index]

    buttons = []
    for cmd in page_commands:
        buttons.append([Button.inline(cmd, f"help_cmd({cmd})")])

    if start_index > 0:
        buttons.append([Button.inline("⬅️ Sebelumnya", f"help_prev({page_n - 1})")])
    if end_index < len(commands):
        buttons.append([Button.inline("Selanjutnya ➡️", f"help_next({page_n + 1})")])

    return buttons

def load(client):
    @client.on(events.NewMessage(pattern=r'\.help(?: (.+))?'))
    async def help_cmd(event):
        if not event.pattern_match.group(1):
            message = f"<b>✣ Daftar Perintah AkiraUBot:</b>\n\n"
            message += f"<b>• Jumlah Perintah: {len(HELP_COMMANDS)}</b>\n\n"
            message += "Pilih perintah di bawah ini untuk melihat detailnya:"
            buttons = paginate_commands(0, HELP_COMMANDS, "help")
            await event.reply(message, buttons=buttons)
        else:
            cmd = event.pattern_match.group(1).lower()
            if cmd in HELP_COMMANDS:
                await event.reply(f"<b>Perintah:</b> {cmd}\n<b>Deskripsi:</b> {HELP_COMMANDS[cmd]}")
            else:
                await event.reply(f"Perintah '{cmd}' tidak ditemukan.")

    @client.on(events.CallbackQuery(pattern=r"help_cmd\((.+?)\)"))
    async def help_command(event):
        cmd = event.data_match.group(1).decode("utf-8")
        if cmd in HELP_COMMANDS:
            text = f"<b>Perintah:</b> {cmd}\n<b>Deskripsi:</b> {HELP_COMMANDS[cmd]}"
            await event.edit(text, buttons=[[Button.inline("🔙 Kembali", "help_back")]])
        else:
            await event.answer(f"Perintah '{cmd}' tidak ditemukan.", alert=True)

    @client.on(events.CallbackQuery(pattern=r"help_(prev|next)\((\d+)\)"))
    async def help_pagination(event):
        direction = event.data_match.group(1).decode("utf-8")
        page = int(event.data_match.group(2))
        page = page - 1 if direction == "prev" else page + 1
        buttons = paginate_commands(page, HELP_COMMANDS, "help")
        await event.edit(buttons=buttons)

    @client.on(events.CallbackQuery(pattern=r"help_back"))
    async def help_back(event):
        message = f"<b>✣ Daftar Perintah AkiraUBot:</b>\n\n"
        message += f"<b>• Jumlah Perintah: {len(HELP_COMMANDS)}</b>\n\n"
        message += "Pilih perintah di bawah ini untuk melihat detailnya:"
        buttons = paginate_commands(0, HELP_COMMANDS, "help")
        await event.edit(message, buttons=buttons)

def add_command(cmd, description):
    HELP_COMMANDS[cmd] = description

def add_module_help(module):
    # Fungsi ini tidak lagi diperlukan, tapi kita biarkan untuk kompatibilitas
    pass

def add_commands(add_command):
    add_command('.help', 'Menampilkan daftar semua perintah')
    add_command('.help <nama_perintah>', 'Menampilkan detail untuk perintah tertentu')