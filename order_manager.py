"""Работа с заказами."""
import sqlite3
from datetime import datetime
from config import DB_PATH


def get_connection():
    """Соединение с БД."""
    return sqlite3.connect(DB_PATH)


# ============================================
# ЗАДАНИЕ 1.1. get_all_orders
# ============================================
def get_all_orders():
    """Возвращает список всех заказов."""
    # 1. Открываем соединение через get_connection()
    conn = get_connection()
    # 2. Создаем курсор
    cur = conn.cursor()
    # 3. Выполняем SQL: SELECT id, дата, клиент FROM Заказ ORDER BY id DESC
    cur.execute("SELECT id, дата, клиент FROM Заказ ORDER BY id DESC")
    # 4. Получаем все строки через cur.fetchall()
    orders = cur.fetchall()
    # 5. Закрываем соединение
    conn.close()
    # 6. Возвращаем список кортежей
    return orders


# ============================================
# ЗАДАНИЕ 1.2. get_order_items (JOIN)
# ============================================
def get_order_items(order_id):
    """
    Возвращает состав заказа.
    :param order_id: id заказа
    :return: список (id, название, производитель,
                     модель, количество, цена)
    """
    # 1. Открываем соединение
    conn = get_connection()
    # 2. Создаем курсор
    cur = conn.cursor()
    # 3-5. Выполняем JOIN таблиц Состав_заказа и Товар с фильтрацией WHERE
    query = """
        SELECT Состав_заказа.id, Товар.название, Товар.производитель,
               Состав_заказа.модель, Состав_заказа.количество, Состав_заказа.цена
        FROM Состав_заказа
        JOIN Товар ON Состав_заказа.товар_id = Товар.id
        WHERE Состав_заказа.заказ_id = ?
    """
    cur.execute(query, (order_id,))
    # 6. Получаем строки
    items = cur.fetchall()
    # Дополнительно: закрываем соединение
    conn.close()
    # 7. Возвращаем результат
    return items


# ============================================
# ЗАДАНИЕ 1.3. get_order_total
# ============================================
def get_order_total(order_id):
    """
    Возвращает итоговую сумму заказа.
    :param order_id: id заказа
    :return: сумма (float)
    """
    # 1. Открываем соединение
    conn = get_connection()
    cur = conn.cursor()
    # 2. Выполняем SELECT SUM(количество * цена) FROM Состав_заказа WHERE заказ_id = ?
    cur.execute(
        "SELECT SUM(количество * цена) FROM Состав_заказа WHERE заказ_id = ?",
        (order_id,)
    )
    # 3. Получаем row = cur.fetchone()
    row = cur.fetchone()
    conn.close()
    
    # 4. Возвращаем row[0] если не None, иначе 0.0
    if row and row[0] is not None:
        return float(row[0])
    return 0.0


# ============================================
# ЗАДАНИЕ 1.4. create_order
# ============================================
def create_order(client, items):
    """
    Создаёт заказ с несколькими позициями.
    :param client: ФИО клиента
    :param items: список (product_id, model, quantity, price)
    :return: id заказа или None
    """
    # 1. Открываем соединение и курсор
    conn = get_connection()
    cur = conn.cursor()
    
    # 2. Оборачиваем в try-except-finally
    try:
        # Получаем дату: datetime.now().strftime("%Y-%m-%d")
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Выполняем INSERT INTO Заказ (дата, клиент) VALUES (?, ?)
        cur.execute(
            "INSERT INTO Заказ (дата, клиент) VALUES (?, ?)", 
            (date_str, client)
        )
        
        # Получаем order_id = cur.lastrowid
        order_id = cur.lastrowid
        
        # Для каждой позиции из items:
        for item in items:
            product_id, model, quantity, price = item
            
            # SELECT количество FROM Товар WHERE id = ?
            cur.execute("SELECT количество FROM Товар WHERE id = ?", (product_id,))
            product_row = cur.fetchone()
            
            # Если row[0] < quantity — raise ValueError
            if not product_row or product_row[0] < quantity:
                raise ValueError(f"Недостаточно товара с id {product_id} на складе")
            
            # INSERT INTO Состав_заказа
            cur.execute(
                """
                INSERT INTO Состав_заказа (заказ_id, товар_id, модель, количество, price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (order_id, product_id, model, quantity, price)
            )
            
            # UPDATE Товар SET количество = количество - ?
            cur.execute(
                "UPDATE Товар SET количество = количество - ? WHERE id = ?",
                (quantity, product_id)
            )
            
        # conn.commit() и возврат id
        conn.commit()
        return order_id
        
    except Exception:
        # В except — conn.rollback() и возвращаем None
        conn.rollback()
        return None
        
    finally:
        # Обязательно закрываем соединение в блоке finally
        conn.close()


# ============================================
# ЗАДАНИЕ 1.5. delete_order
# ============================================
def delete_order(order_id):
    """
    Удаляет заказ и восстанавливает остатки.
    :param order_id: id заказа
    :return: True или False
    """
    # 1. Открываем соединение
    conn = get_connection()
    cur = conn.cursor()
    
    # 2. Оборачиваем в try-except
    try:
        # SELECT товар_id, количество FROM Состав_заказа WHERE заказ_id = ?
        cur.execute(
            "SELECT товар_id, количество FROM Состав_заказа WHERE заказ_id = ?",
            (order_id,)
        )
        # items = cur.fetchall()
        items = cur.fetchall()
        
        # Для каждой позиции восстанавливаем остаток:
        for product_id, quantity in items:
            # UPDATE Товар SET количество = количество + ? WHERE id = ?
            cur.execute(
                "UPDATE Товар SET количество = количество + ? WHERE id = ?",
                (quantity, product_id)
            )
            
        # DELETE FROM Состав_заказа WHERE заказ_id = ?
        cur.execute("DELETE FROM Состав_заказа WHERE заказ_id = ?", (order_id,))
        
        # DELETE FROM Заказ WHERE id = ?
        cur.execute("DELETE FROM Заказ WHERE id = ?", (order_id,))
        
        # conn.commit() и верни True
        conn.commit()
        return True
        
    except Exception:
        # В except — rollback и верни False
        conn.rollback()
        return False
        
    finally:
        conn.close()


# ============================================
# ЗАДАНИЕ 1.6. update_order_date
# ============================================
def update_order_date(order_id, new_date):
    """
    Обновляет дату заказа.
    :param order_id: id заказа
    :param new_date: новая дата (YYYY-MM-DD)
    :return: True
    """
    # 1. Открываем соединение
    conn = get_connection()
    cur = conn.cursor()
    
    # 2. UPDATE Заказ SET дата = ? WHERE id = ?
    cur.execute("UPDATE Заказ SET дата = ? WHERE id = ?", (new_date, order_id))
    
    # 3. conn.commit()
    conn.commit()
    
    # 4. Закрываем соединение
    conn.close()
    
    # 5. Возвращаем True
    return True


# ============================================
# ЗАДАНИЕ 1.7. delete_order_item
# ============================================
def delete_order_item(item_id):
    """
    Удаляет позицию и восстанавливает остаток.
    :param item_id: id позиции в Состав_заказа
    :return: True или False
    """
    # 1. Открываем соединение
    conn = get_connection()
    cur = conn.cursor()
    
    # 2. Оборачиваем в try-except
    try:
        # SELECT товар_id, количество FROM Состав_заказа WHERE id = ?
        cur.execute(
            "SELECT товар_id, количество FROM Состав_заказа WHERE id = ?",
            (item_id,)
        )
        row = cur.fetchone()
        
        if not row:
            return False
            
        # product_id, quantity = cur.fetchone()
        product_id, quantity = row
        
        # DELETE FROM Состав_заказа WHERE id = ?
        cur.execute("DELETE FROM Состав_заказа WHERE id = ?", (item_id,))
        
        # UPDATE Товар SET количество = количество + ? WHERE id = ?
        cur.execute(
            "UPDATE Товар SET количество = количество + ? WHERE id = ?",
            (quantity, product_id)
        )
        
        # conn.commit() и верни True
        conn.commit()
        return True
        
    except Exception:
        # В except — rollback и верни False
        conn.rollback()
        return False
        
    finally:
        conn.close()
