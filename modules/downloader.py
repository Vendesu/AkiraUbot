from telethon import events
import youtube_dl
import asyncio

def load(client):
    @client.on(events.NewMessage(pattern=r'\.yt (.+)'))
    async def youtube_download(event):
        url = event.pattern_match.group(1)
        ydl_opts = {'outtmpl': 'downloads/%(title)s.%(ext)s'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                await event.reply(f"Mulai mengunduh: {info['title']}")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: ydl.download([url]))
                await client.send_file(event.chat_id, filename, caption=info['title'])
                await event.reply("Download selesai!")
            except Exception as e:
                await event.reply(f"Gagal mengunduh: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.ig (.+)'))
    async def instagram_download(event):
        url = event.pattern_match.group(1)
        ydl_opts = {'outtmpl': 'downloads/%(title)s.%(ext)s'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                await event.reply("Mulai mengunduh dari Instagram...")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: ydl.download([url]))
                await client.send_file(event.chat_id, filename)
                await event.reply("Download selesai!")
            except Exception as e:
                await event.reply(f"Gagal mengunduh: {str(e)}")