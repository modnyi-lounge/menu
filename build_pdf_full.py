import requests
import csv
import os
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from time import time

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR3OtmgAYtqeTFqohCHU_jtr-4ml_YJvWTyElPtgjMVERcE2K9freCbwEslfQcgzEYA4g7UgR13OAZW/pub?gid=0&single=true&output=csv"
THUMBS_DIR = 'assets/img/thumbs' 

def get_drive_id(url):
    if not url: return None
    return url.split('/d/')[1].split('/')[0] if '/d/' in url else (url.split('id=')[1].split('&')[0] if 'id=' in url else None)

def build_pdf():
    try:
        response = requests.get(SHEET_CSV_URL, timeout=30)
        response.encoding = 'utf-8'
        items = list(csv.DictReader(response.text.splitlines()))
    except Exception as e:
        print(f"Error fetching data: {e}"); return

    # Конфигурация для правильной обработки шрифтов (Inter)
    font_config = FontConfiguration()

    style = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    :root { --primary: #d66a40; --text: #4a3f35; --accent: #8c7f70; }
    
    @page { 
        size: A4; 
        /* Уменьшаем поля: 10мм сверху/снизу, 7мм по бокам */
        margin: 10mm 7mm; 
        @bottom-right {
            content: counter(page) " / " counter(pages);
            font-size: 8pt;
            color: var(--accent);
        }
    }
    
    body { 
        font-family: 'Inter', sans-serif; 
        color: var(--text); 
        line-height: 1.3; 
        font-size: 10.5pt; 
        margin: 0;
    }
    
    .menu-container {
        /* Включаем две колонки */
        column-count: 2;
        column-gap: 8mm; /* Отступ между колонками */
        column-rule: 0.5pt solid #eee; /* Тонкая разделительная линия */
    }

    .tab-title { 
        font-size: 22pt; color: var(--primary); 
        margin-top: 15pt; 
        margin-bottom: 10pt;
        border-bottom: 1.5pt solid var(--primary); 
        text-transform: uppercase; 
        letter-spacing: 1px;
        column-span: all; /* Заголовок на обе колонки */
    }
    
    .category-block {
        break-inside: avoid; /* Не разбивать категорию между колонками */
        margin-bottom: 15pt;
    }

    .category-title { 
        font-size: 15pt; 
        margin: 10pt 0 8pt; 
        font-weight: 700; 
        page-break-after: avoid;
    }
    
    .product-card { 
        display: flex; 
        align-items: flex-start;
        margin-bottom: 10pt; 
        border-bottom: 0.5pt solid #f5f5f5; 
        padding-bottom: 7pt; 
        page-break-inside: avoid; /* Не разбивать товар между колонками */
    }
    
    .product-img { 
        width: 50pt; /* Немного уменьшили картинку */
        height: 50pt; 
        object-fit: cover; 
        border-radius: 5pt; 
        margin-right: 9pt; 
        flex-shrink: 0;
    }
    
    .product-info { flex: 1; }
    
    .product-header { 
        display: flex; 
        justify-content: space-between; 
        align-items: baseline; 
        margin-bottom: 2pt;
    }
    
    .product-name { font-weight: 700; font-size: 11.5pt; padding-right: 5pt;}
    
    .product-price { color: var(--primary); font-weight: 800; font-size: 12pt; white-space: nowrap; }
    
    .product-meta { font-size: 9pt; color: var(--accent); font-weight: 400;}
    
    .product-desc { font-size: 9.5pt; opacity: 0.85; margin-top: 3pt; line-height: 1.2;}
    """

    content_html = f'<html><head><meta charset="UTF-8"><style>{style}</style></head><body><div class="menu-container">'

    # Группировка
    sections = {"Кухня": {}, "Бар": {}}
    for item in items:
        t = item.get('tab', 'Кухня').strip()
        c = item.get('category', 'Разное')
        if t not in sections: sections[t] = {}
        if c not in sections[t]: sections[t][c] = []
        sections[t][c].append(item)

    for tab_name, categories in sections.items():
        content_html += f'<div class="tab-title">{tab_name}</div>'
        for cat_name, cat_items in categories.items():
            content_html += f'<div class="category-block"><div class="category-title">{cat_name}</div>'
            for item in cat_items:
                img_id = get_drive_id(item.get('img', ''))
                
                img_path = os.path.abspath(f"{THUMBS_DIR}/{img_id}.webp")
                # Используем file:// протокол, чтобы WeasyPrint увидел локальный файл
                img_tag = f'<img src="file://{img_path}" class="product-img">' if img_id and os.path.exists(img_path) else ''
                
                desc = item.get('desc', '').strip()
                weight = item.get('weight', '').strip()

                content_html += f'''
                <div class="product-card">
                    {img_tag}
                    <div class="product-info">
                        <div class="product-header">
                            <span class="product-name">{item["name"]}</span>
                            <span class="product-price">{item["price"]} ₽</span>
                        </div>
                        <div class="product-meta">{weight}</div>
                        <div class="product-desc">{desc}</div>
                    </div>
                </div>'''
            content_html += '</div>' # закрываем category-block
    
    content_html += '</div></body></html>'

    # Сохранить в html виде для дебага в браузере
    # with open('menu_debug.html', 'w', encoding='utf-8') as f:
    #     f.write(content_html)

    # Генерация PDF через WeasyPrint с оптимизацией изображений
    HTML(string=content_html).write_pdf(
        "menu.pdf",
        dpi=120,
        optimize_images=True,  # lossless-оптимизация + downscale до dpi
        jpeg_quality=75,
        font_config=font_config,
        # optimize_size=('images', 'fonts'),
        presentational_hints=True # Помогает с колонками
    )
    size = os.path.getsize("menu.pdf") / (1024 * 1024)
    print(f"Оптимизированный размер PDF: {size:.2f} MB")

if __name__ == "__main__":
    start = time()
    build_pdf()
    print(f'{round(time() - start, 2)} sec')