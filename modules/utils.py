from telethon import events
from functools import wraps
import time
import math

owner_id = None

def set_owner_id(id):
    global owner_id
    owner_id = id

def restricted_to_owner(func):
    @wraps(func)
    async def wrapper(event):
        global owner_id
        if owner_id is None:
            me = await event.client.get_me()
            owner_id = me.id
        
        sender = await event.get_sender()
        if sender.id == owner_id:
            return await func(event)
        else:            
            return
    return wrapper

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["d", "h", "m", "s"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += time_list.pop() + ", "

    time_list.reverse()
    up_time += ":".join(time_list)

    return up_time

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"

def time_formatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + " day(s), ") if days else "") + \
        ((str(hours) + " hour(s), ") if hours else "") + \
        ((str(minutes) + " minute(s), ") if minutes else "") + \
        ((str(seconds) + " second(s), ") if seconds else "") + \
        ((str(milliseconds) + " millisecond(s), ") if milliseconds else "")
    return tmp[:-2]

def percentage(part, whole):
    return 100 * float(part)/float(whole)

def progress(current, total, message, start_time, client, chat_id, message_id):
    now = time.time()
    diff = now - start_time
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        progress_str = "[{0}{1}] {2}%\n".format(
            ''.join(["▰" for _ in range(math.floor(percentage / 10))]),
            ''.join(["▱" for _ in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2))

        tmp = progress_str + \
              "Progress: {0} of {1}\n" \
              "Speed: {2}/s\n" \
              "ETA: {3}\n".format(
                  humanbytes(current),
                  humanbytes(total),
                  humanbytes(speed),
                  time_formatter(estimated_total_time)
              )
        client.edit_message(chat_id, message_id, tmp + message)

def load(client):    
    pass

def add_commands(add_command):
    pass