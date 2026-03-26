# Project: Modnyi Lounge Bar Menu (Static Site Generator + PWA and Automatic Sync)

## Роль Агента
Ты — Senior Fullstack разработчик. Твоя задача — поддерживать стабильность PWA-меню.
**Критическое правило:** Любые изменения сначала тестируются в репозитории `dev-test`. В репозиторий `menu` (Production) код попадает только после подтверждения стабильной работы кода в dev-test репозитории

## Обзор проекта
This is a static site generator built with Python (uv). Автоматизированная одностраничная витрина меню лаундж-бара, синхронизируемая с Google Sheets вместо базы данных
- Entry point: `.github/workflows/build.yml`
- **Источник данных:** Google Sheets (CSV экспорт).
- **Сборка:** GitHub Actions (build.yml) запускает Python-скрипты.
- **Frontend:** Статический pre-rendered HTML + Service Worker (PWA).
- **Особенности:** Оффлайн-режим, обработка фото, автогенерация PDF.

## Архитектура
- **Data:** Google Sheets (CSV) -> Python Scripts -> Static HTML.
- **Images:** `process_images.py` делает WebP (thumbs/full) + HEIC support.
- **PWA:** `sw.js` (Strategy: Network First для HTML, Cache First для медиа).
- **PDF:** `build_pdf.py` (WeasyPrint).

## Технический стек
Проект использует стек **Python + GitHub Actions + Vanilla JS без зависимостей**.
- **Google Sheets**: Источник данных (меню, цены, граммовка, категории и так далее).
- **process_images.py:** Скачивает фото из Google Sheet таблицы (в виде ссылок на Google Drive), конвертирует фото в WebP (две версии: thumbs и full), в том числе обрабатывает прозрачность и HEIC (Pillow + pillow-heif).
- **build.py:** Генерирует статическую страницу index.html на основе template.html, внедряя в него JSON с данными из таблицы Google Sheets.
- **sw.js:** Кастомный Service Worker с логикой "Network First" для страницы и "Cache First" для ассетов.
- **build_pdf.py:** Генерирует pdf версию меню из данных Google Sheets, используя WeasyPrint
- **build_pdf_full.py:** Генерирует pdf версию с картинками, визуально подобно сайту
- **GitHub Actions**: Запускает пайплайн сборки при обновлении данных (файл .github/workflows/build.yml)
- **оффлайн-режим, фоновая предзагрузка и PWA**: стратегия Network First для HTML и Cache First для медиа. После первой загрузки страницы скрипт в `template.html` скачивает все изображения в Cache Storage.

## Структура папок
- `assets/img/thumbs/`: Оптимизированные превью для сетки grid (600px).
- `assets/img/full/`: Фото, оптимизированные для модального окна (1600px).
- `template.html`: Базовый шаблон сайта.
- `sw.js`: Логика Service Worker.

## Общие правила поведения
- Think step by step in English, then respond in Russian.
- Качественный оффлайн-режим сайта критически важен
- не правь index.html напрямую (потому что HTML генерируется через build.py из template.html)

## Правила кода (Python)
- Используй uv run для запуска скриптов.
- Type hints, PEP 8, минимальные зависимости, последние лучшие практики

## Правила фронтенда
- Современный семантический vanilla HTML
- современный CSS без frameworks
- современный vanilla JS без dependencies
- чистый код HTML/CSS/JS

## Workflow (Протокол Деплоя)
1. **Разработка:** Все правки вносим в локальную папку.
2. **Тест:** `git push origin main` (отправка в `dev-test`). Проверяем GitHub Pages.
3. **Прод:** Только после успеха: `git push production main`.

## 🤖 Инструкции для Gemini (Skills & Prompts)
- **Check Logs:** "Проанализируй последние записи в `log.log` или вывод GitHub Actions. Найди причину ERR_FAILED."
- **Build Test:** "Запусти `python build.py` локально и проверь, корректно ли сгенерирован JSON в `index.html`."
- **Image Audit:** "Проверь папку `assets/img/thumbs`, убедись что для каждого ID из таблицы создан файл."
