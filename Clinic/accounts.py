import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

ACCENT_CASH = "#2e7d32"   # green
ACCENT_BANK = "#1565c0"   # blue
INACTIVE_BG = "#e0e0e0"
INACTIVE_FG = "#616161"

DEFAULT_BANKS = [
    "State Bank of India",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Punjab National Bank",
    "Bank of Baroda",
    "Canara Bank",
    "Union Bank of India",
    "Bank of India",
    "IndusInd Bank"
]

DEFAULT_AC_HEADS = [
    "Doctor Fees",
    "Laboratory Expense",
    "Material / Dental Supplies",
    "Rent & Facilities",
    "Salary & Wages",
    "Electricity / Utilities",
    "Equipment Purchase/Maintenance",
    "Office & Administrative",
    "Miscellaneous Expense"
]

def get_db_connection(app=None):
    """Return a SQLite connection to the dental.db database."""
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = getattr(app, "script_dir", os.path.dirname(os.path.abspath(__file__)))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))

def init_db(app=None):
    """Initialize database tables and seed default data if empty."""
    conn = get_db_connection(app)
    cursor = conn.cursor()

    # Receipts & Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            CHS_NO TEXT NOT NULL,
            DATE TEXT NOT NULL,
            PAID_TO TEXT,
            ADDRESS TEXT,
            Narration TEXT,
            A_C_HEAD TEXT,
            AMOUNT REAL NOT NULL
        )
    ''')

    # Account Heads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Heads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            head_name TEXT UNIQUE NOT NULL,
            head_type TEXT NOT NULL
        )
    ''')

    # Bank Master table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Banks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_code TEXT,
            bank_name TEXT UNIQUE NOT NULL,
            branch_name TEXT,
            ifsc_code TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')

    # Journal Entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voucher_no TEXT NOT NULL,
            date TEXT NOT NULL,
            debit_head TEXT NOT NULL,
            credit_head TEXT NOT NULL,
            narration TEXT,
            amount REAL NOT NULL
        )
    ''')

    # Seed default Account Heads if table is empty
    cursor.execute("SELECT COUNT(*) FROM Heads")
    if cursor.fetchone()[0] == 0:
        for head in DEFAULT_AC_HEADS:
            htype = "Income" if "Fees" in head else "Expense"
            cursor.execute("INSERT OR IGNORE INTO Heads (head_name, head_type) VALUES (?, ?)", (head, htype))

    # Seed default Banks if table is empty
    cursor.execute("SELECT COUNT(*) FROM Banks")
    if cursor.fetchone()[0] == 0:
        for idx, bank in enumerate(DEFAULT_BANKS, 1):
            bcode = f"BNK{idx:03d}"
            cursor.execute(
                "INSERT OR IGNORE INTO Banks (bank_code, bank_name, branch_name, ifsc_code, balance) VALUES (?, ?, ?, ?, ?)",
                (bcode, bank, "Main Branch", "SBIN0000000", 0.0)
            )

    conn.commit()
    conn.close()


class Accounts:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.script_dir = getattr(app, "script_dir", os.path.dirname(os.path.abspath(__file__)))
        self.receipt_account_type = tk.StringVar(value="CASH")
        self.payment_account_type = tk.StringVar(value="CASH")
        
        # Ensure database is initialized
        init_db(app)

        # Clear existing workspace
        app.clear_workspace()
        app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        col_buttons = [
            ("Receipts", self.receipts),
            ("Payments", self.payments),
            ("Journal", self.journal),
            ("Deposit", self.deposit),
            ("Withdrawal", self.withdrawal),
            ("Add A/C Head", self.head),
            ("Bank Master", self.bank_list)
        ]

        y_offset = 200
        x_offset = 40

        for i, (text, command) in enumerate(col_buttons):
            btn = tk.Button(app.workspace, text=text, font=('Arial', 11), width=20, command=command)
            btn.place(x=x_offset, y=y_offset + i * 35)

    def get_ac_heads(self):
        """Fetch account heads from DB or fallback to defaults."""
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT head_name FROM Heads ORDER BY head_name")
            rows = cursor.fetchall()
            conn.close()
            if rows:
                return [r[0] for r in rows]
        except Exception:
            pass
        return DEFAULT_AC_HEADS

    def get_banks(self):
        """Fetch bank names from DB or fallback to defaults."""
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT bank_name FROM Banks ORDER BY bank_name")
            rows = cursor.fetchall()
            conn.close()
            if rows:
                return [r[0] for r in rows]
        except Exception:
            pass
        return DEFAULT_BANKS

    def get_next_chs_no(self, mode):
        """Generate auto-incremented voucher/document number."""
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            if mode.startswith("JRN"):
                cursor.execute("SELECT voucher_no FROM Journal WHERE voucher_no LIKE 'JRN-%'")
                rows = cursor.fetchall()
                prefix = "JRN"
            elif mode.startswith("DEP"):
                cursor.execute("SELECT CHS_NO FROM Receipts WHERE CHS_NO LIKE 'DEP-%'")
                rows = cursor.fetchall()
                prefix = "DEP"
            elif mode.startswith("WTH"):
                cursor.execute("SELECT CHS_NO FROM Receipts WHERE CHS_NO LIKE 'WTH-%'")
                rows = cursor.fetchall()
                prefix = "WTH"
            else:
                cursor.execute("SELECT CHS_NO FROM Receipts WHERE CHS_NO LIKE ?", (f"{mode}-%",))
                rows = cursor.fetchall()
                prefix = mode
            conn.close()

            max_num = 0
            for r in rows:
                val = str(r[0])
                try:
                    num = int(val.split("-")[-1])
                    if num > max_num:
                        max_num = num
                except (IndexError, ValueError):
                    pass
            return f"{prefix}-{max_num + 1:03d}"
        except Exception:
            return f"{mode}-001"

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def close(self):
        self.app.accounts()

    def receipts(self):
        from receipts import Receipt
        Receipt(self)
    

    def payments(self):
        from payments import Payments
        Payments(self) 
   
    def journal(self):
        from journal import Joural
        Joural(self)
    # =========================================================================
    # DEPOSIT 
    # =========================================================================
    def deposit(self):
        win = tk.Toplevel(self.root)
        win.title("Cash Deposit")
        win.geometry("450x320")
        win.configure(bg="white")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Bank Cash Deposit", font=("Arial", 16, "bold"), bg="white", fg="navy").pack(pady=10)

        grid_frame = tk.Frame(win, bg="white")
        grid_frame.pack(padx=20, pady=10)

        # Row 1
        tk.Label(grid_frame, text="Date:", font=("Arial", 10), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        date_entry = tk.Entry(grid_frame, font=("Arial", 10), width=14)
        date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(grid_frame, text="Doc No:", font=("Arial", 10), bg="white").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        doc_no_var = tk.StringVar(value=self.get_next_chs_no("DEP"))
        doc_no_entry = tk.Entry(grid_frame, font=("Arial", 10), width=14, textvariable=doc_no_var, state="readonly", justify="center")
        doc_no_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Row 2
        tk.Label(grid_frame, text="Bank Name:", font=("Arial", 10), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        banks = self.get_banks()
        bank_combo = ttk.Combobox(grid_frame, values=banks, font=("Arial", 9), width=24, state="readonly")
        if banks:
            bank_combo.current(0)
        bank_combo.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        # Row 3
        tk.Label(grid_frame, text="Narration:", font=("Arial", 10), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        narration_entry = tk.Entry(grid_frame, font=("Arial", 10), width=26)
        narration_entry.insert(0, "Cash Deposited in Bank")
        narration_entry.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        # Row 4
        tk.Label(grid_frame, text="Amount (₹):", font=('Arial', 10, 'bold'), bg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        amount_entry = tk.Entry(grid_frame, font=('Arial', 10, 'bold'), width=14)
        amount_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        def save_deposit():
            dep_date = date_entry.get().strip()
            doc_no = doc_no_entry.get().strip()
            bank_name = bank_combo.get().strip()
            narration = narration_entry.get().strip()
            amt_str = amount_entry.get().strip()

            if not bank_name:
                messagebox.showwarning("Validation Error", "Please select a Bank Name.")
                return
            try:
                amt = float(amt_str)
                if amt <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid positive Amount.")
                return

            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Receipts (transaction_type, CHS_NO, DATE, PAID_TO, ADDRESS, Narration, A_C_HEAD, AMOUNT)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', ("Deposit-CASH", doc_no, dep_date, bank_name, "Bank Deposit", narration, "Cash Deposit", amt))
                
                # Update bank balance
                cursor.execute("UPDATE Banks SET balance = balance + ? WHERE bank_name = ?", (amt, bank_name))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"₹{amt:,.2f} deposited into {bank_name} successfully!")
                win.destroy()
                if hasattr(self, 'receipt_tree'):
                    self.load_receipts_data()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to record deposit: {e}")

        btn_frame = tk.Frame(win, bg="white")
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Save Deposit", font=("Arial", 10, "bold"), bg="green", fg="white", width=14, command=save_deposit).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", font=("Arial", 10), bg="gray", fg="white", width=10, command=win.destroy).pack(side="left", padx=10)

    # =========================================================================
    # WITHDRAWAL
    # =========================================================================

    def withdrawal(self):
        win = tk.Toplevel(self.root)
        win.title("Cash Withdrawal")
        win.geometry("480x360")
        win.configure(bg="white")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Bank Cash Withdrawal", font=("Arial", 16, "bold"), bg="white", fg="navy").pack(pady=10)

        grid_frame = tk.Frame(win, bg="white")
        grid_frame.pack(padx=20, pady=10)

        # Row 0
        tk.Label(grid_frame, text="Date:", font=("Arial", 10), bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        date_entry = tk.Entry(grid_frame, font=("Arial", 10), width=14)
        date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(grid_frame, text="Doc No:", font=("Arial", 10), bg="white").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        doc_no_var = tk.StringVar(value=self.get_next_chs_no("WTH"))
        doc_no_entry = tk.Entry(grid_frame, font=("Arial", 10), width=14, textvariable=doc_no_var, state="readonly", justify="center")
        doc_no_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Row 1
        tk.Label(grid_frame, text="Cheque No:", font=("Arial", 10), bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        chq_entry = tk.Entry(grid_frame, font=("Arial", 10), width=14)
        chq_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(grid_frame, text="Cheque Date:", font=("Arial", 10), bg="white").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        chq_date_entry = tk.Entry(grid_frame, font=("Arial", 10), width=14)
        chq_date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        chq_date_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Row 2
        tk.Label(grid_frame, text="Bank Name:", font=("Arial", 10), bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        banks = self.get_banks()
        bank_combo = ttk.Combobox(grid_frame, values=banks, font=("Arial", 9), width=24, state="readonly")
        if banks:
            bank_combo.current(0)
        bank_combo.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        # Row 3
        tk.Label(grid_frame, text="Narration:", font=("Arial", 10), bg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        narration_entry = tk.Entry(grid_frame, font=("Arial", 10), width=26)
        narration_entry.insert(0, "Cash Withdrawn from Bank")
        narration_entry.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        # Row 4
        tk.Label(grid_frame, text="Amount (₹):", font=('Arial', 10, 'bold'), bg="white").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        amount_entry = tk.Entry(grid_frame, font=('Arial', 10, 'bold'), width=14)
        amount_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        def save_withdrawal():
            wth_date = date_entry.get().strip()
            doc_no = doc_no_entry.get().strip()
            chq_no = chq_entry.get().strip()
            bank_name = bank_combo.get().strip()
            narration = narration_entry.get().strip()
            amt_str = amount_entry.get().strip()

            if not bank_name:
                messagebox.showwarning("Validation Error", "Please select a Bank Name.")
                return
            try:
                amt = float(amt_str)
                if amt <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid positive Amount.")
                return

            full_narration = f"{narration} (Chq: {chq_no})" if chq_no else narration

            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Receipts (transaction_type, CHS_NO, DATE, PAID_TO, ADDRESS, Narration, A_C_HEAD, AMOUNT)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', ("Withdrawal-CASH", doc_no, wth_date, bank_name, f"Bank Withdrawal|Bank:{bank_name}", full_narration, "Cash Withdrawal", amt))
                
                # Update bank balance
                cursor.execute("UPDATE Banks SET balance = balance - ? WHERE bank_name = ?", (amt, bank_name))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"₹{amt:,.2f} withdrawn from {bank_name} successfully!")
                win.destroy()
                if hasattr(self, 'payment_tree'):
                    self.load_payments_data()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to record withdrawal: {e}")

        btn_frame = tk.Frame(win, bg="white")
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Save Withdrawal", font=("Arial", 10, "bold"), bg="green", fg="white", width=16, command=save_withdrawal).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", font=("Arial", 10), bg="gray", fg="white", width=10, command=win.destroy).pack(side="left", padx=10)

    
    def head(self):
       from head import Head
       Head(self)

    def bank_list(self):
        from bank import Bank
        Bank(self)

# Data Access Layer Helper Functions
def add_receipts(app, transaction_type, CHS_NO, date, paid_to, address, Narration, A_C_HEAD, AMOUNT):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Receipts (transaction_type, CHS_NO, DATE, PAID_TO, ADDRESS, Narration, A_C_HEAD, AMOUNT)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (transaction_type, CHS_NO, date, paid_to, address, Narration, A_C_HEAD, AMOUNT))
    conn.commit()
    conn.close()

def get_all_receipts(app=None):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Receipts ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_receipts(app, id, transaction_type, CHS_NO, date, paid_to, address, Narration, A_C_HEAD, AMOUNT):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Receipts SET transaction_type=?, CHS_NO=?, DATE=?, PAID_TO=?, ADDRESS=?, Narration=?, A_C_HEAD=?, AMOUNT=? WHERE id=?
    ''', (transaction_type, CHS_NO, date, paid_to, address, Narration, A_C_HEAD, AMOUNT, id))
    conn.commit()
    conn.close()

# Auto-initialize database schema when imported
init_db()
