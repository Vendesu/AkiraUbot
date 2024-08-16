from . import (
    basic,
    utils,
    notes,
    admin,
    afk,
    translate,
    sticker,
    downloader,
    spam,
    info,
    speedtest,
    text,
    help,
    autotag,
    ping,
    status,
    wellcome,
    update,
    statistik,
    duck,
    invgrup,
    asupan# Tambahkan modul invgrup di sini
)

def load_modules(client):
    modules_list = [
        basic, utils, notes, admin, afk, translate, sticker, downloader, spam,
        info, speedtest, text, autotag, ping, status, wellcome, update,
        statistik, duck, invgrup, asupan  # Tambahkan invgrup di sini juga
    ]
    
    for module in modules_list:
        module.load(client)
        if hasattr(module, 'add_commands'):
            help.add_module_commands(module.add_commands)
    
    # Load help module last
    help.load(client)

    print("Semua modul berhasil dimuat.")