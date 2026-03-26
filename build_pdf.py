import requests
import csv
import os
from weasyprint import HTML, CSS

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR3OtmgAYtqeTFqohCHU_jtr-4ml_YJvWTyElPtgjMVERcE2K9freCbwEslfQcgzEYA4g7UgR13OAZW/pub?gid=0&single=true&output=csv"
LOGO_URL = "https://raw.githubusercontent.com/modnyi-lounge/dev-test/main/assets/logo.svg"

def build_pdf():
    try:
        response = requests.get(SHEET_CSV_URL, timeout=30)
        response.encoding = 'utf-8'
        reader = csv.DictReader(response.text.splitlines())
        items = list(reader)

        logo_response = requests.get(LOGO_URL, timeout=15)
        logo_content = logo_response.content if logo_response.status_code == 200 else None
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return

    tabs = {'Кухня': {}, 'Бар': {}}
    for item in items:
        tab_name = item.get('tab', 'Кухня').strip()
        cat = item.get('category', 'Разное')
        target_tab = 'Бар' if tab_name.lower() == 'бар' else 'Кухня'
        if cat not in tabs[target_tab]:
            tabs[target_tab][cat] = []
        tabs[target_tab][cat].append(item)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <style>
            /* Подключаем шрифт Inter для корректного отображения ₽ и кириллицы в Ubuntu */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

            @page {{
                size: A4;
                margin: 12mm;
                background-color: #F5E6D3;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                color: #1E1E1E;
                margin: 0;
                padding: 0;
                -webkit-font-smoothing: antialiased;
            }}

            .header-block {{
                column-span: all;
                text-align: center;
                margin-bottom: 12mm;
            }}

            h1 {{
                text-align: center;
                font-size: 24pt;
                text-transform: uppercase;
                letter-spacing: 3px;
                margin-top: 5mm;
                margin-bottom: 10mm;
                color: #1E1E1E;
                column-span: all;
                font-weight: 700;
            }}

            .menu-columns {{
                column-count: 2;
                column-gap: 12mm;
                column-fill: balance;
            }}

            .category-block {{
                display: block;
                break-inside: auto;
                margin-bottom: 12mm;
            }}

            .category-title {{
                text-align: center;
                font-size: 14pt;
                text-transform: uppercase;
                margin: 0 0 5mm 0;
                font-weight: 700;
                border-bottom: 1px solid rgba(0,0,0,0.1);
                padding-bottom: 2mm;
                break-after: avoid; /* Запрещаем заголовку категории отрываться от первого блюда */
            }}

            .item {{
                display: flex;
                break-inside: avoid; /* Полный запрет разрыва внутри блюда */
                margin-bottom: 3.5mm;
                justify-content: space-between;
                align-items: baseline; /* Название и цена на одном уровне (по базовой линии) */
            }}

            .item-content {{
                flex: 1;
                padding-right: 3mm;
            }}

            .item-name {{
                font-weight: 700;
                font-size: 10.5pt;
                line-height: 1.2;
                display: block;
            }}

            .item-meta {{
                font-size: 8.5pt;
                color: #4a3e35;
                line-height: 1.2;
                opacity: 0.8;
                display: block;
                margin-top: 1mm;
            }}

            .item-price-block {{
                display: flex;
                align-items: baseline;
                white-space: nowrap;
                font-weight: 700;
                flex-shrink: 0;
                font-size: 10.5pt;
            }}

            .item-weight {{
                font-size: 8.5pt;
                color: #4a3e35;
                font-weight: 400;
            }}

            .price-divider {{
                font-size: 11pt;
                margin: 0 2px;
                color: #1E1E1E;
                font-weight: 400;
            }}

            .item-price {{
                font-size: 11pt;
            }}
        </style>
    </head>
    <body>
    <div class="header-block">{logo_content.decode("utf-8") if logo_content else ""}</div>
    """

    for tab_name, categories in tabs.items():
        if not categories: continue
        
        # Начинаем Бар с новой страницы
        page_break = 'style="page-break-before: always;"' if tab_name == 'Бар' else ''
        
        html_content += f'<div {page_break}>'
        tab_title = '' if tab_name.lower() == 'кухня' else f'<h1>{tab_name}</h1>'
        html_content += tab_title
        html_content += '<div class="menu-columns">'
        
        for cat_name, cat_items in categories.items():
            # Оборачиваем каждую категорию в блок .category-block
            html_content += f'<div class="category-block"><h2 class="category-title">{cat_name}</h2>'
            
            for item in cat_items:
                name = item.get('name', '')
                price = item.get('price', '').strip()
                desc = item.get('desc', '').strip()
                weight = item.get('weight', '').strip()

                price_block = ""
                if weight and price:
                    price_block = f'<span class="item-weight">{weight}</span><span class="price-divider">/</span><span class="item-price">{price} ₽</span>'
                elif price:
                    price_block = f'<span class="item-price">{price} ₽</span>'
                elif weight:
                    price_block = f'<span class="item-weight">{weight}</span>'
                
                html_content += f"""
                <div class="item">
                    <div class="item-content">
                        <span class="item-name">{name}</span>
                        {f'<span class="item-meta">{desc}</span>' if desc else ''}
                    </div>
                    <div class="item-price-block">{price_block}</div>
                </div>
                """
            html_content += '</div>' # Закрываем .category-block

        html_content += '</div></div>'

    html_content += "</body></html>"

    # Сохранить в html виде для дебага в браузере
    # with open('menu_debug.html', 'w', encoding='utf-8') as f:
    #     f.write(html_content)

    print("Генерация PDF...")
    HTML(string=html_content, base_url=os.path.dirname(os.path.abspath(__file__))).write_pdf(
        'menu_text.pdf', 
        stylesheets=[CSS(string='svg { width: 140px; height: auto; margin: 0 auto; display: block; }')]
    )
    print("PDF сгенерирован!")

if __name__ == "__main__":
    build_pdf()
