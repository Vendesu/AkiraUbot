from telethon import events

def load(client):
    @client.on(events.NewMessage(pattern=r'\.start'))
    async def start_handler(event):
        await event.reply('Halo! Userbot telah aktif.')

    @client.on(events.NewMessage(pattern=r'\.echo (.+)'))
    async def echo_handler(event):
        message = event.pattern_match.group(1)
        await event.reply(f'Anda mengatakan: {message}')