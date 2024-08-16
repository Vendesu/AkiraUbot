from telethon import events
import asyncio
import sys
import os
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

def get_version():
    try:
        with open(VERSION_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "1.0.0"

def update_version():
    current_version = get_version()
    version_parts = current_version.split('.')
    version_parts[-1] = str(int(version_parts[-1]) + 1)
    new_version = '.'.join(version_parts)
    with open(VERSION_FILE, 'w') as f:
        f.write(new_version)
    return new_version

def load(client):
    @client.on(events.NewMessage(pattern=r'\.update'))
    @restricted_to_owner
    async def update_bot(event):
        await event.edit("🔄 Memeriksa pembaruan...")
        try:
            repo = Repo(BOT_DIR)
            current_commit = repo.head.commit
            repo.remotes.origin.fetch()
            
            if current_commit == repo.remotes.origin.refs.main.commit:
                current_version = get_version()
                await event.edit(f"✅ Bot sudah dalam versi terbaru ({current_version}).")
                return
            
            await event.edit("🔄 Memperbarui bot...")
            old_commit = current_commit
            repo.git.reset('--hard')
            repo.remotes.origin.pull()
            new_commit = repo.head.commit
            
            await event.edit("🔄 Menginstal dependensi...")
            os.system('pip install -r requirements.txt')
            
            new_version = update_version()
            
            changelog = await get_changelog(repo, old_commit, new_commit)
            
            update_message = f"✅ Bot berhasil diperbarui ke versi {new_version}!\n\n"
            update_message += changelog
            update_message += "\nBot akan direstart dalam 10 detik..."
            
            await event.edit(update_message)
            
            await asyncio.sleep(10)
            
            await client.disconnect()
            
            subprocess.Popen(["python3", os.path.join(BOT_DIR, "main.py")])
            
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
            
            commits = list(repo.iter_commits(f'{current_commit}..origin/main'))
            
            if not commits:
                await event.edit("✅ Bot sudah dalam versi terbaru.")
                return
            
            changelog = "📋 **Changelog:**\n\n"
            for commit in reversed(commits):
                changelog += f"• {commit.summary}\n"
            
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
                await event.edit(f"🆕 Pembaruan tersedia!\n"
                                 f"Versi saat ini: {current_version}\n"
                                 f"Bot Anda tertinggal {commits_behind} commit.\n"
                                 f"Gunakan `.update` untuk memperbarui bot.")
        except Exception as e:
            await event.edit(f"❌ Terjadi kesalahan saat memeriksa pembaruan: {str(e)}")

async def get_changelog(repo, old_commit, new_commit):
    changelog = "📋 **Changelog:**\n\n"
    for commit in repo.iter_commits(f'{old_commit}..{new_commit}'):
        changelog += f"• {commit.summary}\n"
    return changelog

def add_commands(add_command):
    add_command('.update', '🔄 Memperbarui bot ke versi terbaru dari GitHub')
    add_command('.version', '🔢 Menampilkan versi bot saat ini')
    add_command('.changelog', '📋 Menampilkan daftar perubahan terbaru')
    add_command('.checkupdate', '🔍 Memeriksa ketersediaan pembaruan tanpa menginstalnya')