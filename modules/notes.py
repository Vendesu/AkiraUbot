from telethon import events
import json
import os
import time
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
from .utils import restricted_to_owner

NOTES_FILE = 'notes.json'
COOLDOWN_TIME = 3

def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_notes(notes):
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False)

notes = load_notes()
last_used = {}

def sanitize_unicode(text):
    return ''.join(char for char in text if ord(char) < 0x10000)

def load(client):
    @client.on(events.NewMessage(pattern=r'\.save (.+)'))
    @restricted_to_owner
    async def save_note_handler(event):
        note_name, _, note_content = event.pattern_match.group(1).partition(' ')
        
        if not note_content and not event.media:
            await event.edit('Gagal menyimpan note. Konten atau media tidak boleh kosong.')
            return
        
        note_data = {
            'text': sanitize_unicode(note_content) if note_content else '',
            'media': None
        }
        
        if event.media:
            try:
                if isinstance(event.media, (MessageMediaDocument, MessageMediaPhoto)):
                    media = await event.download_media(bytes)
                    note_data['media'] = media.decode('latin1')
                else:
                    note_data['media'] = 'unsupported_media_type'
            except Exception as e:
                await event.edit(f'Gagal menyimpan media: {str(e)}')
                return
        
        notes[note_name] = note_data
        save_notes(notes)
        
        await event.edit(f'Note "{note_name}" berhasil disimpan dan dapat digunakan di semua chat.')

    @client.on(events.NewMessage(pattern=r'\.note (.+)'))
    async def get_note_handler(event):
        note_name = event.pattern_match.group(1)
        
        current_time = time.time()
        if note_name in last_used:
            if current_time - last_used[note_name] < COOLDOWN_TIME:
                await event.edit(f'Harap tunggu {COOLDOWN_TIME} detik sebelum menggunakan note yang sama.')
                return
        
        last_used[note_name] = current_time
        
        if note_name in notes:
            note_data = notes[note_name]
            text = note_data.get('text', '')
            media = note_data.get('media')
            
            try:
                if media:
                    if media == 'unsupported_media_type':
                        await event.edit(f'Note "{note_name}" berisi tipe media yang tidak didukung.')
                    else:
                        media_bytes = media.encode('latin1')                       
                        await event.delete()                        
                        caption = text if text else f'Note "{note_name}"'
                        await event.respond(caption, file=media_bytes)
                elif text:
                    await event.edit(text)
                else:
                    await event.edit(f'Note "{note_name}" ditemukan, tetapi tidak memiliki konten atau media.')
            except Exception as e:
                await event.edit(f'Terjadi kesalahan saat mengirim note: {str(e)}')
        else:
            await event.edit(f'Note "{note_name}" tidak ditemukan.')

    @client.on(events.NewMessage(pattern=r'\.notes'))
    async def list_notes_handler(event):
        if notes:
            note_list = "\n".join(notes.keys())
            await event.edit(f'Notes yang tersedia:\n{note_list}')
        else:
            await event.edit('Belum ada notes yang disimpan.')

    @client.on(events.NewMessage(pattern=r'\.clear (.+)'))
    @restricted_to_owner
    async def clear_note_handler(event):
        note_name = event.pattern_match.group(1)
        
        if note_name in notes:
            del notes[note_name]
            save_notes(notes)
            await event.edit(f'Note "{note_name}" berhasil dihapus.')
        else:
            await event.edit(f'Note "{note_name}" tidak ditemukan.')

def add_commands(add_command):
    add_command('.save <nama_note> <isi_note>', 'Menyimpan note baru atau memperbarui note yang sudah ada (bisa dengan media)')
    add_command('.note <nama_note>', 'Menampilkan isi note yang telah disimpan')
    add_command('.notes', 'Menampilkan daftar semua notes yang tersedia')
    add_command('.clear <nama_note>', 'Menghapus note tertentu')