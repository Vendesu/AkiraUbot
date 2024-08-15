from telethon import events, types
import time
import random
from .utils import restricted_to_owner

afk_status = {}

is_afk = False

afk_responses = [
    "Halo! {name} lagi AFK nih. {reason}",
    "Yah, {name} lagi nggak ada. {reason}",
    "Sst, {name} lagi sibuk. {reason}",
    "Waduh, {name} lagi off dulu. {reason}",
    "Sorry ya, {name} lagi AFK. {reason}"
]

default_reasons = [
    "Mungkin lagi bobo cantik kali ya?",
    "Kayaknya sih lagi nonton Netflix.",
    "Bisa jadi lagi makan deh.",
    "Mungkin lagi main game kali ya?",
    "Sepertinya lagi asik sendiri nih."
]

def format_time(seconds):
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours} jam {minutes} menit"
    elif minutes > 0:
        return f"{minutes} menit"
    else:
        return f"{seconds} detik"

def load(client):
    @client.on(events.NewMessage(pattern=r'(?i)^\.afk(?: (.*))?'))
    @restricted_to_owner
    async def afk_handler(event):
        global is_afk
        reason = event.pattern_match.group(1)
        user = await event.get_sender()
        user_id = user.id
        first_name = user.first_name if user.first_name else "Kamu"
        
        afk_status[user_id] = {
            'time': time.time(),
            'reason': reason if reason else random.choice(default_reasons),
            'name': first_name
        }
        is_afk = True
        
        if reason:
            await event.edit(f"Oke deh, {first_name} AFK ya. Kalo ada yang nyariin, aku bilang: {reason}")
        else:
            await event.edit(f"Siap, {first_name} AFK mode: ON! 😎")

    @client.on(events.NewMessage)
    async def afk_responder(event):
        if event.is_private:
            sender = await event.get_sender()
            if sender and sender.id in afk_status:
                await respond_to_afk(event, sender.id)
        else:
            mentioned_ids = await get_mentioned_ids(event)
            for user_id in mentioned_ids:
                if user_id in afk_status:
                    await respond_to_afk(event, user_id)

    async def get_mentioned_ids(event):
        mentioned_ids = set()
        if event.message.entities:
            for entity in event.message.entities:
                if isinstance(entity, types.MessageEntityMentionName):
                    mentioned_ids.add(entity.user_id)
                elif isinstance(entity, types.MessageEntityMention):
                    try:
                        text = event.message.text[entity.offset:entity.offset+entity.length]
                        user = await event.client.get_entity(text)
                        if isinstance(user, types.User):
                            mentioned_ids.add(user.id)
                    except:
                        pass
        return mentioned_ids

    async def respond_to_afk(event, user_id):
        afk_time = time.time() - afk_status[user_id]['time']
        time_str = format_time(afk_time)
        reason = afk_status[user_id]['reason']
        name = afk_status[user_id]['name']
        
        response = random.choice(afk_responses)
        response = response.format(name=name, reason=reason)
        response += f"\nUdah AFK {time_str} nih."
        
        await event.edit(response)

    @client.on(events.NewMessage(pattern=r'(?i)^\.noafk'))
    @restricted_to_owner
    async def noafk_handler(event):
        global is_afk
        user = await event.get_sender()
        user_id = user.id
        
        if user_id in afk_status:
            afk_time = time.time() - afk_status[user_id]['time']
            time_str = format_time(afk_time)
            name = afk_status[user_id]['name']
            del afk_status[user_id]
            is_afk = False
            
            messages = [
                f"Halo semuanya! {name} balik lagi nih setelah AFK {time_str}! 🎉",
                f"Guess who's back? {name} udah nggak AFK lagi setelah {time_str}! 😄",
                f"Yuhuu, {name} udah online lagi nih. AFK {time_str} terasa cepet ya!",
                f"Selamat datang kembali, {name}! Abis AFK {time_str}, pasti kangen sama chat ya? 😉"
            ]
            
            await event.edit(random.choice(messages))
        else:
            await event.edit("Loh, kamu kan nggak lagi AFK. Mau AFK? Ketik .afk aja! 😊")

def add_commands(add_command):
    add_command('.afk [alasan]', 'Ngasih tau yang lain kalo kamu lagi AFK')
    add_command('.noafk', 'Nonaktifin mode AFK, biar yang lain tau kamu udah balik')

def check_afk_status():
    return is_afk