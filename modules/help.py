import re
from telethon import events, Button
from telethon.tl.types import InputPeerSelf
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)
daftar_perintah = defaultdict(list)

def buat_halaman_modul(nomor_halaman, kamus_modul, awalan):
    modul = sorted(list(kamus_modul.keys()))
    item_per_halaman = 8
    indeks_awal = nomor_halaman * item_per_halaman
    indeks_akhir = (nomor_halaman + 1) * item_per_halaman
    modul_halaman = modul[indeks_awal:indeks_akhir]

    tombol = []
    for m in modul_halaman:
        tombol.append([Button.inline(m.capitalize(), f"bantuan_modul({m})")])

    if indeks_awal > 0:
        tombol.append([Button.inline("⬅️ Sebelumnya", f"bantuan_sebelumnya({nomor_halaman - 1})")])
    if indeks_akhir < len(modul):
        tombol.append([Button.inline("Selanjutnya ➡️", f"bantuan_selanjutnya({nomor_halaman + 1})")])

    return tombol

def load(client):
    @client.on(events.NewMessage(pattern=r'\.bantuan(?: (.+))?'))
    async def perintah_bantuan(event):
        argumen = event.pattern_match.group(1)
        if not argumen:
            pesan = f"<b>✣ Menu Bantuan</b>\n\n<b>★ Total modul: {len(daftar_perintah)}</b>"
            tombol = buat_halaman_modul(0, daftar_perintah, "bantuan")
            await event.reply(pesan, buttons=tombol)
        else:
            modul = argumen.lower()
            if modul in daftar_perintah:
                awalan = "."  # Anda mungkin ingin mengimplementasikan cara untuk mendapatkan awalan khusus pengguna
                teks_bantuan = f"Bantuan untuk modul {modul.capitalize()}:\n\n"
                for cmd, deskripsi in daftar_perintah[modul]:
                    teks_bantuan += f"`{awalan}{cmd}`: {deskripsi}\n"
                await event.reply(teks_bantuan)
            else:
                await event.reply(f"Modul '{modul}' tidak ditemukan.")

    @client.on(events.InlineQuery)
    async def menu_inline(event):
        if event.query.user_id == event.client.uid:
            pesan = f"<b>✣ Menu Inline Bantuan</b>\n\n<b>★ Total modul: {len(daftar_perintah)}</b>"
            tombol = buat_halaman_modul(0, daftar_perintah, "bantuan")
            await event.answer([
                event.builder.article(
                    title="Menu Bantuan!",
                    text=pesan,
                    buttons=tombol
                )
            ])

    @client.on(events.CallbackQuery(pattern=r"bantuan_modul\((.+?)\)"))
    async def callback_bantuan_modul(event):
        modul = event.pattern_match.group(1)
        if modul in daftar_perintah:
            awalan = "."  # Anda mungkin ingin mengimplementasikan cara untuk mendapatkan awalan khusus pengguna
            teks_bantuan = f"Bantuan untuk modul {modul.capitalize()}:\n\n"
            for cmd, deskripsi in daftar_perintah[modul]:
                teks_bantuan += f"`{awalan}{cmd}`: {deskripsi}\n"
            await event.edit(teks_bantuan, buttons=[[Button.inline("Kembali", "bantuan_kembali")]])

    @client.on(events.CallbackQuery(pattern=r"bantuan_(sebelumnya|selanjutnya)\((.+?)\)"))
    async def callback_halaman_bantuan(event):
        halaman = int(event.pattern_match.group(2))
        if event.pattern_match.group(1) == "sebelumnya":
            halaman -= 1
        else:
            halaman += 1
        tombol = buat_halaman_modul(halaman, daftar_perintah, "bantuan")
        await event.edit(buttons=tombol)

    @client.on(events.CallbackQuery(pattern="bantuan_kembali"))
    async def callback_bantuan_kembali(event):
        pesan = f"<b>✣ Menu Bantuan</b>\n\n<b>★ Total modul: {len(daftar_perintah)}</b>"
        tombol = buat_halaman_modul(0, daftar_perintah, "bantuan")
        await event.edit(pesan, buttons=tombol)

def tambah_perintah_modul(fungsi_tambah_perintah):
    nama_modul = fungsi_tambah_perintah.__module__.split('.')[-1]
    fungsi_tambah_perintah(lambda cmd, desc: daftar_perintah[nama_modul].append((cmd, desc)))
    logger.info(f"Perintah ditambahkan untuk modul {nama_modul}")

def tambah_perintah(tambah_perintah):
    tambah_perintah('.bantuan', '📚 Menampilkan daftar semua perintah')
    tambah_perintah('.bantuan <modul>', '🔍 Menampilkan bantuan untuk modul tertentu')
    logger.info("Perintah bantuan ditambahkan")