#!/bin/bash

# Warna-warna untuk output
MERAH='\033[0;31m'
HIJAU='\033[0;32m'
KUNING='\033[1;33m'
BIRU='\033[0;34m'
UNGU='\033[0;35m'
CYAN='\033[0;36m'
PUTIH='\033[1;37m'
NORMAL='\033[0m'

# Fungsi untuk menampilkan pesan dengan warna
pesan() {
    echo -e "${2}${1}${NORMAL}"
}

# Fungsi untuk menampilkan banner
tampilkan_banner() {
    clear
    echo -e "${CYAN}"
    echo "    _    _    _           _    _ ____        _   "
    echo "   / \  | | _(_)_ __ __ _| |  | | __ )  ___ | |_ "
    echo "  / _ \ | |/ / | '__/ _\` | |  | |  _ \ / _ \| __|"
    echo " / ___ \|   <| | | | (_| | |__| | |_) | (_) | |_ "
    echo "/_/   \_\_|\_\_|_|  \__,_|____/|____/ \___/ \__|"
    echo ""
    echo -e "${PUTIH}========== Instalasi Otomatis AkiraUBot ==========${NORMAL}"
    echo ""
}

# Fungsi untuk menginstal paket jika belum ada
instal_jika_belum_ada() {
    if ! command -v $1 &> /dev/null
    then
        pesan "Menginstal $1..." "${KUNING}"
        sudo apt-get update
        sudo apt-get install -y $1
        pesan "$1 berhasil diinstal." "${HIJAU}"
    else
        pesan "$1 sudah terinstal." "${HIJAU}"
    fi
}

# Fungsi utama
main() {
    tampilkan_banner

    # Instal paket yang diperlukan
    pesan "Memeriksa dan menginstal paket yang diperlukan..." "${BIRU}"
    instal_jika_belum_ada screen
    instal_jika_belum_ada git
    instal_jika_belum_ada python3
    instal_jika_belum_ada python3-pip

    # Klon repositori
    pesan "Mengunduh repositori AkiraUBot..." "${BIRU}"
    git clone https://github.com/Vendesu/AkiraUbot.git
    cd AkiraUbot

    # Buat sesi screen baru dan jalankan setup di dalamnya
    pesan "Memulai instalasi AkiraUBot dalam sesi screen..." "${UNGU}"
    screen -dmS AkiraUBot bash -c '
        echo -e "\033[0;36mMenginstal dependensi Python...\033[0m"
        pip3 install telethon googletrans==3.1.0a0 pydub moviepy SpeechRecognition youtube_dl aiohttp beautifulsoup4 psutil GitPython Pillow emoji
        echo -e "\033[0;32mInstalasi dependensi selesai.\033[0m"
        echo -e "\033[0;35mMemulai AkiraUBot...\033[0m"
        python3 main.py
        exec bash
    '

    # Tempel ke sesi screen
    pesan "Menghubungkan ke sesi AkiraUBot..." "${PUTIH}"
    sleep 2
    screen -r AkiraUBot
}

# Jalankan fungsi utama
main

pesan "Instalasi dan pengaturan selesai!" "${HIJAU}"
pesan "Anda sekarang berada dalam sesi screen AkiraUBot." "${PUTIH}"
pesan "Untuk keluar dari sesi screen, tekan Ctrl+A lalu D" "${KUNING}"