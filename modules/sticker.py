from telethon import events
import io
import math
import urllib.request
from PIL import Image, ImageDraw, ImageFont
from telethon.tl.types import DocumentAttributeFilename

def load(client):
    @client.on(events.NewMessage(pattern=r'\.sticker'))
    async def sticker_to_png(event):
        if event.is_reply:
            reply_message = await event.get_reply_message()
            if reply_message.sticker:
                if reply_message.sticker.mime_type == "application/x-tgsticker":
                    await event.reply("❌ Maaf, stiker animasi belum didukung.")
                    return
                sticker_image = io.BytesIO()
                await client.download_media(reply_message.sticker, sticker_image)
                sticker_image.seek(0)
                img = Image.open(sticker_image)
                png_image = io.BytesIO()
                img.save(png_image, "PNG")
                png_image.name = "sticker.png"
                png_image.seek(0)
                await client.send_file(event.chat_id, png_image, force_document=True, reply_to=reply_message.id)
            else:
                await event.reply("🔔 Mohon balas ke sebuah stiker.")
        else:
            await event.reply("🔔 Mohon balas ke sebuah stiker.")

    @client.on(events.NewMessage(pattern=r'\.stkr'))
    async def image_to_sticker(event):
        if event.is_reply:
            reply_message = await event.get_reply_message()
            if reply_message.photo or reply_message.document:
                image = io.BytesIO()
                await client.download_media(reply_message, image)
                image.seek(0)
                img = Image.open(image)
                img = resize_image(img)
                sticker_image = io.BytesIO()
                img.save(sticker_image, "WebP", quality=95)
                sticker_image.name = "sticker.webp"
                sticker_image.seek(0)
                await client.send_file(event.chat_id, sticker_image, force_document=False, reply_to=reply_message.id)
            else:
                await event.reply("🔔 Mohon balas ke sebuah gambar.")
        else:
            await event.reply("🔔 Mohon balas ke sebuah gambar.")

    @client.on(events.NewMessage(pattern=r'\.stkrurl (.+)'))
    async def url_to_sticker(event):
        url = event.pattern_match.group(1)
        try:
            response = urllib.request.urlopen(url)
            image = io.BytesIO(response.read())
            img = Image.open(image)
            img = resize_image(img)
            sticker_image = io.BytesIO()
            img.save(sticker_image, "WebP", quality=95)
            sticker_image.name = "sticker.webp"
            sticker_image.seek(0)
            await client.send_file(event.chat_id, sticker_image, force_document=False)
        except Exception as e:
            await event.reply(f"❌ Terjadi kesalahan: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.stkrtext (.+)'))
    async def text_to_sticker(event):
        text = event.pattern_match.group(1)
        image = create_text_image(text)
        sticker_image = io.BytesIO()
        image.save(sticker_image, "WebP", quality=95)
        sticker_image.name = "sticker.webp"
        sticker_image.seek(0)
        await client.send_file(event.chat_id, sticker_image, force_document=False)

def resize_image(img):
    maxsize = (512, 512)
    if (img.width and img.height) < 512:
        size1 = img.width
        size2 = img.height
        if img.width > img.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        img = img.resize(sizenew)
    else:
        img.thumbnail(maxsize)
    return img

def create_text_image(text):
    img = Image.new('RGB', (512, 512), color='white')
    d = ImageDraw.Draw(img)
    
    try:
        # Coba gunakan font default
        fnt = ImageFont.load_default()
    except:
        try:
            # Jika gagal, coba gunakan font DejaVu Sans
            fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            # Jika masih gagal, gunakan font built-in PIL
            fnt = ImageFont.load_default()
    
    # Fungsi untuk menghitung ukuran teks
    def get_text_dimensions(text, font):
        bbox = d.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # Hitung ukuran teks
    w, h = get_text_dimensions(text, fnt)
    
    # Jika teks terlalu panjang, kurangi ukuran font
    while w > 500 or h > 500:
        if hasattr(fnt, 'path'):
            fnt = ImageFont.truetype(fnt.path, fnt.size - 1)
        else:
            # Jika font tidak memiliki path, gunakan font default dengan ukuran yang lebih kecil
            fnt = ImageFont.load_default()
        w, h = get_text_dimensions(text, fnt)
    
    # Hitung posisi untuk menempatkan teks di tengah
    x = (512 - w) / 2
    y = (512 - h) / 2
    
    d.text((x, y), text, font=fnt, fill='black')
    return img

def add_commands(add_command):
    add_command('.sticker', '🖼️ Mengonversi stiker menjadi gambar PNG')
    add_command('.stkr', '🔄 Mengonversi gambar menjadi stiker')
    add_command('.stkrurl <url>', '🌐 Membuat stiker dari URL gambar')
    add_command('.stkrtext <teks>', '✍️ Membuat stiker dari teks')