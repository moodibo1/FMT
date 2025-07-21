import json
import os
import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, Toplevel, ttk
from PIL import Image, ImageTk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Button as ttkButton
from ttkbootstrap.widgets import Entry, Combobox
import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button, Entry, Combobox, Label
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
import openpyxl
from openpyxl import Workbook

USERNAME = "admin"
PASSWORD = "admin"

def show_login_window():
    login_win = tk.Toplevel(app)  # اربطها بالنافذة الرئيسية app
    login_win.title("Login")
    login_win.geometry("800x680")
    login_win.grab_set()  # منع التفاعل مع باقي النوافذ

    tk.Label(login_win, text="Username:", font=("Segoe UI", 12)).pack(pady=(20, 5))
    user_entry = tk.Entry(login_win, font=("Segoe UI", 12))
    user_entry.pack()

    tk.Label(login_win, text="Password:", font=("Segoe UI", 12)).pack(pady=(10, 5))
    pass_entry = tk.Entry(login_win, show="*", font=("Segoe UI", 12))
    pass_entry.pack()
    tk.Label(login_win, text="MADE BY IBRAHIM Z.", font=("Segoe UI", 26)).pack(pady=(40, 5))


    def try_login():
        if user_entry.get() == USERNAME and pass_entry.get() == PASSWORD:
            login_win.destroy()
            app.deiconify()  # إظهار النافذة الرئيسية
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(login_win, text="Login", font=("Segoe UI", 12), command=try_login).pack(pady=15)

    # Optional: close app if user closes login window without logging in
    def on_close():
        login_win.destroy()
        app.destroy()  # يغلق التطبيق كله

    login_win.protocol("WM_DELETE_WINDOW", on_close)






import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog

CONFIG_FILE = "config.txt"

def save_db_path(path):
    with open(CONFIG_FILE, "w") as f:
        f.write(path)

def load_db_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            path = f.read().strip()
            if os.path.exists(path):
                return path
    return None

def ask_user_for_db():
    choice = messagebox.askquestion(
        "DATA BASE",
        "CLICK YES TO CHOOOSE AN EXSITING DB AND NO TO MAKE A NEW ONE"
    )
    if choice == 'yes':
        path = filedialog.askopenfilename(
            title="CHOOSE DB",
            filetypes=[("SQLite Database", "*.db")]
        )
    else:
        path = os.path.join(os.getcwd(), "factory_maintenance_new.db")
        conn = sqlite3.connect(path)
        conn.close()
        messagebox.showinfo("NEW DB", f"A NEW DB WHERE MADE IN THIS PATH:\n{path}")
    return path if path else None

def init_db_path():
    db_path = load_db_path()
    if not db_path:
        db_path = ask_user_for_db()
        if not db_path:
            messagebox.showerror("error", "you must choose or make a db")
            exit()
        save_db_path(db_path)
    return db_path

# ----- تنفيذ الإنشاء -----
root = tk.Tk()
root.withdraw()  # إخفاء نافذة التطبيق مؤقتاً

db_path = init_db_path()
conn = sqlite3.connect(db_path)
c = conn.cursor()

# --- إنشاء الجداول ---

try:
    c.execute("ALTER TABLE orders ADD COLUMN category_id INTEGER DEFAULT NULL")
    conn.commit()
except sqlite3.OperationalError:
    pass


c.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    image_path TEXT DEFAULT 'default_category.png'
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS machines (
    id TEXT PRIMARY KEY,
    name TEXT,
    location TEXT,
    category_id INTEGER,
    purchase_date TEXT,
    last_maintenance TEXT,
    maintenance_interval_days INTEGER,
    image_path TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT,
    entry TEXT,
    timestamp TEXT,
    user TEXT DEFAULT 'Unknown'
)
''')

# جدول الطلبات مع كل الأعمدة الجديدة
c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'waiting',
    category TEXT,
    notes TEXT,
    action_type TEXT
)
''')

# سجل تغييرات الطلبات
c.execute('''
CREATE TABLE IF NOT EXISTS order_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    action TEXT,
    timestamp TEXT,
    user TEXT DEFAULT 'Unknown',
    FOREIGN KEY (order_id) REFERENCES orders(id)
)
''')

# معلومات إنهاء الطلب (المشرف والعمال)
c.execute("""
CREATE TABLE IF NOT EXISTS order_finish_info (
    order_id INTEGER PRIMARY KEY,
    leader TEXT,
    workers TEXT
)
""")

# تأكد أن عمود ratings موجود (للإصدار القديم من الجدول)
try:
    c.execute("ALTER TABLE order_finish_info ADD COLUMN ratings TEXT")
except sqlite3.OperationalError:
    pass


conn.commit()

# --------- إعداد التطبيق ---------
app = tk.Tk()
app.title("Factory Maintenance Tracker")
app.geometry("1200x700")
selected_category_id = None

style = Style("darkly")  # ثيم داكن جميل

image_refs = {}  # للاحتفاظ بالصور حتى لا تُحذف من الذاكرة
selected_machine_id = None
c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ongoing'
)
''')
c.execute("""
    CREATE TABLE IF NOT EXISTS order_ratings (
        order_id INTEGER PRIMARY KEY,
        worker_ratings TEXT
    )
""")


conn.commit()

# --------- دوال مساعدة ---------







def show_maintenance_alert():
    c.execute("SELECT id, last_maintenance, maintenance_interval_days FROM machines")
    all_machines = c.fetchall()

    total_due = 0
    red_count = 0
    yellow_count = 0
    green_count = 0

    now = datetime.now()

    for mid, last, interval in all_machines:
        try:
            last_date = datetime.strptime(last, "%Y-%m-%d")
            next_due = last_date + timedelta(days=interval)
            days_left = (next_due - now).days

            if days_left < 0:
                red_count += 1    # متأخرة أكثر من يوم
                total_due += 1
            elif days_left <= 1:
                red_count += 1    # يوم أو أقل متبقي
                total_due += 1
            elif days_left <= 7:
                yellow_count += 1 # أقل من أسبوع متبقي
                total_due += 1
            else:
                green_count += 1  # أكثر من أسبوع متبقي (حسنا)
        except Exception:
            pass

    if total_due == 0:
        messagebox.showinfo("Maintenance Status", "🎉 All machines are well maintained! ✅")
    else:
        msg = (f"Maintenance Alert:\n"
               f"🔴 Red (due or overdue ≤ 1 day): {red_count}\n"
               f"🟡Yellow (due in ≤ 7 days): {yellow_count}\n"
               f"🟢 Green (more than 7 days left): {green_count}\n"
               f"Total machines needing attention: {total_due}")
        messagebox.showwarning("Maintenance Alert", msg)

# استدعِ الدالة عند تشغيل البرنامج
show_maintenance_alert()
def calculate_days_left(last_maintenance, interval_days):
    try:
        last_date = datetime.strptime(last_maintenance, "%Y-%m-%d")
        next_maintenance = last_date + timedelta(days=interval_days)
        delta = next_maintenance - datetime.now()
        return delta.days if delta.days >= 0 else 0
    except:
        return "N/A"

def clear_form():
    entry_id.config(state=tk.NORMAL)
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_location.delete(0, tk.END)
    combo_category.set("")
    entry_purchase.delete(0, tk.END)
    entry_last.delete(0, tk.END)
    entry_interval.delete(0, tk.END)
    days_left_label.config(text="Days Left: N/A")
    image_path_var.set("")

def browse_category_image():
    path = filedialog.askopenfilename(
        title="Select an image for category",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All files", "*.*")
        ]
    )
    if path:
        image_path_var_category.set(path)

def load_categories_into_combo():
    c.execute("SELECT name FROM categories")
    names = [row[0] for row in c.fetchall()]
    combo_category['values'] = names
    if names:
        combo_category.set(names[0])

# --------- عرض كروت التصنيفات مع الصور ---------
selected_category_id = None  # متغير عالمي في ملفك الرئيسي

def display_category_cards():
    global selected_category_id
    for widget in inner_frame.winfo_children():
        widget.destroy()


    c.execute("SELECT id, name, image_path FROM categories")
    categories = c.fetchall()

    if not categories:
        no_cat_label = tk.Label(inner_frame, text="No categories added yet.", fg="white", bg=style.colors.bg, font=("Helvetica", 20))
        no_cat_label.pack(pady=30)
        return

    max_cards = 6
    rows = 2
    cols = 3

    def reset_card_colors():
        for child in inner_frame.winfo_children():
            child.config(bg=style.colors.primary)

    for idx, (cat_id, cat_name, img_path) in enumerate(categories[:max_cards]):
        frame = tk.Frame(inner_frame, bg=style.colors.primary, relief="raised", bd=4, width=350, height=220)
        frame.grid(row=idx // cols, column=idx % cols, padx=15, pady=15)
        frame.grid_propagate(False)

        # صورة التصنيف (إذا موجودة)
        if img_path and os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path).resize((140, 140))
                img = ImageTk.PhotoImage(pil_img)
                image_refs[f"cat_{cat_id}"] = img
                img_label = tk.Label(frame, image=img, bg=style.colors.primary)
            except:
                img_label = tk.Label(frame, text="Image Error", fg="red", bg=style.colors.primary, font=("Helvetica", 10))
        else:
            img_label = tk.Label(frame, text="No Image", fg="gray", bg=style.colors.primary, font=("Helvetica", 12, "italic"))

        img_label.pack(pady=10)

        label = tk.Label(frame, text=cat_name, font=("Helvetica", 18, "bold"), fg="white", bg=style.colors.primary)
        label.pack()

        def on_card_click(event, category_id=cat_id, card_frame=frame):
            global selected_category_id
            selected_category_id = category_id

            reset_card_colors()
            card_frame.config(bg="darkgreen")

            display_machines_by_category(category_id)

        frame.bind("<Button-1>", on_card_click)
        img_label.bind("<Button-1>", on_card_click)
        label.bind("<Button-1>", on_card_click)
# --------- عرض الآلات حسب التصنيف ---------
def display_machines_by_category(category_id):
    for widget in inner_frame.winfo_children():
        widget.destroy()

    c.execute("SELECT id, name, last_maintenance, maintenance_interval_days, image_path FROM machines WHERE category_id=?", (category_id,))
    machines = c.fetchall()

    def back_to_categories():
        display_category_cards()

    back_btn = ttkButton(inner_frame, text="← Back to Categories", command=back_to_categories)
    back_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    if not machines:
        no_machine_label = tk.Label(inner_frame, text="No machines in this category.", fg="white", bg=style.colors.bg, font=("Helvetica", 18))
        no_machine_label.grid(row=1, column=0, padx=20, pady=20)
        return

    for i, (mid, name, last, interval, path) in enumerate(machines):
        days_left = calculate_days_left(last, interval)

        frame = tk.Frame(inner_frame, bg=style.colors.bg, bd=1, relief=tk.SOLID)
        frame.grid(row=i + 1, column=0, sticky="ew", padx=10, pady=6)
        frame.columnconfigure(1, weight=1)

        # صورة الآلة صغيرة
        img_label = tk.Label(frame, bg=style.colors.bg)
        img_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5)

        if path and os.path.exists(path):
            try:
                pil_img = Image.open(path).resize((60, 60))
                img = ImageTk.PhotoImage(pil_img)
                image_refs[mid] = img
                img_label.config(image=img)
            except:
                img_label.config(text="Img Err", fg="red", font=("Helvetica", 8))
        else:
            img_label.config(text="No Img", fg="gray", font=("Helvetica", 8, "italic"))

        tk.Label(frame, text=name, bg=style.colors.bg, fg="white", font=("Helvetica", 14, "bold")).grid(row=0, column=1, sticky="w")
        tk.Label(frame, text=f"ID: {mid}  |  Days Left: {days_left}", bg=style.colors.bg, fg="lightgray", font=("Helvetica", 12)).grid(row=1, column=1, sticky="w")

        # ربط الضغط الأحادى والثنائي لفتح التفاصيل
        frame.bind("<Button-1>", lambda e, m=mid: select_machine(m))
        img_label.bind("<Button-1>", lambda e, m=mid: select_machine(m))

        frame.bind("<Double-Button-1>", lambda e, m=mid: (select_machine(m), open_machine_popup()))
        img_label.bind("<Double-Button-1>", lambda e, m=mid: (select_machine(m), open_machine_popup()))

# --------- دوال إضافة وتحديث وحذف ---------





ORDER_CATEGORIES = [
    "Maintenance", "Spare Parts", "Operation", "Software Update",
    "Periodic Check", "Safety", "Electricity", "Mechanical", "Modification", "Other"
]

ORDER_ACTION_TYPES = [
    "Wash", "Replace", "Repair", "Inspect", "Calibrate", "Upgrade", "Other"
]

LEADERS = []
WORKERS = []

def load_people():
    global LEADERS, WORKERS
    try:
        with open("leaders.txt", "r", encoding="utf-8") as f:
            LEADERS = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        LEADERS = []

    try:
        with open("workers.txt", "r", encoding="utf-8") as f:
            WORKERS = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        WORKERS = []

# load once on program start
load_people()

CATEGORIES_FILE = "categories.txt"
ACTION_TYPES_FILE = "action_types.txt"

def load_static_list(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_static_list(file_path, items):
    with open(file_path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(item + "\n")

def add_to_list(entry_widget, listbox_widget, file_path):
    new_item = entry_widget.get().strip()
    if not new_item:
        messagebox.showerror("Error", "Entry is empty.")
        return
    items = load_static_list(file_path)
    if new_item in items:
        messagebox.showerror("Error", "Item already exists.")
        return
    items.append(new_item)
    save_static_list(file_path, items)
    load_list_to_listbox(file_path, listbox_widget)
    entry_widget.delete(0, tk.END)

def delete_selected(listbox_widget, file_path):
    selected = listbox_widget.curselection()
    if not selected:
        messagebox.showerror("Error", "No item selected.")
        return
    index = selected[0]
    items = load_static_list(file_path)
    del items[index]
    save_static_list(file_path, items)
    load_list_to_listbox(file_path, listbox_widget)

def load_list_to_listbox(file_path, listbox_widget):
    listbox_widget.delete(0, tk.END)
    for item in load_static_list(file_path):
        listbox_widget.insert(tk.END, item)

# === Manage Categories window ===
def manage_categories_window():
    cat_win = tk.Toplevel()
    cat_win.title("Manage Categories")
    cat_win.geometry("400x400")
    cat_win.configure(bg=style.lookup("TFrame", "background") or "white")

    ttk.Label(cat_win, text="Add New Category:").pack(pady=(10, 2))
    entry_cat = ttk.Entry(cat_win)
    entry_cat.pack(pady=2)
    ttk.Button(cat_win, text="Add Category", bootstyle="success",
               command=lambda: add_to_list(entry_cat, listbox_cat, CATEGORIES_FILE)).pack(pady=5)

    listbox_cat = tk.Listbox(cat_win, height=15)
    listbox_cat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    ttk.Button(cat_win, text="Delete Selected Category", bootstyle="danger",
               command=lambda: delete_selected(listbox_cat, CATEGORIES_FILE)).pack(pady=5)

    load_list_to_listbox(CATEGORIES_FILE, listbox_cat)

# === Manage Action Types window ===
def manage_action_types_window():
    act_win = tk.Toplevel()
    act_win.title("Manage Action Types")
    act_win.geometry("400x400")
    act_win.configure(bg=style.lookup("TFrame", "background") or "white")

    ttk.Label(act_win, text="Add New Action Type:").pack(pady=(10, 2))
    entry_act = ttk.Entry(act_win)
    entry_act.pack(pady=2)
    ttk.Button(act_win, text="Add Action Type", bootstyle="success",
               command=lambda: add_to_list(entry_act, listbox_act, ACTION_TYPES_FILE)).pack(pady=5)

    listbox_act = tk.Listbox(act_win, height=15)
    listbox_act.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    ttk.Button(act_win, text="Delete Selected Action Type", bootstyle="danger",
               command=lambda: delete_selected(listbox_act, ACTION_TYPES_FILE)).pack(pady=5)

    load_list_to_listbox(ACTION_TYPES_FILE, listbox_act)


def open_orders_window():
    global ORDER_CATEGORIES, ORDER_ACTION_TYPES
    ORDER_CATEGORIES = load_static_list(CATEGORIES_FILE) or [
        "Maintenance", "Spare Parts", "Operation", "Software Update",
        "Periodic Check", "Safety", "Electricity", "Mechanical", "Modification", "Other"
    ]
    ORDER_ACTION_TYPES = load_static_list(ACTION_TYPES_FILE) or [
        "Wash", "Replace", "Repair", "Inspect", "Calibrate", "Upgrade", "Other"
    ]

    import json
    from datetime import datetime
    from openpyxl import Workbook
    from tkinter import messagebox

    def reset_orders():
        # Fetch finished orders directly
        c.execute("""
            SELECT id, name, description, category, action_type, notes
            FROM orders
            WHERE status='finished'
        """)
        finished_orders = c.fetchall()

        if not finished_orders:
            messagebox.showinfo("Reset Orders", "No finished orders to export.")
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Finished Orders"

        # Header
        ws.append([
            "ID", "Name", "Description", "Category", "Action Type",
            "Notes", "Leader", "Workers (with ratings)",
            "Started At", "Ongoing At", "Finished At"
        ])

        for order in finished_orders:
            order_id, name, description, category_name, action_type, notes = order

            # Get finish info
            c.execute("SELECT leader, workers, ratings FROM order_finish_info WHERE order_id=?", (order_id,))
            finish_info = c.fetchone()
            leader = finish_info[0] if finish_info else ""
            workers_list = finish_info[1].split(", ") if finish_info and finish_info[1] else []

            # Ratings
            ratings_dict = {}
            if finish_info and finish_info[2]:
                try:
                    ratings_dict = json.loads(finish_info[2])
                except json.JSONDecodeError:
                    ratings_dict = {}

            workers_with_ratings = []
            for w in workers_list:
                rating = ratings_dict.get(w, "-")
                workers_with_ratings.append(f"{w} ({rating})")
            workers_str = ", ".join(workers_with_ratings)

            # History
            c.execute("SELECT action, timestamp FROM order_history WHERE order_id=? ORDER BY id", (order_id,))
            history_rows = c.fetchall()
            started_at = ongoing_at = finished_at = ""
            for action, ts in history_rows:
                if "created" in action.lower():
                    started_at = ts
                elif "ongoing" in action.lower():
                    ongoing_at = ts
                elif "finished" in action.lower():
                    finished_at = ts

            # Append row to Excel
            ws.append([
                order_id, name, description, category_name, action_type,
                notes or "", leader, workers_str,
                started_at, ongoing_at, finished_at
            ])

        # Save file
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"finished_orders_{now_str}.xlsx"
        wb.save(filename)

        # Delete exported orders
        c.execute("DELETE FROM orders WHERE status='finished'")
        c.execute("DELETE FROM order_history WHERE order_id NOT IN (SELECT id FROM orders)")
        c.execute("DELETE FROM order_finish_info WHERE order_id NOT IN (SELECT id FROM orders)")
        c.execute("DELETE FROM sqlite_sequence WHERE name='orders'")

        conn.commit()

        load_orders()
        messagebox.showinfo("Reset Orders", f"{len(finished_orders)} finished orders saved to {filename} and deleted.")

    def on_order_double_click(event):
        selected_item = tree.focus()
        if not selected_item:
            return

        order_values = tree.item(selected_item)["values"]
        order_id = order_values[0]

        c.execute("SELECT name, description, notes, category, action_type FROM orders WHERE id=?", (order_id,))
        order = c.fetchone()
        if not order:
            messagebox.showerror("Error", "Order not found.")
            return

        name, description, notes, category, action_type = order

        c.execute("SELECT action, timestamp FROM order_history WHERE order_id=? ORDER BY id", (order_id,))
        history = c.fetchall()

        detail_win = Toplevel(orders_win)
        detail_win.title(f"Order #{order_id} Details")
        detail_win.geometry("900x650")
        detail_win.configure(bg=style.lookup("TFrame", "background") or "white")

        ttk.Label(detail_win, text=f"Name: {name}", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        ttk.Label(detail_win, text=f"Category: {category}", font=("Arial", 11)).pack(anchor="w", padx=10)
        ttk.Label(detail_win, text=f"Action Type: {action_type}", font=("Arial", 11)).pack(anchor="w", padx=10)

        ttk.Label(detail_win, text="Description:", font=("Arial", 11, "underline")).pack(anchor="w", padx=10)
        desc_box = tk.Text(detail_win, height=4, wrap="word")
        desc_box.pack(fill="x", padx=10)
        desc_box.insert("1.0", description)
        desc_box.config(state="disabled")

        ttk.Label(detail_win, text="Notes:", font=("Arial", 11, "underline")).pack(anchor="w", padx=10, pady=(10, 0))
        notes_box = tk.Text(detail_win, height=3, wrap="word")
        notes_box.pack(fill="x", padx=10)
        notes_box.insert("1.0", notes)
        notes_box.config(state="disabled")

        ttk.Label(detail_win, text="Order History:", font=("Arial", 11, "underline")).pack(anchor="w", padx=10, pady=(10, 0))
        history_box = tk.Text(detail_win, height=10, wrap="word")
        history_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if history:
            for action, timestamp in history:
                history_box.insert("end", f"[{timestamp}] {action}\n")
        else:
            history_box.insert("end", "No history found.")

        history_box.config(state="disabled")

    orders_win = Toplevel()
    orders_win.title("Work Orders")
    orders_win.geometry("900x600")
    orders_win.configure(bg=style.lookup("TFrame", "background") or "white")

    main_frame = ttk.Frame(orders_win, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    filter_frame = ttk.Frame(orders_win)
    filter_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

    ttk.Label(filter_frame, text="Filter by Category:").pack(side=tk.LEFT)
    filter_var = tk.StringVar()
    combo_filter = ttk.Combobox(filter_frame, textvariable=filter_var, values=["All"] + ORDER_CATEGORIES, state="readonly")
    combo_filter.set("All")
    combo_filter.pack(side=tk.LEFT, padx=5)

    def on_filter_change(event=None):
        load_orders()

    combo_filter.bind("<<ComboboxSelected>>", on_filter_change)

    columns = ("id", "name", "description", "notes", "category", "action_type", "status", "history")

    tree = ttk.Treeview(main_frame, columns=columns, show="headings")
    tree.heading("id", text="ID")
    tree.heading("name", text="Name")
    tree.heading("description", text="Description")
    tree.heading("notes", text="Notes")
    tree.heading("category", text="Category")
    tree.heading("action_type", text="Action Type")
    tree.heading("status", text="Status")
    tree.heading("history", text="Last History")

    tree.column("id", width=50, anchor=tk.CENTER)
    tree.column("name", width=150)
    tree.column("description", width=250)
    tree.column("notes", width=150)
    tree.column("category", width=100)
    tree.column("action_type", width=100)
    tree.column("status", width=100, anchor=tk.CENTER)
    tree.column("history", width=180)
    tree.pack(fill=tk.BOTH, expand=True, pady=10)
    tree.bind("<Double-1>", on_order_double_click)

    tree.tag_configure("waiting", background="#cce5ff", foreground="#004085")
    tree.tag_configure("ongoing", background="#fff8dc", foreground="#856404")
    tree.tag_configure("finished", background="#d4edda", foreground="#155724")

    def load_orders():
        for row in tree.get_children():
            tree.delete(row)

        selected_category = filter_var.get()

        c.execute("""
            SELECT id, name, description, notes, category, action_type, status FROM orders
            ORDER BY 
                CASE status
                    WHEN 'waiting' THEN 0
                    WHEN 'ongoing' THEN 1
                    WHEN 'finished' THEN 2
                    ELSE 3
                END,
                id DESC
        """)
        orders = c.fetchall()

        for order in orders:
            order_id, name, desc, notes, category, action_type, status = order

            c.execute(
                "SELECT action, timestamp FROM order_history WHERE order_id = ? ORDER BY id DESC LIMIT 1",
                (order_id,))
            hist = c.fetchone()

            last_hist = f"{hist[0]} @ {hist[1]}" if hist else ""

            if selected_category != "All" and category != selected_category:
                continue

            tag = status.lower()
            if tag not in ["waiting", "ongoing", "finished"]:
                tag = "ongoing"

            tree.insert("", tk.END, values=(
                order_id, name, desc, notes, category, action_type, status.capitalize(), last_hist), tags=(tag,))

    def add_order():
        # تحميل التصنيفات والإجراءات من الملفات
        categories = load_static_list(CATEGORIES_FILE) or []
        actions = load_static_list(ACTION_TYPES_FILE) or []

        def save_new():
            n = entry_name.get().strip()
            d = text_desc.get("1.0", tk.END).strip()
            cat = combo_category.get().strip()
            action_type = combo_action_type.get().strip()
            notes = text_notes.get("1.0", tk.END).strip()

            if not n or not cat or cat == "Choose Category" or not action_type or action_type == "Choose Action Type":
                messagebox.showerror("Error", "Please fill all fields and choose category and action type.")
                return

            # حفظ الطلب باستخدام اسم التصنيف مباشرة
            c.execute(
                "INSERT INTO orders (name, description, status, category, action_type, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (n, d, "waiting", cat, action_type, notes)
            )

            # إضافة السجل الزمني
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("SELECT last_insert_rowid()")
            order_id = c.fetchone()[0]
            c.execute("INSERT INTO order_history (order_id, action, timestamp) VALUES (?, ?, ?)",
                      (order_id, f"", now))

            conn.commit()
            load_orders()
            popup.destroy()

        # واجهة الإدخال
        popup = Toplevel(orders_win)
        popup.title("Add New Order")
        popup.geometry("400x450")
        popup.configure(bg=style.lookup("TFrame", "background") or "white")

        ttk.Label(popup, text="Category:").pack(padx=10, pady=5, anchor="w")
        combo_category = ttk.Combobox(popup, values=categories, state="readonly")
        combo_category.set("Choose Category")
        combo_category.pack(padx=10, pady=5)

        ttk.Label(popup, text="Action Type:").pack(padx=10, pady=5, anchor="w")
        combo_action_type = ttk.Combobox(popup, values=actions, state="readonly")
        combo_action_type.set("Choose Action Type")
        combo_action_type.pack(padx=10, pady=5)

        ttk.Label(popup, text="Name:").pack(padx=10, pady=5, anchor="w")
        entry_name = ttk.Entry(popup, width=40)
        entry_name.pack(padx=10, pady=5)

        ttk.Label(popup, text="Description:").pack(padx=10, pady=5, anchor="w")
        text_desc = tk.Text(popup, width=40, height=4)
        text_desc.pack(padx=10, pady=5)

        ttk.Label(popup, text="Notes:").pack(padx=10, pady=5, anchor="w")
        text_notes = tk.Text(popup, width=40, height=3)
        text_notes.pack(padx=10, pady=5)

        ttk.Button(popup, text="Save", command=save_new).pack(padx=10, pady=10)

    def edit_order():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No order selected.")
            return
        order_id = tree.item(selected[0])["values"][0]

        c.execute("""
            SELECT name, description, notes, category_id, action_type 
            FROM orders WHERE id=?
        """, (order_id,))
        order = c.fetchone()
        if not order:
            messagebox.showerror("Error", "Order not found.")
            return

        name, description, notes, category_id, action_type = order

        # Get category name from id
        c.execute("SELECT name FROM categories WHERE id=?", (category_id,))
        row = c.fetchone()
        category_name = row[0] if row else "Unknown"

        def save_edit():
            new_name = entry_name.get().strip()
            new_desc = text_desc.get("1.0", tk.END).strip()
            new_notes = text_notes.get("1.0", tk.END).strip()
            new_cat = combo_category.get().strip()
            new_action_type = combo_action_type.get().strip()

            if not new_name or not new_cat or new_cat == "Choose Category" or not new_action_type or new_action_type == "Choose Action Type":
                messagebox.showerror("Error", "Please fill all fields and choose category and action type.")
                return

            # Get category_id for the selected category
            c.execute("SELECT id FROM categories WHERE name=?", (new_cat,))
            row = c.fetchone()
            if not row:
                messagebox.showerror("Error", "Selected category not found in database.")
                return
            new_category_id = row[0]

            c.execute("""
                UPDATE orders SET name=?, description=?, notes=?, category_id=?, action_type=?
                WHERE id=?
            """, (new_name, new_desc, new_notes, new_category_id, new_action_type, order_id))

            conn.commit()
            load_orders()
            popup.destroy()

        popup = Toplevel(orders_win)
        popup.title("Edit Order")
        popup.geometry("900x750")
        popup.configure(bg=style.lookup("TFrame", "background") or "white")

        ttk.Label(popup, text="Category:").pack(padx=10, pady=5, anchor="w")
        combo_category = ttk.Combobox(popup, values=ORDER_CATEGORIES, state="readonly")
        combo_category.set(category_name)
        combo_category.pack(padx=10, pady=5)

        ttk.Label(popup, text="Action Type:").pack(padx=10, pady=5, anchor="w")
        combo_action_type = ttk.Combobox(popup, values=ORDER_ACTION_TYPES, state="readonly")
        combo_action_type.set(action_type)
        combo_action_type.pack(padx=10, pady=5)

        ttk.Label(popup, text="Name:").pack(padx=10, pady=5, anchor="w")
        entry_name = ttk.Entry(popup, width=40)
        entry_name.pack(padx=10, pady=5)
        entry_name.insert(0, name)

        ttk.Label(popup, text="Description:").pack(padx=10, pady=5, anchor="w")
        text_desc = tk.Text(popup, width=40, height=4)
        text_desc.pack(padx=10, pady=5)
        text_desc.insert("1.0", description)

        ttk.Label(popup, text="Notes:").pack(padx=10, pady=5, anchor="w")
        text_notes = tk.Text(popup, width=40, height=3)
        text_notes.pack(padx=10, pady=5)
        text_notes.insert("1.0", notes)

        ttk.Button(popup, text="Save", command=save_edit).pack(padx=10, pady=10)

    def delete_order():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No order selected.")
            return
        order_id = tree.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this order?")
        if confirm:
            c.execute("DELETE FROM orders WHERE id=?", (order_id,))
            c.execute("DELETE FROM order_finish_info WHERE order_id=?", (order_id,))
            conn.commit()
            load_orders()

    def finish_order():
        global conn, c  # تأكد أن الاتصال متاح
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No order selected.")
            return

        order_id = tree.item(selected[0])["values"][0]

        c.execute("SELECT status FROM orders WHERE id=?", (order_id,))
        current_status_row = c.fetchone()
        if not current_status_row:
            messagebox.showerror("Error", "Order not found.")
            return

        current_status = current_status_row[0]

        if current_status == "waiting":
            new_status = "ongoing"
            c.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO order_history (order_id, action, timestamp) VALUES (?, ?, ?)",
                      (order_id, "Order Started (ongoing)", now))
            conn.commit()
            load_orders()



        elif current_status == "ongoing":

            # تأكد أن جدول order_finish_info موجود

            c.execute("""

            CREATE TABLE IF NOT EXISTS order_finish_info (

                order_id INTEGER PRIMARY KEY,

                leader TEXT,

                workers TEXT,

                ratings TEXT

            )

            """)

            conn.commit()

            # نافذة إنهاء الطلب

            finish_win = Toplevel(orders_win)

            finish_win.title("Finish Order")

            finish_win.geometry("800x600")

            finish_win.configure(bg=style.lookup("TFrame", "background") or "white")

            ttk.Label(finish_win, text="Select Leader:", font=("Segoe UI", 12)).pack(pady=10)

            combo_leader = ttk.Combobox(finish_win, values=LEADERS, state="readonly")

            combo_leader.pack(pady=5)

            ttk.Label(finish_win, text="Select Workers and Rate:", font=("Segoe UI", 12)).pack(pady=10)

            workers_vars = []

            ratings_vars = []

            workers_frame = ttk.Frame(finish_win)

            workers_frame.pack(pady=5)

            for worker in WORKERS:
                row = ttk.Frame(workers_frame)

                row.pack(anchor="w", pady=2)

                var = tk.BooleanVar()

                chk = ttk.Checkbutton(row, text=worker, variable=var)

                chk.pack(side=tk.LEFT)

                rating = ttk.Combobox(row, values=[1, 2, 3, 4, 5], width=3, state="readonly")

                rating.set(5)

                rating.pack(side=tk.LEFT, padx=10)

                workers_vars.append((var, worker))

                ratings_vars.append((worker, rating))

            def save_finish():

                leader = combo_leader.get()

                selected_workers = [w for (v, w) in workers_vars if v.get()]

                if not leader:
                    messagebox.showerror("Error", "Please select a leader.")

                    return

                if not selected_workers:
                    messagebox.showerror("Error", "Please select at least one worker.")

                    return

                # جمع التقييمات فقط للعمال المحددين

                ratings = {}

                for worker, rating_cb in ratings_vars:

                    if worker in selected_workers:

                        try:

                            ratings[worker] = int(rating_cb.get())

                        except ValueError:

                            ratings[worker] = 5  # تقييم افتراضي

                # تحديث الطلب

                c.execute("UPDATE orders SET status='finished' WHERE id=?", (order_id,))

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                c.execute("INSERT INTO order_history (order_id, action, timestamp) VALUES (?, ?, ?)",

                          (order_id, f"Order Finished by {leader}", now))

                c.execute("""

                    INSERT OR REPLACE INTO order_finish_info (order_id, leader, workers, ratings)

                    VALUES (?, ?, ?, ?)

                """, (order_id, leader, ", ".join(selected_workers), json.dumps(ratings)))

                conn.commit()

                load_orders()





            ttk.Button(finish_win, text="Finish Order", command=save_finish).pack(pady=20)


        elif current_status == "finished":
            messagebox.showinfo("Info", "Order is already finished.").showinfo("Info", "Order is already finished.")

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X)

    ttk.Button(btn_frame, text="Manage People", command=manage_people_window).pack(side=tk.RIGHT, padx=5, pady=5)
    ttk.Button(btn_frame, text="Manage Categories", command=manage_categories_window).pack(side=tk.RIGHT, padx=5,
                                                                                           pady=5)
    ttk.Button(btn_frame, text="Manage Actions", command=manage_action_types_window).pack(side=tk.RIGHT, padx=5, pady=5)
    ttk.Button(btn_frame, text="Reset Orders", command=reset_orders).pack(side=tk.RIGHT, padx=5, pady=5)
    ttk.Button(btn_frame, text="Add Order", command=add_order, style="success.TButton").pack(side=tk.LEFT, padx=5, pady=5)
    ttk.Button(btn_frame, text="Edit Selected", command=edit_order, style="warning.TButton").pack(side=tk.LEFT, padx=5, pady=5)
    ttk.Button(btn_frame, text="Delete Selected", command=delete_order, style="danger.TButton").pack(side=tk.LEFT, padx=5, pady=5)
    ttk.Button(btn_frame, text="Mark as Finished", command=finish_order, style="info.TButton").pack(side=tk.LEFT, padx=5, pady=5)

    load_orders()

def manage_people_window():
    people_win = tk.Toplevel()
    people_win.title("mangement")
    people_win.geometry("700x600")
    people_win.configure(bg=style.colors.bg)

    # --- الإدخالات ---
    ttk.Label(people_win, text="adding new leader:").pack(pady=(10, 2))
    leader_entry = ttk.Entry(people_win)
    leader_entry.pack(pady=2)

    ttk.Button(people_win, text="add leader", bootstyle="success", command=lambda: add_to_list(leader_entry, listbox_leaders, "leaders.txt")).pack(pady=5)

    ttk.Label(people_win, text="adding new worker:").pack(pady=(20, 2))
    worker_entry = ttk.Entry(people_win)
    worker_entry.pack(pady=2)

    ttk.Button(people_win, text="add worker", bootstyle="success", command=lambda: add_to_list(worker_entry, listbox_workers, "workers.txt")).pack(pady=5)

    # --- عرض القوائم ---
    frame_lists = ttk.Frame(people_win)
    frame_lists.pack(fill="both", expand=True, padx=10, pady=10)

    listbox_leaders = tk.Listbox(frame_lists, height=8)
    listbox_leaders.grid(row=0, column=0, sticky="nsew", padx=5)
    ttk.Button(frame_lists, text="delete selected leader", bootstyle="danger", command=lambda: delete_selected(listbox_leaders, "leaders.txt")).grid(row=1, column=0, pady=5)

    listbox_workers = tk.Listbox(frame_lists, height=8)
    listbox_workers.grid(row=0, column=1, sticky="nsew", padx=5)
    ttk.Button(frame_lists, text="delete selected worker", bootstyle="danger", command=lambda: delete_selected(listbox_workers, "workers.txt")).grid(row=1, column=1, pady=5)

    frame_lists.columnconfigure(0, weight=1)
    frame_lists.columnconfigure(1, weight=1)

    # تحميل البيانات الحالية
    load_list_to_listbox("leaders.txt", listbox_leaders)
    load_list_to_listbox("workers.txt", listbox_workers)

# --- توابع المساعدة ---
def add_to_list(entry_widget, listbox, filename):
    name = entry_widget.get().strip()
    if name:
        listbox.insert(tk.END, name)
        save_listbox_to_file(listbox, filename)
        entry_widget.delete(0, tk.END)

def delete_selected(listbox, filename):
    selected = listbox.curselection()
    if selected:
        listbox.delete(selected[0])
        save_listbox_to_file(listbox, filename)

def save_listbox_to_file(listbox, filename):
    items = listbox.get(0, tk.END)
    with open(filename, "w", encoding="utf-8") as f:
        for item in items:
            f.write(item + "\n")

def load_list_to_listbox(filename, listbox):
    listbox.delete(0, tk.END)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                listbox.insert(tk.END, line.strip())



def add_category():
    name = entry_new_category.get().strip()
    img_path = image_path_var_category.get().strip()
    if not name:
        messagebox.showerror("Error", "Category name cannot be empty.")
        return
    if not img_path or not os.path.exists(img_path):
        img_path = "default_category.png"
    try:
        c.execute("INSERT INTO categories (name, image_path) VALUES (?, ?)", (name, img_path))
        conn.commit()
        load_categories_into_combo()
        entry_new_category.delete(0, tk.END)
        image_path_var_category.set("")
        display_category_cards()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Category already exists.")

def update_category():
    global selected_category_id
    if selected_category_id is None:
        messagebox.showerror("Error", "Please select a category first.")
        return

    new_name = entry_new_category.get().strip()
    new_img_path = image_path_var_category.get().strip()

    if not new_name:
        messagebox.showerror("Error", "Category name cannot be empty.")
        return

    try:
        c.execute(
            "UPDATE categories SET name=?, image_path=? WHERE id=?",
            (new_name, new_img_path, selected_category_id)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Category name must be unique.")
        return
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update category:\n{e}")
        return

    messagebox.showinfo("Success", "Category updated successfully.")

    # تحديث عرض التصنيفات والاختيارات
    load_categories_into_combo()
    display_category_cards()

    # تنظيف الحقول
    clear_category_form()

    # إلغاء تحديد التصنيف
    selected_category_id = None

    # افتح نافذة تعديل أو عدل الحقول حسب selected_category_id
def clear_category_form():
    entry_new_category.delete(0, tk.END)
    image_path_var_category.set("")

def delete_category():
    global selected_category_id
    if selected_category_id is None:
        messagebox.showerror("خطأ", "يرجى اختيار تصنيف أولاً.")
        return
    confirm = messagebox.askyesno(title='WARINING',message="make sure that there is no machines in this category")
    if confirm:
        c.execute("DELETE FROM categories WHERE id=?", (selected_category_id,))
        conn.commit()
        selected_category_id = None
        display_category_cards()


        # حدث قائمة التصنيفات وأي مكان آخر

def clear_category_form():
    global selected_category_id
    selected_category_id = None
    entry_new_category.delete(0, tk.END)
    image_path_var_category.set("")

def refresh_categories():
    load_categories_into_combo(combo_category)
    display_category_cards(inner_frame, combo_category)



def add_machine():
    machine_id = entry_id.get().strip()
    name = entry_name.get().strip()
    location = entry_location.get().strip()
    category_name = combo_category.get().strip()
    purchase = entry_purchase.get().strip()
    last = entry_last.get().strip()
    interval = entry_interval.get().strip()
    image_path = image_path_var.get().strip()

    if not all([machine_id, name, location, category_name, last, interval]):
        messagebox.showerror("Missing Info", "Please fill all fields.")
        return

    # التحقق من أن الفاصل الزمني رقم
    try:
        interval = int(interval)
    except ValueError:
        messagebox.showerror("Invalid Input", "Interval must be a number.")
        return

    # التحقق من أن تاريخ آخر صيانة ليس في المستقبل
    try:
        last_date = datetime.strptime(last, "%Y-%m-%d").date()
        today = datetime.today().date()
        if last_date > today:
            messagebox.showerror("Invalid Date", "Last maintenance date cannot be in the future.")
            return
    except ValueError:
        messagebox.showerror("Invalid Date", "Date format should be YYYY-MM-DD.")
        return

    # التأكد من أن التصنيف موجود
    c.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    result = c.fetchone()
    if not result:
        messagebox.showerror("Error", "Category not found.")
        return
    cat_id = result[0]

    # إضافة الماكينة إلى القاعدة
    try:
        c.execute('''
        INSERT INTO machines (id, name, location, category_id, purchase_date, last_maintenance, maintenance_interval_days, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (machine_id, name, location, cat_id, purchase, last, interval, image_path))
        conn.commit()
        clear_form()
        display_category_cards()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Machine ID '{machine_id}' already exists.")

def update_machine():
    global selected_machine_id
    if not selected_machine_id:
        messagebox.showerror("Error", "No machine selected.")
        return

    name = entry_name.get().strip()
    location = entry_location.get().strip()
    category_name = combo_category.get().strip()
    purchase = entry_purchase.get().strip()
    last = entry_last.get().strip()
    interval = entry_interval.get().strip()
    image_path = image_path_var.get().strip()

    if not all([name, location, category_name, purchase, last, interval]):
        messagebox.showerror("Missing Info", "Please fill all fields.")
        return

    try:
        interval = int(interval)
    except ValueError:
        messagebox.showerror("Invalid Input", "Interval must be a number.")
        return

    c.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    result = c.fetchone()
    if not result:
        messagebox.showerror("Error", "Category not found.")
        return
    cat_id = result[0]

    c.execute('''
    UPDATE machines SET name=?, location=?, category_id=?, purchase_date=?, last_maintenance=?, maintenance_interval_days=?, image_path=?
    WHERE id=?
    ''', (name, location, cat_id, purchase, last, interval, image_path, selected_machine_id))
    conn.commit()
    clear_form()
    display_category_cards()
    messagebox.showinfo("Success", "Machine updated successfully.")
    selected_machine_id = None
    update_button.pack_forget()
    delete_button.pack_forget()

def delete_machine():
    global selected_machine_id
    if not selected_machine_id:
        messagebox.showerror("Error", "No machine selected.")
        return
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this machine?")
    if confirm:
        c.execute("DELETE FROM machines WHERE id=?", (selected_machine_id,))
        conn.commit()
        clear_form()
        display_category_cards()
        selected_machine_id = None
        update_button.pack_forget()
        delete_button.pack_forget()

def select_machine(machine_id):
    global selected_machine_id
    selected_machine_id = machine_id
    c.execute("SELECT id, name, location, category_id, purchase_date, last_maintenance, maintenance_interval_days, image_path FROM machines WHERE id=?", (machine_id,))
    machine = c.fetchone()
    if not machine:
        return
    mid, name, location, cat_id, purchase, last, interval, image_path = machine

    entry_id.config(state=tk.DISABLED)
    entry_id.delete(0, tk.END)
    entry_id.insert(0, mid)
    entry_name.delete(0, tk.END)
    entry_name.insert(0, name)
    entry_location.delete(0, tk.END)
    entry_location.insert(0, location)

    c.execute("SELECT name FROM categories WHERE id=?", (cat_id,))
    cat_name = c.fetchone()
    if cat_name:
        combo_category.set(cat_name[0])
    else:
        combo_category.set("")

    entry_purchase.delete(0, tk.END)
    entry_purchase.insert(0, purchase)
    entry_last.delete(0, tk.END)
    entry_last.insert(0, last)
    entry_interval.delete(0, tk.END)
    entry_interval.insert(0, interval)

    days_left = calculate_days_left(last, interval)
    days_left_label.config(text=f"Days Left: {days_left}")

    image_path_var.set(image_path if image_path else "")

    update_button.pack(pady=5)
    delete_button.pack(pady=5)

# --------- النافذة المنبثقة لتفاصيل الآلة ---------
def open_machine_popup():
    if not selected_machine_id:
        messagebox.showerror("Error", "No machine selected.")
        return

    popup = Toplevel(app)
    popup.title("Machine Details & Maintenance History")
    popup.geometry("600x500")
    popup.configure(bg=style.colors.bg)

    # عرض تفاصيل الماكينة في الأعلى
    c.execute("SELECT * FROM machines WHERE id=?", (selected_machine_id,))
    machine = c.fetchone()
    if not machine:
        messagebox.showerror("Error", "Machine not found.")
        popup.destroy()
        return

    labels = ["ID", "Name", "Location", "Category ID", "Purchase Date", "Last Maintenance", "Interval Days", "Image Path"]
    for i, label in enumerate(labels):
        tk.Label(popup, text=label + ":", bg=style.colors.bg, fg="white", font=("Helvetica", 10, "bold")).grid(row=i, column=0, sticky="w", padx=10, pady=3)
        tk.Label(popup, text=machine[i], bg=style.colors.bg, fg="white", font=("Helvetica", 10)).grid(row=i, column=1, sticky="w", padx=10, pady=3)

    # قسم سجل الصيانة (History)
    tk.Label(popup, text="Maintenance History:", bg=style.colors.bg, fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=2, sticky="w", padx=10, pady=3, rowspan=1)

    listbox_history = tk.Listbox(popup, width=40, height=15, font=("Helvetica", 10))
    listbox_history.grid(row=1, column=2, rowspan=6, padx=10, pady=5, sticky="nsew")

    scrollbar_history = tk.Scrollbar(popup, orient="vertical", command=listbox_history.yview)
    scrollbar_history.grid(row=1, column=3, rowspan=6, sticky="ns", pady=5)
    listbox_history.config(yscrollcommand=scrollbar_history.set)

    # إدخالات سجل الصيانة الجديد
    tk.Label(popup, text="Your Name:", bg=style.colors.bg, fg="white").grid(row=7, column=2, sticky="w", padx=10, pady=2)
    entry_user_popup = Entry(popup)
    entry_user_popup.grid(row=8, column=2, sticky="ew", padx=10)

    tk.Label(popup, text="Date (YYYY-MM-DD):", bg=style.colors.bg, fg="white").grid(row=9, column=2, sticky="w", padx=10, pady=2)
    entry_date_popup = Entry(popup)
    entry_date_popup.grid(row=10, column=2, sticky="ew", padx=10)
    entry_date_popup.insert(0, datetime.now().strftime("%Y-%m-%d"))

    tk.Label(popup, text="Details:", bg=style.colors.bg, fg="white").grid(row=11, column=2, sticky="w", padx=10, pady=2)
    text_details_popup = tk.Text(popup, height=5, width=30)
    text_details_popup.grid(row=12, column=2, padx=10, pady=5)

    def add_history_popup():
        user = entry_user_popup.get().strip()
        date_str = entry_date_popup.get().strip()
        details = text_details_popup.get("1.0", tk.END).strip()

        if not user or not date_str or not details:
            messagebox.showerror("Error", "Please fill all history fields.")
            return
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return

        c.execute("INSERT INTO history (machine_id, entry, timestamp, user) VALUES (?, ?, ?, ?)",
                  (selected_machine_id, details, date_str, user))
        conn.commit()
        messagebox.showinfo("Success", "History record added.")
        text_details_popup.delete("1.0", tk.END)
        load_history_popup()

    def load_history_popup():
        listbox_history.delete(0, tk.END)
        c.execute("SELECT timestamp, user, entry FROM history WHERE machine_id=? ORDER BY timestamp DESC", (selected_machine_id,))
        rows = c.fetchall()
        if not rows:
            listbox_history.insert(tk.END, "No history records yet.")
            return
        for ts, usr, ent in rows:
            entry_str = f"[{ts}] by {usr}: {ent[:40]}{'...' if len(ent)>40 else ''}"
            listbox_history.insert(tk.END, entry_str)

    btn_add_history = ttkButton(popup, text="Add History Record", command=add_history_popup, bootstyle=SUCCESS)
    btn_add_history.grid(row=13, column=2, pady=10)

    # جعل الأعمدة والصفوف قابلة للتمدد (لتحسين المظهر)
    popup.grid_columnconfigure(2, weight=1)
    popup.grid_rowconfigure(1, weight=1)

    load_history_popup()

def open_alarms_window():
    alarm_win = Toplevel(app)
    alarm_win.title("Maintenance Alarms")
    alarm_win.geometry("700x500")
    alarm_win.configure(bg=style.colors.bg)

    ttk.Label(alarm_win, text="Upcoming & Overdue Maintenances", font=("Helvetica", 18, "bold"), bootstyle="danger").pack(pady=10)

    frame = ttk.Frame(alarm_win)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    canvas = tk.Canvas(frame, bg=style.colors.bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        # ويندوز وماك
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            # لينكس (Button-4 = scroll up, Button-5 = scroll down)
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

    # ربط حدث الماوس بالعجلة على الـ canvas
    canvas.bind_all("<MouseWheel>", _on_mousewheel)  # ويندوز وماك
    canvas.bind_all("<Button-4>", _on_mousewheel)  # لينكس scroll up
    canvas.bind_all("<Button-5>", _on_mousewheel)  # لينكس scroll down

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    c.execute("SELECT id, name, last_maintenance, maintenance_interval_days FROM machines")
    all_machines = c.fetchall()

    alarms = []
    for mid, name, last, interval in all_machines:
        try:
            last_date = datetime.strptime(last, "%Y-%m-%d")
            next_due = last_date + timedelta(days=interval)
            days_left = (next_due - datetime.now()).days

            if days_left <= 7:
                alarms.append((mid, name, days_left))
        except Exception as e:
            print("Error in alarm calc:", e)

    if not alarms:
        ttk.Label(scroll_frame, text="🎉 No upcoming or overdue maintenances!", font=("Helvetica", 14), bootstyle="success").pack(pady=30)
        return

    for mid, name, days_left in alarms:
        status = "OVERDUE" if days_left < 0 else f"{days_left} day(s) left"
        color = "danger" if days_left < 0 else "warning"
        text = f"{name} (ID: {mid}) - {status}"
        ttk.Label(scroll_frame, text=text, font=("Helvetica", 12), bootstyle=color).pack(anchor="w", pady=4)

# --------- البحث ---------
def search_machines(event=None):
    query = search_var.get().strip()
    if not query:
        # لو البحث فاضي، نعرض الكل ونخفي زر الرجوع
        display_category_cards()
        btn_back_to_categories.pack_forget()
        return

    c.execute("SELECT id, name, last_maintenance, maintenance_interval_days, image_path FROM machines WHERE id LIKE ? OR name LIKE ?", (f'%{query}%', f'%{query}%'))
    results = c.fetchall()

    for widget in inner_frame.winfo_children():
        widget.destroy()

    if not results:
        no_label = tk.Label(inner_frame, text="No machines found.", fg="white", bg=style.colors.bg, font=("Helvetica", 20))
        no_label.pack(pady=30)
    else:
        # عرض نتائج البحث هنا (حسب كودك)
        for i, (mid, name, last, interval, path) in enumerate(results):
            days_left = calculate_days_left(last, interval)
            frame = tk.Frame(inner_frame, bg=style.colors.bg, bd=1, relief=tk.SOLID)
            frame.pack(fill=tk.X, padx=10, pady=5)
            frame.columnconfigure(1, weight=1)

            img_label = tk.Label(frame, bg=style.colors.bg)
            img_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5)

            if path and os.path.exists(path):
                try:
                    pil_img = Image.open(path).resize((60, 60))
                    img = ImageTk.PhotoImage(pil_img)
                    image_refs[mid] = img
                    img_label.config(image=img)
                except:
                    img_label.config(text="Img Err", fg="red", font=("Helvetica", 8))
            else:
                img_label.config(text="No Img", fg="gray", font=("Helvetica", 8, "italic"))

            tk.Label(frame, text=name, bg=style.colors.bg, fg="white", font=("Helvetica", 14, "bold")).grid(row=0, column=1, sticky="w")
            tk.Label(frame, text=f"ID: {mid}  |  Days Left: {days_left}", bg=style.colors.bg, fg="lightgray", font=("Helvetica", 12)).grid(row=1, column=1, sticky="w")

            frame.bind("<Button-1>", lambda e, m=mid: select_machine(m))
            img_label.bind("<Button-1>", lambda e, m=mid: select_machine(m))

            frame.bind("<Double-Button-1>", lambda e, m=mid: (select_machine(m), open_machine_popup()))
            img_label.bind("<Double-Button-1>", lambda e, m=mid: (select_machine(m), open_machine_popup()))

    btn_back_to_categories.pack(pady=5)  # اظهار الزر بعد البحث
def back_to_categories():
    search_var.set("")  # يمسح البحث
    display_category_cards()  # يعرض كل التصنيفات
    btn_back_to_categories.pack_forget()  # يخفي الزر


# --------- استجابة عند الضغط في خلفية اليمين ---------
def on_canvas_click(event):
    clear_form()
    global selected_machine_id
    selected_machine_id = None
    update_button.pack_forget()
    delete_button.pack_forget()

## --------- واجهة المستخدم محسنة ---------

style = Style("darkly")
app = style.master
app.title("Factory Maintenance Tracker")
app.geometry("1200x720")
app.minsize(1000, 600)

image_refs = {}  # لمنع حذف الصور من الذاكرة
selected_machine_id = None

def calculate_days_left(last_maintenance, interval_days):
    try:
        last_date = datetime.strptime(last_maintenance, "%Y-%m-%d").date()
        today = datetime.today().date()

        # تحقق إن التاريخ ليس في المستقبل
        if last_date > today:
            return "please choose a valid date"

        next_maintenance = last_date + timedelta(days=interval_days)
        delta = next_maintenance - today
        return max(delta.days, 0)
    except:
        return "N/A"


def clear_form():
    entry_id.config(state=tk.NORMAL)
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_location.delete(0, tk.END)
    combo_category.set("")
    entry_purchase.delete(0, tk.END)
    entry_last.delete(0, tk.END)
    entry_interval.delete(0, tk.END)
    days_left_label.config(text="Days Left: N/A")
    image_path_var.set("")
    update_button.pack_forget()
    delete_button.pack_forget()


def browse_image():
    path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All files", "*.*")
        ]
    )
    if path:
        image_path_var.set(path)
def add_labeled_entry(parent, text, **kwargs):
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.X, pady=6)
    lbl = Label(frame, text=text, width=24, anchor="w", font=("Segoe UI", 12, "bold"))
    lbl.pack(side=tk.LEFT)
    ent = Entry(frame, font=("Segoe UI", 12), **kwargs)
    ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
    return ent

# === التصميم الرئيسي ===
main_frame = ttk.Frame(app, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# زر لفتح نافذة الإنذارات
top_controls_frame = ttk.Frame(main_frame)
top_controls_frame.pack(fill=tk.X, pady=(0, 10))

ttk.Button(top_controls_frame, text="🔔 Show Alarms", command=open_alarms_window, bootstyle="danger").pack(side=tk.RIGHT, padx=5)

ttk.Button(top_controls_frame, text="Manage Orders", command=open_orders_window).pack(side=tk.RIGHT, padx=5)

# إعداد شبكة 2 عمود مع توازن جيد للمساحات
main_frame.columnconfigure(0, weight=1, uniform="col")
main_frame.columnconfigure(1, weight=2, uniform="col")
main_frame.rowconfigure(0, weight=1)

# === الشريط الجانبي الأيسر (نموذج الإدخال + بحث + إضافة تصنيف) ===
left_frame = ttk.Frame(main_frame, bootstyle="secondary", padding=15, borderwidth=2, relief="ridge")
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,15))

# Scrollable canvas داخل اليسار
canvas_left = tk.Canvas(left_frame, bg=style.colors.bg, highlightthickness=0)
scrollbar_left = ttk.Scrollbar(left_frame, orient="vertical", command=canvas_left.yview)
scrollable_left = ttk.Frame(canvas_left)

scrollable_left.bind(
    "<Configure>",
    lambda e: canvas_left.configure(scrollregion=canvas_left.bbox("all"))
)

canvas_left.create_window((0,0), window=scrollable_left, anchor="nw")
canvas_left.configure(yscrollcommand=scrollbar_left.set)

canvas_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar_left.pack(side=tk.RIGHT, fill=tk.Y)

# --- عنوان ---
Label(scrollable_left, text="Factory Maintenance", font=("Segoe UI", 22, "bold"), foreground=style.colors.info).pack(pady=15)

# --- حقل البحث ---
search_var = tk.StringVar()
search_frame = ttk.Labelframe(scrollable_left, text="Search Machine", bootstyle="info", padding=10)
search_frame.pack(fill=tk.X, pady=12)
btn_back_to_categories = ttk.Button(search_frame, text="back to category", command=lambda: back_to_categories())
btn_back_to_categories.pack(pady=5)
btn_back_to_categories.pack_forget()  # يخفيه بالبداية


search_entry = Entry(search_frame, textvariable=search_var, font=("Segoe UI", 14))
search_entry.pack(fill=tk.X, padx=5, pady=5)
search_entry.bind("<KeyRelease>", search_machines) # اربط هنا البحث الخاص بك

# --- نموذج بيانات الماكينة ---
form_frame = ttk.Labelframe(scrollable_left, text="Machine Details", padding=15, bootstyle="secondary")
form_frame.pack(fill=tk.BOTH, pady=10)

entry_id = add_labeled_entry(form_frame, "Machine ID (Serial):")
entry_name = add_labeled_entry(form_frame, "Machine Name:")
entry_location = add_labeled_entry(form_frame, "Location:")

Label(form_frame, text="Category:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(12, 3))
combo_category = Combobox(form_frame, font=("Segoe UI", 13), state="readonly")
combo_category.pack(fill=tk.X, pady=4)

entry_purchase = add_labeled_entry(form_frame, "Purchase Date (YYYY-MM-DD):")
entry_last = add_labeled_entry(form_frame, "Last Maintenance (YYYY-MM-DD):")
entry_interval = add_labeled_entry(form_frame, "Maintenance Interval (days):")

days_left_label = Label(form_frame, text="Days Left: N/A", font=("Segoe UI", 14, "bold"), foreground=style.colors.warning)
days_left_label.pack(anchor="w", pady=8)

# مسار الصورة مع زر تصفح
img_frame = ttk.Frame(form_frame)
img_frame.pack(fill=tk.X, pady=6)
image_path_var = tk.StringVar()
img_entry = Entry(img_frame, textvariable=image_path_var, font=("Segoe UI", 12))
img_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
btn_browse_img = Button(img_frame, text="Browse Image", command=browse_image, bootstyle="secondary")
btn_browse_img.pack(side=tk.RIGHT, padx=5)

# أزرار الإجراءات
actions_frame = ttk.Frame(scrollable_left)
actions_frame.pack(fill=tk.X, pady=15)

add_button = Button(actions_frame, text="Add Machine", bootstyle="success", command=add_machine)

add_button.pack(fill=tk.X, pady=5)

update_button = Button(actions_frame, text="Update Machine", bootstyle="warning", command=update_machine)

delete_button = Button(actions_frame, text="Delete Machine", bootstyle="danger",command=delete_machine)
ttk.Button(scrollable_left, text="Show Alarms", command=open_alarms_window, bootstyle="danger").pack(fill=tk.X, pady=5)


update_button.pack_forget()
delete_button.pack_forget()

# --- إضافة تصنيف جديد ---
category_frame = ttk.Labelframe(scrollable_left, text="Add New Category", padding=15, bootstyle="info")
category_frame.pack(fill=tk.BOTH, pady=15)

entry_new_category = Entry(category_frame, font=("Segoe UI", 14))
entry_new_category.pack(fill=tk.X, pady=(0,8))

img_cat_frame = ttk.Frame(category_frame)
img_cat_frame.pack(fill=tk.X)

image_path_var_category = tk.StringVar()
entry_new_cat_image = Entry(img_cat_frame, textvariable=image_path_var_category, font=("Segoe UI", 14))
entry_new_cat_image.pack(side=tk.LEFT, fill=tk.X, expand=True)


btn_browse_cat = Button(
    img_cat_frame,
    text="Browse Category Image",
    command=browse_category_image,
    bootstyle="secondary"
)
btn_browse_cat.pack(side=tk.RIGHT, padx=5)

btn_add_category = Button(category_frame, text="Add Category", bootstyle="info", command=add_category)
btn_update_category = Button(category_frame, text="Update Category", bootstyle="warning", command=update_category)
btn_delete_category = Button(category_frame, text="Delete Category", bootstyle="danger", command=delete_category)

btn_update_category.pack(fill=tk.X, pady=5)
btn_delete_category.pack(fill=tk.X, pady=5)
btn_add_category.pack(fill=tk.X, pady=8)

# === الجهة اليمنى: عرض التصنيفات والآلات كـ "كروت" جميلة مع Scroll ===
right_frame = ttk.Frame(main_frame, bootstyle="secondary", padding=15, borderwidth=2, relief="ridge")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


Label(right_frame, text="Categories & Machines", font=("Segoe UI", 20, "bold"), foreground=style.colors.primary).pack(pady=12)

canvas_frame = ttk.Frame(right_frame)
canvas_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(canvas_frame, bg=style.colors.bg, highlightthickness=0)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

inner_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=inner_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

inner_frame.bind("<Configure>", on_frame_configure)

def on_canvas_click(event):
    clear_form()

canvas.bind("<Button-1>", on_canvas_click)

# --- إضافة تأثير hover على الأزرار لتحسين UX ---
for btn in [add_button, update_button, delete_button, btn_browse_img, btn_browse_cat, btn_add_category]:
    btn.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
    btn.bind("<Leave>", lambda e: e.widget.config(cursor=""))
load_categories_into_combo()
display_category_cards()

app.withdraw()  # إخفاء التطبيق مؤقتًا
show_login_window()


app.mainloop()
