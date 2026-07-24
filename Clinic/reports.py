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


class Reports:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        app.clear_workspace()
        app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        workspace = app.workspace

        col1_buttons = [
            ("Receipt List",self.receipts_list),
            ("Payments List",self.payments_list),
            ("Cash Book",self.cash_book),
            ("General Ledger",self.general_ledger),
        ] 

        btn_Transaction = tk.Button(workspace, text="Daily Transactions", font=('Arial', 11), width=22)
        btn_Transaction.place(x=200, y=180)  

        for i, (text, command) in enumerate(col1_buttons):
            btn = tk.Button(workspace, text=text, font=('Arial', 11), width=22, command=command)
            btn.place(x=200, y=260 + i * 35)  

        btn_update = tk.Button(workspace, text="Update", font=('Arial', 11), width=22)
        btn_update.place(x=500, y=180)

        lbl_start_date = tk.Label(workspace, text="Start Date", font=('Arial', 11))
        lbl_start_date.place(x=430, y=290, width=210)

        entry_start_date = tk.Entry(workspace, font=('Arial', 11, 'bold'), justify='center', fg="blue")
        entry_start_date.insert(0, "01-04-2026")
        entry_start_date.place(x=580, y=290, width=150) 

        lbl_end_date = tk.Label(workspace, text="End Date", font=('Arial', 11))
        lbl_end_date.place(x=430, y=340, width=210)

        entry_end_date = tk.Entry(workspace, font=('Arial', 11, 'bold'), justify='center', fg="blue")
        entry_end_date.insert(0, "31-03-2027")
        entry_end_date.place(x=580, y=340, width=150)

        # Calendar Button for Start Date
        btn_start_calendar = tk.Button(workspace, text="📅", font=('Arial', 11), command=self.select_start_date)
        btn_start_calendar.place(x=750, y=290, height=25)

        # Calendar Button for End Date
        btn_end_calendar = tk.Button(workspace, text="📅", font=('Arial', 11), command=self.select_end_date)
        btn_end_calendar.place(x=750, y=340, height=25)
        
        # Store entries for calendar access
        self.entry_start_date = entry_start_date
        self.entry_end_date = entry_end_date

    def select_start_date(self):
        self.open_calendar(self.entry_start_date)

    def select_end_date(self):
        self.open_calendar(self.entry_end_date)

    def open_calendar(self, entry_widget):
        if Calendar is None:
            messagebox.showinfo("Calendar", "Please enter date manually in format DD-MM-YYYY (e.g. 01-04-2026).")
            return

        win = tk.Toplevel(self.app.root)
        win.title("Select Date")
        win.transient(self.app.root)
        win.grab_set()

        cal = Calendar(win, selectmode="day", date_pattern="dd-mm-yyyy")
        cal.pack(padx=10, pady=10)

        def select():
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, cal.get_date())
            win.destroy()

        tk.Button(win, text="OK", font=("Arial", 10, "bold"), bg="green", fg="white", width=10, command=select).pack(pady=5)

    def close(self):
        self.app.reports()

    def general_ledger(self):
        from general_ledger import General
        General(self)
    # =========================================================================
    # RECEIPTS LIST REPORT
    # =========================================================================
    def receipts_list(self):
        win = tk.Toplevel(self.app.root)
        win.title("Receipts List Report")
        win.geometry("800x500")
        win.transient(self.app.root)
        win.grab_set()

        title = tk.Label(win, text="Receipts List Report", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=10)

        # Filter Frame
        filter_frame = tk.Frame(win)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Date / Filter:", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        entry_date = tk.Entry(filter_frame, font=('Arial', 10, 'bold'), width=12, fg='blue', justify="center")
        entry_date.insert(0, date.today().strftime("%d-%m-%Y"))
        entry_date.pack(side="left", padx=5)

        btn_cal = tk.Button(filter_frame, text="📅", font=('Arial', 10), command=lambda: self.open_calendar(entry_date))
        btn_cal.pack(side="left", padx=5)

        # Treeview Table
        tree_frame = tk.Frame(win)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("ID", "Date", "CHS_NO", "Received_From", "Mode", "A_C_Head", "Narration", "Amount")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

        headings = {
            "ID": "ID", "Date": "Date", "CHS_NO": "Receipt No", "Received_From": "Received From",
            "Mode": "Mode", "A_C_Head": "A/C Head", "Narration": "Narration", "Amount": "Amount (₹)"
        }
        widths = {"ID": 40, "Date": 90, "CHS_NO": 90, "Received_From": 140, "Mode": 70, "A_C_Head": 130, "Narration": 150, "Amount": 100}

        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center" if col in ("ID", "Date", "CHS_NO", "Mode") else "w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        total_var = tk.StringVar(value="Total Receipts: ₹0.00")
        tk.Label(win, textvariable=total_var, font=('Arial', 11, 'bold'), fg="navy").pack(pady=5)

        def load_data():
            for item in tree.get_children():
                tree.delete(item)

            filter_dt = entry_date.get().strip()
            total_amt = 0.0

            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                if filter_dt:
                    cursor.execute('''
                        SELECT id, DATE, CHS_NO, PAID_TO, transaction_type, A_C_HEAD, Narration, AMOUNT
                        FROM Receipts
                        WHERE (transaction_type LIKE 'Receipt%' OR transaction_type='Receipt') AND DATE=?
                        ORDER BY id DESC
                    ''', (filter_dt,))
                else:
                    cursor.execute('''
                        SELECT id, DATE, CHS_NO, PAID_TO, transaction_type, A_C_HEAD, Narration, AMOUNT
                        FROM Receipts
                        WHERE transaction_type LIKE 'Receipt%' OR transaction_type='Receipt'
                        ORDER BY id DESC
                    ''')

                rows = cursor.fetchall()
                conn.close()

                for r in rows:
                    rec_id, r_date, chs_no, r_from, t_type, ac_head, narration, amt = r
                    mode = "BANK" if "BANK" in str(t_type).upper() else "CASH"
                    tree.insert("", "end", values=(rec_id, r_date, chs_no, r_from, mode, ac_head, narration, f"₹{amt:,.2f}"))
                    total_amt += amt

                total_var.set(f"Total Receipts: ₹{total_amt:,.2f}")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to load receipts: {e}")

        btn_submit = tk.Button(filter_frame, text="Submit Filter", font=('Arial', 10, 'bold'), bg="#2e7d32", fg="white", command=load_data)
        btn_submit.pack(side="left", padx=10)


        load_data()

    # =========================================================================
    # PAYMENTS LIST REPORT
    # =========================================================================
    def payments_list(self):
        win = tk.Toplevel(self.app.root)
        win.title("Payments List Report")
        win.geometry("800x500")
        win.transient(self.app.root)
        win.grab_set()

        title = tk.Label(win, text="Payments List Report", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=10)

        # Filter Frame
        filter_frame = tk.Frame(win)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Date / Filter:", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        entry_date = tk.Entry(filter_frame, font=('Arial', 10, 'bold'), width=12, fg='blue', justify="center")
        entry_date.insert(0, date.today().strftime("%d-%m-%Y"))
        entry_date.pack(side="left", padx=5)

        btn_cal = tk.Button(filter_frame, text="📅", font=('Arial', 10), command=lambda: self.open_calendar(entry_date))
        btn_cal.pack(side="left", padx=5)

        # Treeview Table
        tree_frame = tk.Frame(win)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("ID", "Date", "CHS_NO", "Paid_To", "Mode", "A_C_Head", "Narration", "Amount")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

        headings = {
            "ID": "ID", "Date": "Date", "CHS_NO": "Payment No", "Paid_To": "Paid To",
            "Mode": "Mode", "A_C_Head": "A/C Head", "Narration": "Narration", "Amount": "Amount (₹)"
        }
        widths = {"ID": 40, "Date": 90, "CHS_NO": 90, "Paid_To": 140, "Mode": 70, "A_C_Head": 130, "Narration": 150, "Amount": 100}

        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center" if col in ("ID", "Date", "CHS_NO", "Mode") else "w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        total_var = tk.StringVar(value="Total Payments: ₹0.00")
        tk.Label(win, textvariable=total_var, font=('Arial', 11, 'bold'), fg="navy").pack(pady=5)

        def load_data():
            for item in tree.get_children():
                tree.delete(item)

            filter_dt = entry_date.get().strip()
            total_amt = 0.0

            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                if filter_dt:
                    cursor.execute('''
                        SELECT id, DATE, CHS_NO, PAID_TO, transaction_type, A_C_HEAD, Narration, AMOUNT
                        FROM Receipts
                        WHERE (transaction_type LIKE 'Payment%' OR transaction_type='Payment') AND DATE=?
                        ORDER BY id DESC
                    ''', (filter_dt,))
                else:
                    cursor.execute('''
                        SELECT id, DATE, CHS_NO, PAID_TO, transaction_type, A_C_HEAD, Narration, AMOUNT
                        FROM Receipts
                        WHERE transaction_type LIKE 'Payment%' OR transaction_type='Payment'
                        ORDER BY id DESC
                    ''')

                rows = cursor.fetchall()
                conn.close()

                for r in rows:
                    rec_id, r_date, chs_no, p_to, t_type, ac_head, narration, amt = r
                    mode = "BANK" if "BANK" in str(t_type).upper() else "CASH"
                    tree.insert("", "end", values=(rec_id, r_date, chs_no, p_to, mode, ac_head, narration, f"₹{amt:,.2f}"))
                    total_amt += amt

                total_var.set(f"Total Payments: ₹{total_amt:,.2f}")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to load payments: {e}")

        btn_submit = tk.Button(filter_frame, text="Submit Filter", font=('Arial', 10, 'bold'), bg="#2e7d32", fg="white", command=load_data)
        btn_submit.pack(side="left", padx=10)

        load_data()

    # =========================================================================
    # CASH BOOK REPORT
    # =========================================================================
    def cash_book(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame = tk.Frame(self.app.workspace)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title = tk.Label(main_frame, text="Cash Book Statement", font=("Arial", 16, "bold"), fg="navy")
        title.pack(pady=5)

        # Date Control Header
        hdr_frame = tk.Frame(main_frame)
        hdr_frame.pack(pady=5)

        tk.Label(hdr_frame, text="Date:", font=("Arial", 11, "bold")).pack(side="left", padx=5)
        date_entry = tk.Entry(hdr_frame, font=("Arial", 11), width=12, justify="center")
        date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        date_entry.pack(side="left", padx=5)

        btn_cal = tk.Button(hdr_frame, text="📅", font=('Arial', 10), command=lambda: self.open_calendar(date_entry))
        btn_cal.pack(side="left", padx=5)

        # Tables Container
        tables_frame = tk.Frame(main_frame)
        tables_frame.pack(fill="both", expand=True, pady=10)

        # Left Column: Cash Receipts
        r_frame = tk.LabelFrame(tables_frame, text="Cash Receipts (Dr)", font=("Arial", 10, "bold"), padx=10, pady=10)
        r_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        r_tree = ttk.Treeview(r_frame, columns=("No", "Particulars", "Amount"), show="headings", height=10)
        r_tree.heading("No", text="Receipt No")
        r_tree.heading("Particulars", text="Particulars")
        r_tree.heading("Amount", text="Amount (₹)")
        r_tree.column("No", width=90, anchor="center")
        r_tree.column("Particulars", width=180)
        r_tree.column("Amount", width=100, anchor="e")
        r_tree.pack(fill="both", expand=True)

        # Right Column: Cash Payments
        p_frame = tk.LabelFrame(tables_frame, text="Cash Payments (Cr)", font=("Arial", 10, "bold"), padx=10, pady=10)
        p_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        p_tree = ttk.Treeview(p_frame, columns=("No", "Particulars", "Amount"), show="headings", height=10)
        p_tree.heading("No", text="Payment No")
        p_tree.heading("Particulars", text="Particulars")
        p_tree.heading("Amount", text="Amount (₹)")
        p_tree.column("No", width=90, anchor="center")
        p_tree.column("Particulars", width=180)
        p_tree.column("Amount", width=100, anchor="e")
        p_tree.pack(fill="both", expand=True)

        # Bottom Totals Bar
        totals_frame = tk.Frame(main_frame, bd=1, relief="groove", padx=10, pady=8)
        totals_frame.pack(fill="x", pady=5)

        tot_r_var = tk.StringVar(value="Total Cash In: ₹0.00")
        tk.Label(totals_frame, textvariable=tot_r_var, font=("Arial", 10, "bold"), fg="green").pack(side="left", padx=20)

        tot_p_var = tk.StringVar(value="Total Cash Out: ₹0.00")
        tk.Label(totals_frame, textvariable=tot_p_var, font=("Arial", 10, "bold"), fg="red").pack(side="left", padx=20)

        net_c_var = tk.StringVar(value="Net Cash Balance: ₹0.00")
        tk.Label(totals_frame, textvariable=net_c_var, font=("Arial", 11, "bold"), fg="navy").pack(side="right", padx=20)

        def load_cash_book():
            for item in r_tree.get_children():
                r_tree.delete(item)
            for item in p_tree.get_children():
                p_tree.delete(item)

            d_str = date_entry.get().strip()
            tot_in = 0.0
            tot_out = 0.0

            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()

                # Fetch Cash Receipts
                cursor.execute('''
                    SELECT CHS_NO, PAID_TO, AMOUNT FROM Receipts
                    WHERE transaction_type='Receipt-CASH' AND DATE=?
                ''', (d_str,))
                for chs, p_to, amt in cursor.fetchall():
                    r_tree.insert("", "end", values=(chs, p_to, f"₹{amt:,.2f}"))
                    tot_in += amt

                # Fetch Cash Payments
                cursor.execute('''
                    SELECT CHS_NO, PAID_TO, AMOUNT FROM Receipts
                    WHERE transaction_type='Payment-CASH' AND DATE=?
                ''', (d_str,))
                for chs, p_to, amt in cursor.fetchall():
                    p_tree.insert("", "end", values=(chs, p_to, f"₹{amt:,.2f}"))
                    tot_out += amt

                conn.close()

                tot_r_var.set(f"Total Cash In: ₹{tot_in:,.2f}")
                tot_p_var.set(f"Total Cash Out: ₹{tot_out:,.2f}")

                net_bal = tot_in - tot_out
                net_c_var.set(f"Net Cash Balance: ₹{net_bal:,.2f}")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error loading cash book: {e}")

        btn_load = tk.Button(hdr_frame, text="Submit Filter", font=("Arial", 10, "bold"), bg="#1565c0", fg="white", command=load_cash_book)
        btn_load.pack(side="left", padx=10)
        btn_close = tk.Button(hdr_frame, text="Close", font=("Arial", 10, "bold"), bg="#c62828", fg="white", command=self.close)
        btn_close.pack(side="left", padx=10)

        load_cash_book()
