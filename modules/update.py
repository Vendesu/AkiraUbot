from telethon import events
import asyncio
import sys
import os
import aiohttp
from git import Repo
from git.exc import GitCommandError
from .utils import restricted_to_owner

REPO_URL = "https://github.com/Vendesu/AkiraUbot.git"

BOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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
                await event.edit("✅ Bot sudah dalam versi terbaru.")
                return
                        
            await event.edit("🔄 Memperbarui bot...")
            repo.git.reset('--hard')
            repo.remotes.origin.pull()
            
            await event.edit("🔄 Menginstal dependensi...")
            os.system('pip install -r requirements.txt')
            
            await event.edit("✅ Bot berhasil diperbarui! Merestart...")
            
            await client.disconnect()
            os.execl(sys.executable, sys.executable, *sys.argv)
        
        except GitCommandError as e:
            await event.edit(f"❌ Terjadi kesalahan saat memperbarui: {str(e)}")
        except Exception as e:
            await event.edit(f"❌ Terjadi kesalahan yang tidak diketahui: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.changelog'))
    @restricted_to_owner
    async def get_changelog(event):
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
                await event.edit("✅ Bot sudah dalam versi terbaru.")
            else:
                commits_behind = len(list(repo.iter_commits(f'{current_commit}..origin/main')))
                await event.edit(f"🆕 Pembaruan tersedia!\n"
                                 f"Bot Anda tertinggal {commits_behind} commit.\n"
                                 f"Gunakan `.update` untuk memperbarui bot.")
        except Exception as e:
            await event.edit(f"❌ Terjadi kesalahan saat memeriksa pembaruan: {str(e)}")

def add_commands(add_command):
    add_command('.update', '🔄 Memperbarui bot ke versi terbaru dari GitHub')
    add_command('.changelog', '📋 Menampilkan daftar perubahan terbaru')
    add_command('.checkupdate', '🔍 Memeriksa ketersediaan pembaruan tanpa menginstalnya')