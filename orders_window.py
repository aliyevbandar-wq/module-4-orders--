import tkinter as tk
from tkinter import ttk, messagebox
from styles import (
    COLOR_MAIN_BG,
    COLOR_SECONDARY_BG,
    COLOR_ACCENT,
    FONT_SIZE_NORMAL,
    FONT_SIZE_TITLE,
    font  # Используем как функцию генерации шрифта
)
import order_manager as om


class OrdersWindow:
    """Окно списка заказов."""

    def __init__(self, parent, current_user=None):
        self.current_user = current_user
        self.window = tk.Toplevel(parent)
        self.window.title("Список заказов")
        self.window.geometry("800x500")
        self.window.configure(bg=COLOR_MAIN_BG)
        
        self.window.grab_set()
        
        self.build_ui()
        self.load_orders()

    def build_ui(self):
        """Строит интерфейс."""
        header_frame = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        # ИСПРАВЛЕНО: вызываем функцию font() напрямую с именованными аргументами
        header_label = tk.Label(
            header_frame,
            text="СПИСОК ЗАКАЗОВ",
            bg=COLOR_SECONDARY_BG,
            fg=COLOR_ACCENT,
            font=font(size=FONT_SIZE_TITLE, bold=True)
        )
        header_label.pack(pady=15)

        table_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.tree = ttk.Treeview(
            table_frame, 
            columns=("id", "date", "client"), 
            show="headings",
            selectmode="browse"
        )
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.heading("id", text="No")
        self.tree.heading("date", text="Дата")
        self.tree.heading("client", text="Клиент")

        self.tree.column("id", width=50, minwidth=50, anchor=tk.CENTER)
        self.tree.column("date", width=120, minwidth=120, anchor=tk.CENTER)
        self.tree.column("client", width=400, minwidth=250, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_order_select)

        buttons_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=15)

        # ИСПРАВЛЕНО: вызываем функцию font() для нормального размера и жирности по умолчанию
        btn_view = tk.Button(
            buttons_frame,
            text="Просмотр состава",
            bg=COLOR_ACCENT,
            fg=COLOR_MAIN_BG,
            font=font(size=FONT_SIZE_NORMAL),
            command=self.on_order_select
        )
        btn_view.pack(side=tk.LEFT, padx=10)

        # ИСПРАВЛЕНО: аналогично вызываем функцию font()
        btn_back = tk.Button(
            buttons_frame,
            text="Назад",
            bg=COLOR_SECONDARY_BG,
            fg="#FFFFFF",
            font=font(size=FONT_SIZE_NORMAL),
            command=self.window.destroy
        )
        btn_back.pack(side=tk.RIGHT, padx=10)

    def load_orders(self):
        """Загружает заказы."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        orders = om.get_all_orders()

        for order in orders:
            self.tree.insert("", tk.END, values=order)

    def on_order_select(self, event=None):
        """Обработчик выбора."""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите заказ из списка.")
            return

        # ИСПРАВЛЕНО: Достаем первый элемент кортежа values корректно
        order_id = self.tree.item(selected[0])["values"][0]

        from order_items_window import OrderItemsWindow
        OrderItemsWindow(self.window, order_id, self.current_user)
