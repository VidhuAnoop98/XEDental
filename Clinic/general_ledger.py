import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

try:
    from tkcalendar import Calendar
except ImportError:
    Calendar = None


def get_db_connection(app=None):
    """Return a SQLite connection to dental.db."""
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = getattr(app, "script_dir", os.path.dirname(os.path.abspath(__file__)))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))


def parse_date(date_str):
    """Parse date string into date object for comparison."""
    if not date_str:
        return None
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            pass
    return None


class General:
    def __init__(self, reports_view):
        self.reports_view = reports_view
        self.app = reports_view.app
        self.root = self.app.root
        self.open_calendar = reports_view.open_calendar
        self.general_ledger()

    def close(self):
        self.reports_view.close()

    def general_ledger(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame = tk.Frame(self.app.workspace)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title Header
        title = tk.Label(main_frame, text="General Ledger", font=("Arial", 16, "bold"), fg="navy")
        title.pack(side="top", pady=(5, 10))

        # Split Content Layout
        content_box = tk.Frame(main_frame)
        content_box.pack(fill="both", expand=True)

        # ── LEFT PANEL (Account Heads & Date Range) ──────────────────────────
        left_frame = tk.LabelFrame(content_box, text="Ledger Controls", font=("Arial", 10, "bold"), width=300, padx=10, pady=10)
        left_frame.pack(side="left", fill="y", padx=(0, 10), pady=5)
        left_frame.pack_propagate(False)

        # Date Filters
        tk.Label(left_frame, text="Start Date:", font=('Arial', 9, 'bold')).pack(anchor="w", pady=(5, 2))
        s_date_frame = tk.Frame(left_frame)
        s_date_frame.pack(fill="x", pady=(0, 5))
        self.gl_start_date = tk.Entry(s_date_frame, font=('Arial', 10), width=12, justify='center')
        self.gl_start_date.insert(0, "01-04-2026")
        self.gl_start_date.pack(side="left", padx=(0, 5))
        tk.Button(s_date_frame, text="📅", font=('Arial', 9), command=lambda: self.open_calendar(self.gl_start_date)).pack(side="left")

        tk.Label(left_frame, text="End Date:", font=('Arial', 9, 'bold')).pack(anchor="w", pady=(5, 2))
        e_date_frame = tk.Frame(left_frame)
        e_date_frame.pack(fill="x", pady=(0, 10))
        self.gl_end_date = tk.Entry(e_date_frame, font=('Arial', 10), width=12, justify='center')
        self.gl_end_date.insert(0, date.today().strftime("%d-%m-%Y"))
        self.gl_end_date.pack(side="left", padx=(0, 5))
        tk.Button(e_date_frame, text="📅", font=('Arial', 9), command=lambda: self.open_calendar(self.gl_end_date)).pack(side="left")

        # Head Search Box
        tk.Label(left_frame, text="Find Head:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        self.gl_search_entry = tk.Entry(left_frame, font=("Arial", 10))
        self.gl_search_entry.pack(fill="x", pady=(0, 8))
        self.gl_search_entry.bind("<KeyRelease>", self._filter_heads_list)

        # Heads Treeview
        tk.Label(left_frame, text="Account Heads List:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
        head_tree_frame = tk.Frame(left_frame)
        head_tree_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.heads_tree = ttk.Treeview(head_tree_frame, columns=("Head", "Type"), show="headings", height=8)
        self.heads_tree.heading("Head", text="Head Name")
        self.heads_tree.heading("Type", text="Type")
        self.heads_tree.column("Head", width=160, anchor="w")
        self.heads_tree.column("Type", width=90, anchor="center")

        vsb_h = ttk.Scrollbar(head_tree_frame, orient="vertical", command=self.heads_tree.yview)
        self.heads_tree.configure(yscrollcommand=vsb_h.set)
        self.heads_tree.pack(side="left", fill="both", expand=True)
        vsb_h.pack(side="right", fill="y")

        self.heads_tree.bind("<<TreeviewSelect>>", lambda e: self.load_general_ledger_data())

        btn_load = tk.Button(left_frame, text="Load Selected Ledger", font=("Arial", 10, "bold"), bg="#2e7d32", fg="white", command=self.load_general_ledger_data)
        btn_load.pack(fill="x", pady=4)

        btn_close = tk.Button(left_frame, text="Close Report", font=("Arial", 10), command=self.close)
        btn_close.pack(fill="x", pady=4)

        # ── RIGHT PANEL (Ledger Statements & Totals) ─────────────────────────
        right_frame = tk.LabelFrame(content_box, text="Ledger Statement", font=("Arial", 10, "bold"), padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=5)

        self.gl_header_lbl = tk.Label(right_frame, text="Select an Account Head to view statement", font=("Arial", 11, "bold"), fg="navy")
        self.gl_header_lbl.pack(anchor="w", pady=(0, 8))

        # Ledger Transactions Treeview
        gl_tree_frame = tk.Frame(right_frame)
        gl_tree_frame.pack(fill="both", expand=True, pady=5)

        gl_columns = ("Date", "No", "Type", "Narrations", "Debit", "Credit")
        self.general_ledger_tree = ttk.Treeview(gl_tree_frame, columns=gl_columns, show="headings", height=12)

        headings = {
            "Date": "Date", "No": "Voucher No", "Type": "Type",
            "Narrations": "Particulars / Narration", "Debit": "Debit (₹)", "Credit": "Credit (₹)"
        }
        widths = {
            "Date": 90, "No": 100, "Type": 110, "Narrations": 260, "Debit": 110, "Credit": 110
        }

        for col in gl_columns:
            self.general_ledger_tree.heading(col, text=headings[col])
            self.general_ledger_tree.column(col, width=widths[col], anchor="e" if col in ("Debit", "Credit") else ("center" if col in ("Date", "No") else "w"))

        vsb_gl = ttk.Scrollbar(gl_tree_frame, orient="vertical", command=self.general_ledger_tree.yview)
        self.general_ledger_tree.configure(yscrollcommand=vsb_gl.set)
        self.general_ledger_tree.pack(side="left", fill="both", expand=True)
        vsb_gl.pack(side="right", fill="y")

        # Totals Summary Bar
        totals_frame = tk.Frame(right_frame, bd=1, relief="groove", padx=10, pady=6)
        totals_frame.pack(fill="x", pady=(8, 0))

        tk.Label(totals_frame, text="Total Debit (Dr):", font=("Arial", 10, "bold")).pack(side="left", padx=(5, 2))
        self.dr_var = tk.StringVar(value="₹0.00")
        dr_entry = tk.Entry(totals_frame, textvariable=self.dr_var, font=("Arial", 10, "bold"), fg="green", width=14, state="readonly", justify="right")
        dr_entry.pack(side="left", padx=(0, 15))

        tk.Label(totals_frame, text="Total Credit (Cr):", font=("Arial", 10, "bold")).pack(side="left", padx=(5, 2))
        self.cr_var = tk.StringVar(value="₹0.00")
        cr_entry = tk.Entry(totals_frame, textvariable=self.cr_var, font=("Arial", 10, "bold"), fg="red", width=14, state="readonly", justify="right")
        cr_entry.pack(side="left", padx=(0, 15))

        tk.Label(totals_frame, text="Net Balance:", font=("Arial", 10, "bold")).pack(side="left", padx=(5, 2))
        self.balance_var = tk.StringVar(value="₹0.00")
        bal_entry = tk.Entry(totals_frame, textvariable=self.balance_var, font=("Arial", 10, "bold"), fg="navy", width=16, state="readonly", justify="right")
        bal_entry.pack(side="left", padx=(0, 5))

        self._all_heads = []
        self._populate_heads_tree()

    def _populate_heads_tree(self):
        for item in self.heads_tree.get_children():
            self.heads_tree.delete(item)

        self._all_heads = []
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT head_name, head_type FROM Heads ORDER BY head_name")
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                default_heads = [
                    ("Doctor Fees", "Income"),
                    ("Laboratory Expense", "Expense"),
                    ("Material / Dental Supplies", "Expense"),
                    ("Rent & Facilities", "Expense"),
                    ("Salary & Wages", "Expense"),
                    ("Electricity / Utilities", "Expense"),
                    ("Equipment Purchase/Maintenance", "Expense"),
                    ("Office & Administrative", "Expense"),
                    ("Miscellaneous Expense", "Expense")
                ]
                rows = default_heads

            self._all_heads = rows
            for h_name, h_type in rows:
                self.heads_tree.insert("", "end", values=(h_name, h_type))

            # Select first head by default
            children = self.heads_tree.get_children()
            if children:
                self.heads_tree.selection_set(children[0])
                self.load_general_ledger_data()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading account heads: {e}")

    def _filter_heads_list(self, event=None):
        query = self.gl_search_entry.get().strip().lower()
        for item in self.heads_tree.get_children():
            self.heads_tree.delete(item)

        for h_name, h_type in self._all_heads:
            if query in h_name.lower() or query in h_type.lower():
                self.heads_tree.insert("", "end", values=(h_name, h_type))

    def load_general_ledger_data(self):
        selected = self.heads_tree.selection()
        if not selected:
            return

        head_name, head_type = self.heads_tree.item(selected[0])['values']
        s_date_obj = parse_date(self.gl_start_date.get())
        e_date_obj = parse_date(self.gl_end_date.get())

        s_str = self.gl_start_date.get().strip()
        e_str = self.gl_end_date.get().strip()

        self.gl_header_lbl.config(text=f"Statement for Head: {head_name} ({head_type})  [{s_str} to {e_str}]")

        for item in self.general_ledger_tree.get_children():
            self.general_ledger_tree.delete(item)

        total_dr = 0.0
        total_cr = 0.0

        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()

            # 1. Fetch from Receipts table where A_C_HEAD matches
            cursor.execute('''
                SELECT DATE, CHS_NO, transaction_type, PAID_TO, Narration, AMOUNT
                FROM Receipts
                WHERE A_C_HEAD = ? OR PAID_TO = ?
            ''', (head_name, head_name))
            rec_rows = cursor.fetchall()

            # 2. Fetch from Journal table where debit_head or credit_head matches
            cursor.execute('''
                SELECT date, voucher_no, debit_head, credit_head, narration, amount
                FROM Journal
                WHERE debit_head = ? OR credit_head = ?
            ''', (head_name, head_name))
            jrn_rows = cursor.fetchall()

            conn.close()

            transactions = []

            # Process Receipts records
            for r_date, chs_no, t_type, paid_to, narration, amount in rec_rows:
                d_obj = parse_date(r_date)
                if s_date_obj and d_obj and d_obj < s_date_obj:
                    continue
                if e_date_obj and d_obj and d_obj > e_date_obj:
                    continue

                is_receipt = "RECEIPT" in str(t_type).upper() or "DEPOSIT" in str(t_type).upper()

                # Standard double entry assignment based on Head Type:
                # For Income heads: Receipts are Credit
                # For Expense heads: Payments are Debit
                dr = 0.0
                cr = 0.0

                if head_type == "Income":
                    if is_receipt:
                        cr = amount
                    else:
                        dr = amount
                elif head_type == "Expense":
                    if not is_receipt:
                        dr = amount
                    else:
                        cr = amount
                else:  # Asset or Liability
                    if is_receipt:
                        dr = amount
                    else:
                        cr = amount

                particulars = f"{paid_to} | {narration}".strip(" |")
                transactions.append((d_obj or date.min, r_date, chs_no, t_type, particulars, dr, cr))

            # Process Journal records
            for j_date, v_no, debit_head, credit_head, narration, amount in jrn_rows:
                d_obj = parse_date(j_date)
                if s_date_obj and d_obj and d_obj < s_date_obj:
                    continue
                if e_date_obj and d_obj and d_obj > e_date_obj:
                    continue

                dr = 0.0
                cr = 0.0

                if debit_head == head_name:
                    dr = amount
                    particulars = f"To {credit_head} - {narration}".strip(" -")
                else:
                    cr = amount
                    particulars = f"By {debit_head} - {narration}".strip(" -")

                transactions.append((d_obj or date.min, j_date, v_no, "Journal", particulars, dr, cr))

            # Sort transactions chronologically
            transactions.sort(key=lambda x: x[0])

            for _, d_str, v_no, t_type, narration, dr, cr in transactions:
                dr_str = f"₹{dr:,.2f}" if dr > 0 else ""
                cr_str = f"₹{cr:,.2f}" if cr > 0 else ""

                self.general_ledger_tree.insert("", "end", values=(
                    d_str, v_no, t_type, narration, dr_str, cr_str
                ))

                total_dr += dr
                total_cr += cr

            self.dr_var.set(f"₹{total_dr:,.2f}")
            self.cr_var.set(f"₹{total_cr:,.2f}")

            net_bal = total_dr - total_cr
            if head_type == "Income":
                net_bal = total_cr - total_dr
                suffix = " (Cr)" if net_bal >= 0 else " (Dr)"
            else:
                suffix = " (Dr)" if net_bal >= 0 else " (Cr)"

            self.balance_var.set(f"₹{abs(net_bal):,.2f}{suffix}")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error querying general ledger: {e}")
