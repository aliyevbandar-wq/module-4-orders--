"""Каталог товаров."""
import tkinter as tk
from styles import (
    COLOR_MAIN_BG, COLOR_HIGHLIGHT,
    FONT_SIZE_NORMAL, FONT_SIZE_HEADER, font
)
from resources import get_product_image


def create_product_card(parent, product, refresh=None):
    """
    Создаёт карточку товара.
    :param parent: родительский контейнер
    :param product: кортеж (id, название, категория, производитель,
                            характеристики, цена, количество,
                            изображение, модель) или аналогичный из БД.
    :param refresh: callback для обновления каталога после заказа
    :return: созданный Frame
    """
    # Безопасно извлекаем количество товара (в КИМ это индекс 6, но в БД может быть индекс 4)
    qty = product[6] if len(product) > 6 else (product[4] if len(product) > 4 else 0)
    
    # 1. Определяем цвет фона в зависимости от остатка
    bg_color = _get_card_color(qty)
    
    # 2. Создаем Frame с рамкой
    card = tk.Frame(parent, bg=bg_color, bd=1, relief="solid")
    
    # 3. Размещаем на экране
    card.pack(fill="x", padx=10, pady=5)
    
    # 4. Добавляем изображение товара или заглушку
    _add_image(card, product, bg_color)
    
    # 5. Добавляем всю текстовую информацию (название, цену, бренд)
    _add_text_info(card, product, bg_color, qty)
    
    # 6. Привязываем открытие детального просмотра по клику на саму карточку
    card.bind("<Button-1>", lambda e: _open_view(parent, product, refresh))
    
    # 7. Проходимся по всем вложенным элементам и тоже биндим клик на них
    for child in card.winfo_children():
        child.bind("<Button-1>", lambda e: _open_view(parent, product, refresh))
        # Обрабатываем элементы второго уровня вложенности (внутри фреймов картинок и текста)
        if isinstance(child, tk.Frame):
            for sub_child in child.winfo_children():
                sub_child.bind("<Button-1>", lambda e: _open_view(parent, product, refresh))
                
    # 8. Возвращаем созданный объект фрейма
    return card


def _get_card_color(qty):
    """
    Возвращает цвет фона карточки.
    Если количество ≤ 3 — подсветка #ff8080 (COLOR_HIGHLIGHT), иначе белый.
    :param qty: количество товара
    :return: HEX-цвет
    """
    if qty <= 3:
        return COLOR_HIGHLIGHT
    return COLOR_MAIN_BG


def _add_image(card, product, bg_color):
    """
    Добавляет изображение товара (или заглушку).
    :param card: карточка товара
    :param product: кортеж с данными товара
    :param bg_color: цвет фона
    """
    # 1. Создаем Frame-контейнер для картинки слева
    img_frame = tk.Frame(card, bg=bg_color)
    img_frame.pack(side="left", padx=10, pady=10)
    
    # Имя картинки в шаблоне под индексом 7
    img_name = product[7] if len(product) > 7 else None
    photo = get_product_image(img_name, size=(100, 100)) if img_name else None
    
    # 2. Если фото успешно загружено — отображаем его
    if photo:
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label["image"] = photo
  # Сохраняем ссылку для защиты от Garbage Collector'а
        img_label.pack()
    else:
        # 3. Иначе выводим текстовую заглушку
        img_label = tk.Label(
            img_frame, 
            text="[НЕТ ФОТО]", 
            bg=bg_color, 
            font=font(size=FONT_SIZE_NORMAL), 
            fg="gray"
        )
        img_label.pack(pady=40)  # Центрируем заглушку по высоте карточки


def _add_text_info(card, product, bg_color, qty):
    """
    Добавляет текстовую информацию о товаре.
    :param card: карточка товара
    :param product: кортеж с данными товара
    :param bg_color: цвет фона
    :param qty: количество
    """
    # 1. Создаем Frame для текстового содержимого
    text_frame = tk.Frame(card, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    
    # Безопасное чтение данных с автоматическим сопоставлением индексов БД и КИМ
    if len(product) >= 9:
        # Если пришел полный кортеж из КИМ (9 полей)
        name = product[1] if product[1] else "[Без названия]"
        category = product[2] if product[2] else "[Без категории]"
        production = product[3] if product[3] else "[Без производителя]"
        characteristics = product[4] if product[4] else "[Не указаны]"
        price = product[5] if product[5] is not None else 0
    else:
        # Если пришел стандартный кортеж напрямую из таблицы Товар (6 полей)
        name = product[1] if product[1] else "[Без названия]"
        production = product[2] if product[2] else "[Без производителя]"
        category = "Электроника"
        characteristics = f"Модель: {product[3]}" if product[3] else "[Не указана]"
        price = product[5] if len(product) > 5 and product[5] is not None else (product[4] if len(product) > 4 else 0)

    # 2. Добавляем метки на форму через вспомогательную функцию _add_label
    _add_label(text_frame, f"{production} | {name}", bg_color, bold=True, size=FONT_SIZE_HEADER)
    _add_label(text_frame, f"Категория: {category}", bg_color)
    _add_label(text_frame, f"Количество: {_indicator(qty)} ({qty} шт.)", bg_color)
    _add_label(text_frame, f"Характеристики: {characteristics}", bg_color)
    
    # Выводим цену, выравнивая её по правому краю фрейма ("e" — East)
    _add_label(text_frame, f"{price} руб.", bg_color, bold=True, size=FONT_SIZE_HEADER, align="e")


def _add_label(parent, text, bg_color, bold=False,
               size=FONT_SIZE_NORMAL, align="w"):
    """
    Добавляет метку с текстом.
    :param parent: родительский фрейм
    :param text: текст метки
    :param bg_color: цвет фона
    :param bold: жирный шрифт
    :param size: размер шрифта
    :param align: выравнивание ("w" — слева, "e" — справа)
    """
    # Сопоставляем текстовое выравнивание Tkinter anchor
    tk_anchor = tk.W if align == "w" else tk.E
    
    # Создаем метку с использованием функции font() из стилей
    lbl = tk.Label(
        parent, 
        text=text, 
        bg=bg_color, 
        anchor=tk_anchor, 
        font=font(size=size, bold=bold)
    )
    # Размещаем метку, растягивая её по горизонтали
    lbl.pack(fill="x", pady=2)


def _indicator(qty):
    """
    Индикатор «много/мало» (порог 5).
    :param qty: количество
    :return: «много» или «мало»
    """
    if qty > 5:
        return "много"
    return "мало"


def _open_view(parent, product, refresh=None):
    """
    Открывает форму просмотра товара.
    :param parent: родительское окно
    :param product: кортеж с данными товара
    :param refresh: callback для обновления каталога
    """
    try:
        from view_form import ViewForm
        ViewForm(parent, product, on_add_to_order=refresh)
    except ImportError:
        # На случай, если файл view_form.py еще не создан или не сдан
        print(f"Открытие карточки товара ID: {product[0]} (Окно детального просмотра не найдено)")
