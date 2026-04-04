import requests
import json
import csv
import os

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR3OtmgAYtqeTFqohCHU_jtr-4ml_YJvWTyElPtgjMVERcE2K9freCbwEslfQcgzEYA4g7UgR13OAZW/pub?gid=0&single=true&output=csv"

def get_drive_id(url):
    """Извлекает ID из ссылки так же, как и process_images.py"""
    if not url: return None
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    elif 'id=' in url:
        return url.split('id=')[1].split('&')[0]
    return None

def build():
    try:
        response = requests.get(SHEET_CSV_URL, timeout=30)
        response.encoding = 'utf-8'
        reader = csv.DictReader(response.text.splitlines())
        items = list(reader)
    except Exception as e:
        print(f"Ошибка при загрузке таблицы: {e}")
        return

    # Группируем по категориям
    categories = {}
    for item in items:
        cat = item.get('category', 'Разное')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    nav_html = ""
    sections_food_html = ""
    sections_bar_html = ""
    flat_items_for_js = []
    global_idx = 0

    for cat_name, cat_items in categories.items():
        # Определяем вкладку по первому товару в категории
        raw_tab = cat_items[0].get('tab', 'Кухня').strip().lower()
        is_bar = (raw_tab == 'бар')
        
        cat_id = f"cat-{abs(hash(cat_name))}"
        tab_key = "bar" if is_bar else "food"
        display_style = 'style="display: none;"' if is_bar else 'style="display: inline-block;"'
        
        nav_html += f'<a href="#{cat_id}" class="nav-item" data-tab="{tab_key}" {display_style}>{cat_name}</a>'
        
        section_html = f'<h2 id="{cat_id}" class="category-title">{cat_name}</h2>\n<div class="menu-grid">'
        
        for item in cat_items:
            price_val = item.get('price', '').strip()
            price_html = f'<div class="product-price">{price_val} ₽</div>' if price_val else ''
            
            img_url = item.get('img', '').strip()
            img_id = get_drive_id(img_url)
            
            if img_id:
                # Проверяем, существуют ли файлы физически в репозитории
                t_path = f"assets/img/thumbs/{img_id}.webp"
                f_path = f"assets/img/full/{img_id}.webp"
                
                item['img_thumb'] = t_path
                item['img_full'] = f_path

                img_tag = f'<img src="{t_path}" class="product-img" loading="lazy" alt="{item["name"]}">'
                card_class = "product-card"
            else:
                item['img_thumb'] = None
                item['img_full'] = None
                img_tag = ""
                card_class = "product-card no-image"

            section_html += f'''
            <div class="{card_class}" onclick="openModal({global_idx})">
                {img_tag}
                <div class="product-info">
                    <div class="product-title">{item['name']}</div>
                    {price_html}
                </div>
            </div>'''

            flat_items_for_js.append(item)
            global_idx += 1

        section_html += '</div>\n'
        
        if is_bar:
            sections_bar_html += section_html
        else:
            sections_food_html += section_html

    # Запись в шаблон
    if not os.path.exists('template.html'):
        print("Ошибка: template.html не найден")
        return

    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    final_html = template.replace('{nav_items}', nav_html)
    final_html = final_html.replace('{sections_food}', sections_food_html)
    final_html = final_html.replace('{sections_bar}', sections_bar_html)
    final_html = final_html.replace('{ items_json }', json.dumps(flat_items_for_js, ensure_ascii=False))

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    build()
