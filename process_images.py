import os
import requests
import csv
from PIL import Image
from io import BytesIO
import pillow_heif

# Регистрируем плагин HEIF в Pillow
pillow_heif.register_heif_opener()

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR3OtmgAYtqeTFqohCHU_jtr-4ml_YJvWTyElPtgjMVERcE2K9freCbwEslfQcgzEYA4g7UgR13OAZW/pub?gid=0&single=true&output=csv"
THUMBS_DIR = 'assets/img/thumbs'
FULL_DIR = 'assets/img/full'

# Заголовки, чтобы Google Drive не блокировал запросы
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def get_drive_id(url):
    if not url: return None
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    elif 'id=' in url:
        return url.split('id=')[1].split('&')[0]
    return None

def process():
    os.makedirs(THUMBS_DIR, exist_ok=True)
    os.makedirs(FULL_DIR, exist_ok=True)

    try:
        response = requests.get(SHEET_CSV_URL, headers=HEADERS)
        response.encoding = 'utf-8'
        reader = csv.DictReader(response.text.splitlines())
    except Exception as e:
        print(f"Не удалось получить таблицу: {e}")
        return

    for row in reader:
        img_url = row.get('img', '')
        img_id = get_drive_id(img_url)
        
        if not img_id:
            continue

        full_path = f"{FULL_DIR}/{img_id}.webp"
        thumb_path = f"{THUMBS_DIR}/{img_id}.webp"

        # Если файл уже есть, пропускаем
        if os.path.exists(full_path) and os.path.exists(thumb_path):
            continue

        print(f"Загрузка и оптимизация нового изображения: {img_id}")
        download_url = f'https://drive.google.com/uc?export=download&id={img_id}'
        
        try:
            res = requests.get(download_url, headers=HEADERS, timeout=30)
            if res.status_code == 200:
                img = Image.open(BytesIO(res.content))
                
                # Обработка прозрачности (заменяем на белый фон)
                if img.mode in ("RGBA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.convert("RGBA").split()[3])
                    img = background
                else:
                    img = img.convert("RGB")
                
                # Full size (1600px)
                full_img = img.copy()
                full_img.thumbnail((1600, 1600))
                full_img.save(full_path, 'WEBP', quality=80)

                # Thumbnail (600px)
                thumb_img = img.copy()
                thumb_img.thumbnail((600, 600))
                thumb_img.save(thumb_path, 'WEBP', quality=75)
            else:
                print(f"Ошибка загрузки {img_id}: Status {res.status_code}")
        except Exception as e:
            print(f"Ошибка при обработке картинки с ID {img_id}: {e}")

if __name__ == "__main__":
    process()
