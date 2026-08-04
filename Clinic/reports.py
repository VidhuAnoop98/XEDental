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

        btn_Transaction = tk.Button(workspace, text="Daily Transactions", font=('Arial', 11), width=22,command=self.daily_transaction)
        btn_Transaction.place(x=200, y=180)  

        for i, (text, command) in enumerate(col1_buttons):
            btn = tk.Button(workspace, text=text, font=('Arial', 11), width=22, command=command)
            btn.place(x=200, y=260 + i * 35)  

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
        win.geometry("800x800")
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
        btn_close = tk.Button(win, text="Close", font=('Arial', 10, 'bold'), bg="#c62828", fg="white", command=win.destroy)
        btn_close.pack(pady=10)

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

        btn_close = tk.Button(win, text="Close", font=('Arial', 10, 'bold'), bg="#c62828", fg="white", command=win.destroy)
        btn_close.pack(pady=10)

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
                messagebox.showerror("Error", f"Database error: {e}")

            # Button controls
            btn_load = tk.Button(hdr_frame, text="Submit Filter", font=("Arial", 10, "bold"), bg="#1565c0", fg="white", command=load_cash_book)
            btn_load.pack(side="left", padx=10)
            btn_close = tk.Button(hdr_frame, text="Close", font=("Arial", 10, "bold"), bg="#c62828", fg="white", command=self.close)
            btn_close.pack(side="left", padx=10)

        load_cash_book()

    def daily_transaction(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(fill="both", expand=True, padx=10, pady=10)
        ws = self.app.workspace

        PAGE_W, PAGE_H = 595.0, 842.0 # A4 size in points

        # Try to check if reportlab is ok
        try:
            from reportlab.lib.pagesizes import A4
            reportlab_ok = True
        except ImportError:
            reportlab_ok = False

        # Date Control Header
        hdr_frame = tk.Frame(ws)
        hdr_frame.pack(pady=5)

        tk.Label(hdr_frame, text="Start Date:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        start_date_entry = tk.Entry(hdr_frame, font=("Arial", 10), width=12, justify="center")
        start_date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        start_date_entry.pack(side="left", padx=5)

        btn_cal_start = tk.Button(hdr_frame, text="📅", font=('Arial', 9), command=lambda: self.open_calendar(start_date_entry))
        btn_cal_start.pack(side="left", padx=5)

        tk.Label(hdr_frame, text="End Date:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        end_date_entry = tk.Entry(hdr_frame, font=("Arial", 10), width=12, justify="center")
        end_date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        end_date_entry.pack(side="left", padx=5)

        btn_cal_end = tk.Button(hdr_frame, text="📅", font=('Arial', 9), command=lambda: self.open_calendar(end_date_entry))
        btn_cal_end.pack(side="left", padx=5)

        btn_refresh = tk.Button(hdr_frame, text="Update", font=("Arial", 10, "bold"), bg="#0288d1", fg="white", command=lambda: update_preview())
        btn_refresh.pack(side="left", padx=10)

        AVAIL_H = 500
        AVAIL_W = 500
        self.preview_scale = min(AVAIL_H / PAGE_H, AVAIL_W / PAGE_W)
        
        CW      = int(PAGE_W * self.preview_scale)
        CH      = int(PAGE_H * self.preview_scale)

        outer = tk.Frame(ws, bg="#c0c0c0")
        outer.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        vsb = tk.Scrollbar(outer, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(outer, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        cv = tk.Canvas(outer, bg="#c0c0c0", width=CW+10, height=CH+1,
                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        cv.pack(fill="both", expand=True)
        vsb.config(command=cv.yview)
        hsb.config(command=cv.xview)

        canvas_width = CW + 950      # Same as the Canvas width logic in Letter_Pad
        OX = (canvas_width - CW) // 2
        OY = 10

        state = {
            "pages": [[]],
            "current_page": 0,
            "total_receipts": 0.0,
            "total_payments": 0.0,
            "s_str": "",
            "e_str": ""
        }

        def zoom_in():
            if self.preview_scale < 2.0:
                self.preview_scale = round(min(2.0, self.preview_scale + 0.1), 1)
                draw_page_preview(state["current_page"])

        def zoom_out():
            if self.preview_scale > 0.25:
                self.preview_scale = round(max(0.25, self.preview_scale - 0.1), 1)
                draw_page_preview(state["current_page"])

        def on_mouse_wheel(event):
            if getattr(event, "delta", 0) > 0 or getattr(event, "num", 0) == 4:
                zoom_in()
            else:
                zoom_out()
            return "break"

        cv.bind("<MouseWheel>", on_mouse_wheel)
        cv.bind("<Button-4>", on_mouse_wheel)
        cv.bind("<Button-5>", on_mouse_wheel)

        def prev_page():
            if state["current_page"] > 0:
                draw_page_preview(state["current_page"] - 1)

        def next_page():
            if state["current_page"] < len(state["pages"]) - 1:
                draw_page_preview(state["current_page"] + 1)

        def draw_page_preview(page_idx):
            state["current_page"] = page_idx
            cv.delete("all")
            
            scale = self.preview_scale
            w_scaled = int(PAGE_W * scale)
            h_scaled = int(PAGE_H * scale)
            
            cv.config(scrollregion=(0, 0, w_scaled + 40, h_scaled + 40))
            
            local_ox = (canvas_width - w_scaled) // 2
            local_oy = 10
            
            # Draw paper shadow
            cv.create_rectangle(local_ox+4, local_oy+4, local_ox+w_scaled+4, local_oy+h_scaled+4, fill="#888888", outline="")
            # Draw paper background
            cv.create_rectangle(local_ox, local_oy, local_ox+w_scaled, local_oy+h_scaled, fill="white", outline="#aaaaaa", width=1)
            
            def ppx(pt):  return local_ox + int(pt * scale)
            def ppy(pt):  return local_oy + int((PAGE_H - pt) * scale)
            def pcx():    return local_ox + w_scaled // 2
            def spt(pt_val): return max(6, int(pt_val * scale))
            
            pages = state["pages"]
            if not pages or page_idx >= len(pages):
                return
                
            page_txs = pages[page_idx]
            
            page_lbl.config(text=f"Page {page_idx + 1} of {len(pages)}")
            zoom_lbl.config(text=f"{int(scale / (min(600 / PAGE_H, 500 / PAGE_W)) * 100)}%")
            
            s_str = state["s_str"]
            e_str = state["e_str"]
            
            if page_idx == 0:
                cv.create_text(pcx(), ppy(PAGE_H - 40), text="Daily Transactions",
                               font=("Helvetica", spt(16), "bold"), fill="black")
                cv.create_text(pcx(), ppy(PAGE_H - 60), text=f"{s_str} to {e_str}",
                               font=("Helvetica", spt(12)), fill="black")
                y_pt = PAGE_H - 100
            else:
                y_pt = PAGE_H - 50
                
            # Table headers
            headers = ["No", "Patient Name", "Address", "Receipts", "Payments"]
            x_pt_positions = [30, 100, 200, 420, 500]
            
            cv.create_line(ppx(30), ppy(y_pt - 5), ppx(PAGE_W - 30), ppy(y_pt - 5), fill="black", width=1)
            y_pt -= 16
            
            for i, h in enumerate(headers):
                cv.create_text(ppx(x_pt_positions[i]), ppy(y_pt), text=h,
                               font=("Helvetica", spt(10), "bold"), fill="black", anchor="w")
            
            cv.create_line(ppx(30), ppy(y_pt - 10), ppx(PAGE_W - 30), ppy(y_pt - 10), fill="black", width=1)
            y_pt -= 10
            
            for t in page_txs:
                t_id, r_date, chs_no, paid_to, t_type, ac_head, amt = t
                t_type_str = str(t_type) if t_type else ""
                
                cv.create_text(ppx(x_pt_positions[0]), ppy(y_pt), text=str(t_id), font=("Helvetica", spt(10)), fill="black", anchor="w")
                cv.create_text(ppx(x_pt_positions[1]), ppy(y_pt), text=str(r_date), font=("Helvetica", spt(10)), fill="black", anchor="w")
                cv.create_text(ppx(x_pt_positions[2]), ppy(y_pt), text=str(chs_no)[:12], font=("Helvetica", spt(10)), fill="black", anchor="w")
                cv.create_text(ppx(x_pt_positions[3]), ppy(y_pt), text=str(paid_to)[:25], font=("Helvetica", spt(10)), fill="black", anchor="w")
                cv.create_text(ppx(x_pt_positions[4]), ppy(y_pt), text=t_type_str[:12], font=("Helvetica", spt(10)), fill="black", anchor="w")
                cv.create_text(ppx(x_pt_positions[5]), ppy(y_pt), text=str(ac_head)[:12], font=("Helvetica", spt(10)), fill="black", anchor="w")
                cv.create_text(ppx(x_pt_positions[6]), ppy(y_pt), text=f"{amt:,.2f}", font=("Helvetica", spt(10)), fill="black", anchor="w")
                y_pt -= 18
                
            if page_idx == len(pages) - 1:
                y_pt_totals = y_pt - 70
                cv.create_line(ppx(30), ppy(y_pt_totals + 5), ppx(PAGE_W - 30), ppy(y_pt_totals + 5), fill="black", width=1)
                y_pt_totals -= 20
                cv.create_text(ppx(360), ppy(y_pt_totals), text="Total Receipts:", font=("Helvetica", spt(10), "bold"), fill="black", anchor="w")
                cv.create_text(ppx(510), ppy(y_pt_totals), text=f"{state['total_receipts']:,.2f}", font=("Helvetica", spt(10), "bold"), fill="black", anchor="w")
                y_pt_totals -= 15
                cv.create_text(ppx(360), ppy(y_pt_totals), text="Total Payments:", font=("Helvetica", spt(10), "bold"), fill="black", anchor="w")
                cv.create_text(ppx(510), ppy(y_pt_totals), text=f"{state['total_payments']:,.2f}", font=("Helvetica", spt(10), "bold"), fill="black", anchor="w")
                y_pt_totals -= 15
                cv.create_text(ppx(360), ppy(y_pt_totals), text="Net Balance:", font=("Helvetica", spt(10), "bold"), fill="black", anchor="w")
                cv.create_text(ppx(510), ppy(y_pt_totals), text=f"{(state['total_receipts'] - state['total_payments']):,.2f}", font=("Helvetica", spt(10), "bold"), fill="black", anchor="w")
            
            # Paper Page Footer
            cv.create_text(pcx(), ppy(30), text=f"Page {page_idx + 1} of {len(pages)}", font=("Helvetica", spt(9)), fill="black")

        def update_preview():
            s_str = start_date_entry.get().strip()
            e_str = end_date_entry.get().strip()
            if not s_str or not e_str:
                return

            s_date_obj = parse_date(s_str)
            e_date_obj = parse_date(e_str)

            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, DATE, CHS_NO, PAID_TO, transaction_type, A_C_HEAD, AMOUNT
                    FROM Receipts
                    ORDER BY id ASC
                ''')
                all_transactions = cursor.fetchall()
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error loading cash book: {e}")
                return

            # Filter by date range
            transactions = []
            total_receipts = 0.0
            total_payments = 0.0
            
            for t in all_transactions:
                t_id, r_date, chs_no, paid_to, t_type, ac_head, amt = t
                d_obj = parse_date(r_date)
                if s_date_obj and d_obj and d_obj < s_date_obj:
                    continue
                if e_date_obj and d_obj and d_obj > e_date_obj:
                    continue
                
                transactions.append((t_id, r_date, chs_no, paid_to, t_type, ac_head, amt))
                
                t_type_str = str(t_type) if t_type else ""
                if "Receipt" in t_type_str:
                    total_receipts += amt
                elif "Payment" in t_type_str:
                    total_payments += amt

            # Paginate transactions exactly
            pages = []
            current_page_txs = []
            y = 700  # Start Y for page 1
            
            for i, tx in enumerate(transactions):
                is_last = (i == len(transactions) - 1)
                required_space = 18
                if is_last:
                    required_space += 54
                
                if y - required_space < 50:
                    pages.append(current_page_txs)
                    current_page_txs = [tx]
                    y = 780
                else:
                    current_page_txs.append(tx)
                    y -= 18
            if current_page_txs:
                pages.append(current_page_txs)
            
            if not pages:
                pages = [[]]

            state["pages"] = pages
            state["current_page"] = 0
            state["total_receipts"] = total_receipts
            state["total_payments"] = total_payments
            state["s_str"] = s_str
            state["e_str"] = e_str

            draw_page_preview(0)

        # Preview Controls (Zoom & Navigation)
        ctrl_frame = tk.Frame(ws)
        ctrl_frame.pack(fill="x", pady=4)

        btn_prev = tk.Button(ctrl_frame, text=" ◀", font=("Arial", 9, "bold"), command=lambda: prev_page())
        btn_prev.pack(side="left", padx=5)

        page_lbl = tk.Label(ctrl_frame, text="Page 1 of 1", font=("Arial", 10, "bold"), bg="white")
        page_lbl.pack(side="left", padx=5)

        btn_next = tk.Button(ctrl_frame, text=" ▶", font=("Arial", 9, "bold"), command=lambda: next_page())
        btn_next.pack(side="left", padx=5)

        # tk.Label(ctrl_frame, text="   |   ", bg="white").pack(side="left")

        btn_zoom_out = tk.Button(ctrl_frame, text="-", font=("Arial", 9, "bold"), command=lambda: zoom_out())
        btn_zoom_out.pack(side="left", padx=5)

        zoom_lbl = tk.Label(ctrl_frame, text="100%", font=("Arial", 10), bg="white")
        zoom_lbl.pack(side="left", padx=5)

        btn_zoom_in = tk.Button(ctrl_frame, text="+", font=("Arial", 9, "bold"), command=lambda: zoom_in())
        btn_zoom_in.pack(side="left", padx=5)

        btn_bar = tk.Frame(ws)
        btn_bar.pack(pady=8)

        def generate_pdf(filepath, s_str, e_str):
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors

            s_date_obj = parse_date(s_str)
            e_date_obj = parse_date(e_str)

            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, DATE, CHS_NO, PAID_TO, transaction_type, A_C_HEAD, AMOUNT
                FROM Receipts
                ORDER BY id ASC
            ''')
            all_transactions = cursor.fetchall()
            conn.close()

            # Filter by date range
            transactions = []
            total_receipts = 0.0
            total_payments = 0.0
            for t in all_transactions:
                t_id, r_date, chs_no, paid_to, t_type, ac_head, amt = t
                d_obj = parse_date(r_date)
                if s_date_obj and d_obj and d_obj < s_date_obj:
                    continue
                if e_date_obj and d_obj and d_obj > e_date_obj:
                    continue
                transactions.append((t_id, r_date, chs_no, paid_to, t_type, ac_head, amt))
                
                t_type_str = str(t_type) if t_type else ""
                if "Receipt" in t_type_str:
                    total_receipts += amt
                elif "Payment" in t_type_str:
                    total_payments += amt

            # Paginate exactly like preview
            pages = []
            current_page_txs = []
            y = 700
            for i, tx in enumerate(transactions):
                is_last = (i == len(transactions) - 1)
                required_space = 18
                if is_last:
                    required_space += 54
                
                if y - required_space < 50:
                    pages.append(current_page_txs)
                    current_page_txs = [tx]
                    y = 780
                else:
                    current_page_txs.append(tx)
                    y -= 18
            if current_page_txs:
                pages.append(current_page_txs)
            
            if not pages:
                pages = [[]]

            c = canvas.Canvas(filepath, pagesize=(PAGE_W, PAGE_H))
            width, height = PAGE_W, PAGE_H
            
            for page_idx, page_txs in enumerate(pages):
                # Draw white background
                c.setFillColor(colors.white)
                c.rect(0, 0, width, height, fill=1, stroke=0)

                # Reset to black for text
                c.setFillColor(colors.black)
                
                if page_idx == 0:
                    c.setFont("Helvetica-Bold", 16)
                    c.drawCentredString(width / 2.0, height - 50, "Daily Transaction")
                    
                    c.setFont("Helvetica", 12)
                    c.drawCentredString(width / 2.0, height - 70, f"Period: {s_str} to {e_str}")
                    
                    y = height - 100
                else:
                    y = height - 50
                
                # Table headers
                c.setFont("Helvetica-Bold", 10)
                headers = ["No", "Patient Name", "Address", "Receipts", "Payments"]
                x_positions = [30, 100, 200, 420, 500]

                c.line(30, y - 5, width - 30, y - 5)
                y -= 16

                for i, h in enumerate(headers):
                    c.drawString(x_positions[i], y, h)
                
                c.line(30, y - 5, width - 30, y - 5)
                y -= 10
                
                c.setFont("Helvetica", 10)
                for t in page_txs:
                    t_id, r_date, chs_no, paid_to, t_type, ac_head, amt = t
                    t_type_str = str(t_type) if t_type else ""
                    
                    c.drawString(x_positions[0], y, str(t_id))
                    c.drawString(x_positions[1], y, str(r_date))
                    c.drawString(x_positions[2], y, str(chs_no)[:12])
                    c.drawString(x_positions[3], y, str(paid_to)[:25])
                    c.drawString(x_positions[4], y, t_type_str[:12])
                    c.drawString(x_positions[5], y, str(ac_head)[:12])
                    c.drawString(x_positions[6], y, f"{amt:,.2f}")
                    y -= 18

                if page_idx == len(pages) - 1:
                    y_pt_totals = y - 70
                    c.line(30, y_pt_totals + 5, width - 30, y_pt_totals + 5)
                    y_pt_totals -= 20
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(360, y_pt_totals, "Total Receipts:")
                    c.drawString(510, y_pt_totals, f"{total_receipts:,.2f}")
                    y_pt_totals -= 15
                    c.drawString(360, y_pt_totals, "Total Payments:")
                    c.drawString(510, y_pt_totals, f"{total_payments:,.2f}")
                    y_pt_totals -= 15
                    c.drawString(360, y_pt_totals, "Net Balance:")
                    c.drawString(510, y_pt_totals, f"{(total_receipts - total_payments):,.2f}")
                
                # Page number footer
                c.setFont("Helvetica", 9)
                c.drawCentredString(width / 2.0, 30, f"Page {page_idx + 1} of {len(pages)}")
                
                c.showPage()
                
            c.save()

        def _open_pdf(path):
            import subprocess
            import sys
            try:
                if hasattr(os, "startfile"):
                    os.startfile(path)
                elif sys.platform.startswith("linux"):
                    subprocess.Popen(["xdg-open", path])
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["cmd", "/c", "start", "", path])
            except Exception as exc:
                messagebox.showwarning("Open PDF", f"Could not open the PDF automatically.\n{exc}")

        def _generate_pdf():
            if not reportlab_ok:
                messagebox.showerror("Missing Library",
                    "ReportLab is required.\nRun:  pip install reportlab")
                return
            s_str = start_date_entry.get().strip()
            e_str = end_date_entry.get().strip()
            if not s_str or not e_str:
                messagebox.showerror("Error", "Please select start and end dates.")
                return
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf", initialfile=f"Daily_Transaction_{s_str}_to_{e_str}.pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Daily Transaction Report As")
            if not filepath: return
            try:
                generate_pdf(filepath, s_str, e_str)
                messagebox.showinfo("Done", f"Daily Transaction Report saved:\n{filepath}")
                _open_pdf(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"PDF generation failed:\n{exc}")

        def _print_now():
            if not reportlab_ok:
                messagebox.showerror("Missing Library",
                    "ReportLab is required.\nRun:  pip install reportlab")
                return
            s_str = start_date_entry.get().strip()
            e_str = end_date_entry.get().strip()
            if not s_str or not e_str:
                messagebox.showerror("Error", "Please select start and end dates.")
                return
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tmp = os.path.join(script_dir, "_daily_transaction_temp.pdf")
            try:
                generate_pdf(tmp, s_str, e_str)
                _open_pdf(tmp)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not open PDF:\n{exc}")

        tk.Button(btn_bar, text="📄  Generate PDF", font=("Arial", 11), width=16,
                  bg="#1565C0", fg="white", command=_generate_pdf).pack(side="left", padx=8)
        tk.Button(btn_bar, text="🖨  Open / Print", font=("Arial", 11), width=16,
                  bg="#2E7D32", fg="white", command=_print_now).pack(side="left", padx=8)
        tk.Button(btn_bar, text="Close",bg="#ED350E",fg="white", font=("Arial", 11), width=10,
                  command=self.close).pack(side="left", padx=8)

        update_preview()
