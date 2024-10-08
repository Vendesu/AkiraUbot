from telethon import events, types
import time
import random
from .utils import restricted_to_authorized
import json
import os

AFK_FILE = 'afk_status_{}.json'

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

def load_afk_status(user_id):
    file_name = AFK_FILE.format(user_id)
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return json.load(f)
    return None

def save_afk_status(user_id, status):
    file_name = AFK_FILE.format(user_id)
    with open(file_name, 'w') as f:
        json.dump(status, f)

def check_afk_status(user_id):
    status = load_afk_status(user_id)
    if status:
        return True, status
    return False, None

def load(client):
    @client.on(events.NewMessage(pattern=r'(?i)^\.afk(?: (.*))?'))
    @restricted_to_authorized
    async def afk_handler(event):
        reason = event.pattern_match.group(1)
        user = await event.get_sender()
        user_id = user.id
        first_name = user.first_name if user.first_name else "Kamu"
        
        afk_status = {
            'time': time.time(),
            'reason': reason if reason else random.choice(default_reasons),
            'name': first_name
        }
        save_afk_status(user_id, afk_status)
        
        if reason:
            await event.edit(f"Oke deh, {first_name} AFK ya. Kalo ada yang nyariin, aku bilang: {reason}")
        else:
            await event.edit(f"Siap, {first_name} AFK mode: ON! 😎")

    @client.on(events.NewMessage)
    async def afk_responder(event):
        if event.is_private:
            sender = await event.get_sender()
            if sender:
                is_afk, afk_status = check_afk_status(sender.id)
                if is_afk:
                    await respond_to_afk(event, sender.id, afk_status)
        else:
            if event.mentioned:
                for user_id in event.get_mentioned_user_ids():
                    is_afk, afk_status = check_afk_status(user_id)
                    if is_afk:
                        await respond_to_afk(event, user_id, afk_status)

    async def respond_to_afk(event, user_id, afk_status):
        afk_time = time.time() - afk_status['time']
        time_str = format_time(afk_time)
        reason = afk_status['reason']
        name = afk_status['name']
        
        response = random.choice(afk_responses)
        response = response.format(name=name, reason=reason)
        response += f"\nUdah AFK {time_str} nih."
        
        await event.reply(response)

    @client.on(events.NewMessage(pattern=r'(?i)^\.noafk'))
    @restricted_to_authorized
    async def noafk_handler(event):
        user = await event.get_sender()
        user_id = user.id
        
        afk_status = load_afk_status(user_id)
        if afk_status:
            afk_time = time.time() - afk_status['time']
            time_str = format_time(afk_time)
            name = afk_status['name']
            os.remove(AFK_FILE.format(user_id))
            
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
