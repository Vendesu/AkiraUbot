from telethon import events
import asyncio
import sys
import os
import aiohttp
from git import Repo
from git.exc import GitCommandError
from .utils import restricted_to_owner
import subprocess

# URL repositori GitHub AkiraUBot
REPO_URL = "https://github.com/Vendesu/AkiraUBot.git"
# Direktori tempat bot diinstal
BOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# File untuk menyimpan versi
VERSION_FILE = os.path.join(BOT_DIR, "version.txt")
# File requirements
REQUIREMENTS_FILE = os.path.join(BOT_DIR, "requirements.txt")

def get_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    return "1.0.0"

def update_version():
    current_version = get_version()
    version_parts = current_version.split('.')
    version_parts[-1] = str(int(version_parts[-1]) + 1)
    new_version = '.'.join(version_parts)
    with open(VERSION_FILE, "w") as f:
        f.write(new_version)
    return new_version

async def get_changelog(repo, old_commit, new_commit):
    changelog = "📋 **Changelog:**\n\n"
    for commit in repo.iter_commits(f'{old_commit}..{new_commit}'):
        changelog += f"• {commit.summary}\n"
    return changelog

def install_dependencies():
    if os.path.exists(REQUIREMENTS_FILE):
        return os.system(f'pip install -r {REQUIREMENTS_FILE}')
    else:
        return os.system('pip install telethon googletrans==3.1.0a0 pydub moviepy SpeechRecognition youtube_dl aiohttp beautifulsoup4 psutil GitPython Pillow emoji python-dotenv speedtest-cli')

def load(client):
    @client.on(events.NewMessage(pattern=r'\.update'))
    @restricted_to_owner
    async def update_bot(event):
        await event.edit("🔄 Memeriksa pembaruan...")
        try:
            repo = Repo(BOT_DIR)
            current_commit = repo.head.commit
            repo.remotes.origin.fetch()
            
            # Cek apakah ada pembaruan
            if current_commit == repo.remotes.origin.refs.main.commit:
                await event.edit("✅ Bot sudah dalam versi terbaru.")
                return
            
            # Ada pembaruan, lakukan pull
            await event.edit("🔄 Memperbarui bot...")
            old_commit = current_commit
            repo.git.reset('--hard')
            repo.remotes.origin.pull()
            new_commit = repo.head.commit
            
            # Instal dependensi baru jika ada
            await event.edit("🔄 Menginstal dependensi...")
            install_result = install_dependencies()
            if install_result != 0:
                await event.edit("❌ Terjadi kesalahan saat menginstal dependensi.")
                return
            
            # Update versi
            new_version = update_version()
            
            # Dapatkan changelog
            changelog = await get_changelog(repo, old_commit, new_commit)
            
            # Tampilkan changelog dan informasi pembaruan
            update_message = f"✅ Bot berhasil diperbarui ke versi {new_version}!\n\n"
            update_message += changelog
            update_message += "\nBot akan direstart dalam 10 detik..."
            
            await event.edit(update_message)
            
            # Tunggu 10 detik agar pengguna dapat membaca changelog
            await asyncio.sleep(10)
            
            # Disconnect client
            await client.disconnect()
            
            # Jalankan main.py dalam proses baru
            subprocess.Popen(["python3", os.path.join(BOT_DIR, "main.py")])
            
            # Keluar dari proses saat ini
            os._exit(0)
        
        except GitCommandError as e:
            await event.edit(f"❌ Terjadi kesalahan saat memperbarui: {str(e)}")
        except Exception as e:
            await event.edit(f"❌ Terjadi kesalahan yang tidak diketahui: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.version'))
    @restricted_to_owner
    async def get_bot_version(event):
        version = get_version()
        await event.reply(f"🤖 Versi AkiraUBot saat ini: {version}")

    @client.on(events.NewMessage(pattern=r'\.changelog'))
    @restricted_to_owner
    async def get_changelog_command(event):
        await event.edit("🔍 Mengambil changelog...")
        try:
            repo = Repo(BOT_DIR)
            current_commit = repo.head.commit
            repo.remotes.origin.fetch()
            
            # Ambil commit antara versi saat ini dan versi terbaru
            changelog = await get_changelog(repo, current_commit, 'origin/main')
            
            if changelog == "📋 **Changelog:**\n\n":
                await event.edit("✅ Bot sudah dalam versi terbaru.")
            else:
                await event.edit(changelog)
        except Exception as e:
            await event.edit(f"❌ Terjadi kesalahan saat mengambil changelog: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.checkupdate'))
    @restricted_to_owner
    async def check_update(event):
        await event.edit("🔍 Memeriksa pembaruan...")
        try:
            repo = Repo(BOT_DIR)
            current_commit = repo.head.commit
            repo.remotes.origin.fetch()
            
            if current_commit == repo.remotes.origin.refs.main.commit:
                current_version = get_version()
                await event.edit(f"✅ Bot sudah dalam versi terbaru ({current_version}).")
            else:
                commits_behind = len(list(repo.iter_commits(f'{current_commit}..origin/main')))
                current_version = get_version()
                changelog = await get_changelog(repo, current_commit, 'origin/main')
                update_message = f"🆕 Pembaruan tersedia!\n"
                update_message += f"Versi saat ini: {current_version}\n"
                update_message += f"Bot Anda tertinggal {commits_behind} commit.\n\n"
                update_message += changelog
                update_message += "\nGunakan `.update` untuk memperbarui bot."
                await event.edit(update_message)
        except Exception as e:
            await event.edit(f"❌ Terjadi kesalahan saat memeriksa pembaruan: {str(e)}")

def add_commands(add_command):
    add_command('.update', '🔄 Memperbarui bot ke versi terbaru dari GitHub')
    add_command('.version', '🔢 Menampilkan versi bot saat ini')
    add_command('.changelog', '📋 Menampilkan daftar perubahan terbaru')
    add_command('.checkupdate', '🔍 Memeriksa ketersediaan pembaruan tanpa menginstalnya')