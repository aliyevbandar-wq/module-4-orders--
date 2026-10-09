import tkinter as tk
from tkinter import ttk, messagebox
from styles import COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT, FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font
import order_manager as om
from datetime import datetime

class OrderItemsWindow:
    """Окно состава заказа."""
    def __init__(self, parent, order_id, current_user=None):
        self.order_id, self.current_user = order_id, current_user
        self.window = tk.Toplevel(parent)
        self.window.title(f"Состав заказа №{order_id}")
        self.window.geometry("900x600")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.window.grab_set()
        
        self.is_admin = current_user and len(current_user) > 5 and current_user[5] == "Администратор"
        self.build_ui()
        self.refresh_all()

    def build_ui(self):
        # 1. Шапка
        hdr = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"СОСТАВ ЗАКАЗА №{self.order_id}", bg=COLOR_SECONDARY_BG, fg=COLOR_ACCENT, font=font(FONT_SIZE_TITLE, bold=True)).pack(pady=15)

        # 2. Инфо-панель
        info = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        info.pack(fill="x", padx=20, pady=15)
        
        tk.Label(info, text="Дата заказа:", bg=COLOR_MAIN_BG, font=font(FONT_SIZE_NORMAL)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(info, textvariable=self.date_var, state="normal" if self.is_admin else "readonly", font=font(FONT_SIZE_NORMAL), width=15)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        if self.is_admin:
            tk.Button(info, text="Сохранить дату", bg=COLOR_ACCENT, fg=COLOR_MAIN_BG, font=font(FONT_SIZE_NORMAL), command=self.save_date).grid(row=0, column=2, padx=10)

        tk.Label(info, text="Клиент:", bg=COLOR_MAIN_BG, font=font(FONT_SIZE_NORMAL, bold=True)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.client_label = tk.Label(info, text="", bg=COLOR_MAIN_BG, font=font(FONT_SIZE_NORMAL))
        self.client_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        # 3. Таблица (Treeview)
        t_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        t_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = {"id": ("ID", 50, "center"), "name": ("Название", 200, "w"), "prod": ("Производитель", 120, "w"), 
                "model": ("Модель", 120, "w"), "qty": ("Кол-во", 70, "center"), "price": ("Цена (руб.)", 100, "e"), "tot": ("Всего (руб.)", 120, "e")}
        
        self.tree = ttk.Treeview(t_frame, columns=list(cols.keys()), show="headings", selectmode="browse")
        sb = ttk.Scrollbar(t_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        for cid, (txt, w, anc) in cols.items():
            self.tree.heading(cid, text=txt)
            self.tree.column(cid, width=w, anchor=anc)

        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # 4. Итог
        self.total_label = tk.Label(self.window, text="ИТОГО: 0.00 руб.", bg=COLOR_MAIN_BG, fg=COLOR_ACCENT, font=font(FONT_SIZE_TITLE, bold=True))
        self.total_label.pack(anchor="e", padx=20, pady=10)

        # 5. Кнопки
        btns = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        btns.pack(fill="x", side="bottom", padx=20, pady=15)

        if self.is_admin:
            tk.Button(btns, text="Удалить позицию", bg="#FF4D4D", fg="#FFFFFF", font=font(FONT_SIZE_NORMAL), command=self.delete_item).pack(side="left", padx=5)
        
        tk.Button(btns, text="Обновить", bg=COLOR_SECONDARY_BG, fg="#FFFFFF", font=font(FONT_SIZE_NORMAL), command=self.refresh_all).pack(side="left", padx=5)
        tk.Button(btns, text="Назад", bg=COLOR_SECONDARY_BG, fg="#FFFFFF", font=font(FONT_SIZE_NORMAL), command=self.window.destroy).pack(side="right", padx=5)

    def refresh_all(self):
        order = om.get_order_by_id(self.order_id)
        if order:
            # Обход readonly режима для программного изменения текста
            self.date_entry.config(state="normal")
            self.date_var.set(order[1])
            self.date_entry.config(state="normal" if self.is_admin else "readonly")
            self.client_label.config(text=order[2])

        for row in self.tree.get_children(): self.tree.delete(row)
        
        for item in om.get_order_items(self.order_id):
            self.tree.insert("", "end", values=(item[0], item[1], item[2], item[3], item[4], item[5], item[4] * item[5]))

        self.total_label.config(text=f"ИТОГО: {om.get_order_total(self.order_id):.2f} руб.")

    def save_date(self):
        new_date = self.date_var.get().strip()
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            if om.update_order_date(self.order_id, new_date):
                messagebox.showinfo("Успех", "Дата изменена.")
                self.refresh_all()
        except ValueError:
            messagebox.showerror("Ошибка", "Формат: ГГГГ-ММ-ДД")

    def delete_item(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Удаление", "Удалить позицию?"):
            if om.delete_order_item(self.tree.item(sel[0])["values"][0]):
                messagebox.showinfo("Успех", "Товар удален.")
                self.refresh_all()
