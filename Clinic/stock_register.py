import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime
from tkcalendar import Calendar

class Stock_Register:
    def __init__(self, materials_view):
        self.materials_view = materials_view
        self.app = materials_view.app
        self.root = self.app.root
        self._close_suppliers = materials_view._close_suppliers
        self.ensure_table_exists()
        self.stock_register()

    def get_db_connection(self):
        if hasattr(self.app, 'get_db_connection'):
            return self.app.get_db_connection()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return sqlite3.connect(os.path.join(script_dir, "dental.db"))

    def ensure_table_exists(self):
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS Stock_Register (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Date TEXT,
                    SID TEXT,
                    Invoice_No TEXT,
                    Invoice_Details TEXT,
                    Rate REAL,
                    Clinic TEXT,
                    Particulars TEXT,
                    Received_Qty REAL,
                    Used_Qty REAL,
                    Balance REAL,
                    Total REAL,
                    Product_Name TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass

    def stock_register(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        title = tk.Label(self.app.workspace, text="Stock Register", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=5)

        main = tk.Frame(self.app.workspace)
        main.pack(fill="both", expand=True)

        top_frame = tk.Frame(main)
        top_frame.pack(side="top", fill="x", padx=5, pady=5)

        left = tk.Frame(top_frame)
        left.pack(side="left", padx=5)

        middle = tk.Frame(top_frame)
        middle.pack(side="left", fill="both", expand=True, padx=5)

        right = tk.Frame(top_frame)
        right.pack(side="right", padx=5)
        
        bottom_frame = tk.LabelFrame(main, text="Stock Transactions List", font=('Arial', 10, 'bold'))
        bottom_frame.pack(side="bottom", fill="both", expand=True, padx=5, pady=5)

        # Calendar
        cal_lf = tk.LabelFrame(right, text="Calendar",
                               font=("Arial", 10, "bold"), bd=2, relief="groove",
                               width=400, height=300)
        cal_lf.pack(side="right", padx=(10, 0), pady=2)
        cal_lf.pack_propagate(False)


        self.sup_cal = Calendar(cal_lf, selectmode="day",
                                date_pattern="dd-mm-yyyy", font=("Arial", 10))
        self.sup_cal.pack(fill="both", expand=True, padx=5, pady=5)

        def _on_cal_select(event=None):
            selected = self.sup_cal.get_date()
            target = self.end_date if self.cal_target_var.get() == "end" else self.start_date
            target.delete(0, "end")
            target.insert(0, selected)
        self.sup_cal.bind("<<CalendarSelected>>", _on_cal_select)

        # Product List Treeview
        columns = ("Products Name",)
        self.product_tree = ttk.Treeview(left, columns=columns, show="headings", height=10)
        self.product_tree.pack(pady=10)
        self.product_tree.heading("Products Name", text="Products Name")
        self.product_tree.column("Products Name", width=120, anchor="center")
        if hasattr(self.app, 'setup_treeview_style'):
            self.app.setup_treeview_style(self.product_tree)
        else:
            self.product_tree.config(cursor="hand2")
            self.product_tree.tag_configure("evenrow", background="#E3F2FD", foreground="black")
            self.product_tree.tag_configure("oddrow", background="#F5F5F5", foreground="black")

        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)

        # Form Entries in Middle Frame
        tk.Label(middle, text="Start Date", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.start_date = tk.Entry(middle, width=15)
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(middle, text="End Date", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.end_date = tk.Entry(middle, width=15)
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        self.sr_start_date = self.start_date
        self.sr_end_date = self.end_date

        self.start_date.bind("<FocusIn>", lambda e: self.cal_target_var.set("start"))
        self.end_date.bind("<FocusIn>", lambda e: self.cal_target_var.set("end"))

        # Ctrl+; → insert today's date
        def _bind_date(entry_widget):
            def _today(event=None):
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, datetime.now().strftime("%d-%m-%Y"))
                return "break"
            entry_widget.bind("<Control-semicolon>", _today)
        _bind_date(self.start_date)
        _bind_date(self.end_date)

        tk.Label(middle, text="Opening Balance", font=('Arial', 10, 'bold')).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.opening_balance = tk.Entry(middle, width=15)
        self.opening_balance.grid(row=0, column=5, padx=5, pady=5)


        tk.Label(middle, text="Find Product", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.Find_product = tk.Entry(middle, width=15)
        self.Find_product.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(middle, text="SID", font=('Arial', 10, 'bold')).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.SID = tk.Entry(middle, width=15)
        self.SID.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(middle, text="Invoice No", font=('Arial', 10, 'bold')).grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.Invoice = tk.Entry(middle, width=15)
        self.Invoice.grid(row=1, column=5, padx=5, pady=5)

        tk.Label(middle, text="Invoice Details", font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.Invoice_detials = tk.Entry(middle, width=15)
        self.Invoice_detials.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(middle, text="Rate", font=('Arial', 10, 'bold')).grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.Rate = tk.Entry(middle, width=15)
        self.Rate.grid(row=2, column=3, padx=5, pady=5)

        tk.Label(middle, text="Clinic", font=('Arial', 10, 'bold')).grid(row=2, column=4, padx=5, pady=5, sticky="e")
        self.Clinic = tk.Entry(middle, width=15)
        self.Clinic.grid(row=2, column=5, padx=5, pady=5)

        tk.Label(middle, text="Particulars", font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.Particulars = tk.Entry(middle, width=15)
        self.Particulars.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(middle, text="Received Qty", font=('Arial', 10, 'bold')).grid(row=3, column=2, padx=5, pady=5, sticky="e")
        self.Received_qty = tk.Entry(middle, width=15)
        self.Received_qty.grid(row=3, column=3, padx=5, pady=5)

        tk.Label(middle, text="Used Qty", font=('Arial', 10, 'bold')).grid(row=3, column=4, padx=5, pady=5, sticky="e")
        self.Used_qty = tk.Entry(middle, width=15)
        self.Used_qty.grid(row=3, column=5, padx=5, pady=5)

        tk.Label(middle, text="Address", font=('Arial', 10, 'bold')).grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.Address = tk.Entry(middle, width=15)
        self.Address.grid(row=4, column=1, padx=5, pady=5)

        # Auto Calculated Fields
        self.balance_var = tk.StringVar(value="0")
        self.total_var = tk.StringVar(value="0.00")

        tk.Label(middle, text="Auto Balance", font=('Arial', 10, 'bold'), fg="darkgreen").grid(row=4, column=2, padx=5, pady=5, sticky="e")
        self.balance_entry = tk.Entry(middle, textvariable=self.balance_var, width=15, state="readonly", font=('Arial', 10, 'bold'))
        self.balance_entry.grid(row=4, column=3, padx=5, pady=5)

        tk.Label(middle, text="Auto Total", font=('Arial', 10, 'bold'), fg="darkblue").grid(row=4, column=4, padx=5, pady=5, sticky="e")
        self.total_entry = tk.Entry(middle, textvariable=self.total_var, width=15, state="readonly", font=('Arial', 10, 'bold'))
        self.total_entry.grid(row=4, column=5, padx=5, pady=5)

        # Live calculation on input typing
        for entry in [self.opening_balance, self.Received_qty, self.Used_qty, self.Rate]:
            entry.bind("<KeyRelease>", self.auto_calculate)

        # Action Buttons with Colors
        btn_frame = tk.Frame(middle)
        btn_frame.grid(row=5, column=0, columnspan=6, pady=10)

        btn_add = tk.Button(btn_frame, text="ADD", font=('Arial', 10, 'bold'), bg="#28a745", fg="white", width=10, relief="raised", cursor="hand2", command=self.add_stock)
        btn_add.pack(side="left", padx=5)

        btn_update = tk.Button(btn_frame, text="UPDATE", font=('Arial', 10, 'bold'), bg="#17a2b8", fg="white", width=10, relief="raised", cursor="hand2", command=self.update_stock)
        btn_update.pack(side="left", padx=5)

        btn_delete = tk.Button(btn_frame, text="DELETE", font=('Arial', 10, 'bold'), bg="#dc3545", fg="white", width=10, relief="raised", cursor="hand2", command=self.delete_stock)
        btn_delete.pack(side="left", padx=5)

        btn_clear = tk.Button(btn_frame, text="CLEAR", font=('Arial', 10, 'bold'), bg="#ffc107", fg="black", width=10, relief="raised", cursor="hand2", command=self.clear_stock)
        btn_clear.pack(side="left", padx=5)

        btn_close = tk.Button(btn_frame, text="Close", font=('Arial', 10, 'bold'), bg="#6c757d", fg="white", width=10, relief="raised", cursor="hand2", command=self._close_suppliers)
        btn_close.pack(side="left", padx=5)

        # Bottom Treeview with Balance & Total columns
        inv_columns = ("Date", "SID", "Invoice No", "Invoice Details", "Rate", "Clinic", "Address", "Particulars", "Received Qty", "Used Qty", "Balance", "Total")
        self.inv_tree = ttk.Treeview(bottom_frame, columns=inv_columns, show="headings")
        
        vsb = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.inv_tree.yview)
        hsb = ttk.Scrollbar(bottom_frame, orient="horizontal", command=self.inv_tree.xview)
        self.inv_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Auto Calculated Fields Bar at Bottom of inv_tree
        bottom_calc_frame = tk.Frame(bottom_frame, bg="#e9ecef", bd=2, relief="groove")
        bottom_calc_frame.pack(side="bottom", fill="x", padx=5, pady=5)

        self.total_rec_var = tk.StringVar(value="0")
        self.total_used_var = tk.StringVar(value="0")
        self.total_bal_var = tk.StringVar(value="0")
        self.grand_total_var = tk.StringVar(value="0.00")

        tk.Label(bottom_calc_frame, text="Auto Calculated Totals:", font=('Arial', 9, 'bold'), bg="#e9ecef", fg="navy").pack(side="left", padx=10)

        tk.Label(bottom_calc_frame, text="Total Received:", font=('Arial', 9, 'bold'), bg="#e9ecef").pack(side="left", padx=(10, 2))
        tk.Entry(bottom_calc_frame, textvariable=self.total_rec_var, width=10, state="readonly", font=('Arial', 9, 'bold'), justify="center").pack(side="left", padx=(0, 15))

        tk.Label(bottom_calc_frame, text="Total Used:", font=('Arial', 9, 'bold'), bg="#e9ecef").pack(side="left", padx=(5, 2))
        tk.Entry(bottom_calc_frame, textvariable=self.total_used_var, width=10, state="readonly", font=('Arial', 9, 'bold'), justify="center").pack(side="left", padx=(0, 15))

        tk.Label(bottom_calc_frame, text="Total Balance:", font=('Arial', 9, 'bold'), bg="#e9ecef", fg="darkgreen").pack(side="left", padx=(5, 2))
        tk.Entry(bottom_calc_frame, textvariable=self.total_bal_var, width=10, state="readonly", font=('Arial', 9, 'bold'), justify="center").pack(side="left", padx=(0, 15))

        tk.Label(bottom_calc_frame, text="Grand Total (₹):", font=('Arial', 9, 'bold'), bg="#e9ecef", fg="darkblue").pack(side="left", padx=(5, 2))
        tk.Entry(bottom_calc_frame, textvariable=self.grand_total_var, width=12, state="readonly", font=('Arial', 9, 'bold'), justify="center").pack(side="left", padx=(0, 10))

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.inv_tree.pack(side="left", fill="both", expand=True)

        for col in inv_columns:
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=95, anchor="center")

        if hasattr(self.app, 'setup_treeview_style'):
            self.app.setup_treeview_style(self.inv_tree)
        else:
            self.inv_tree.config(cursor="hand2")
            self.inv_tree.tag_configure("evenrow", background="#E3F2FD", foreground="black")
            self.inv_tree.tag_configure("oddrow", background="#F5F5F5", foreground="black")

        self.inv_tree.bind("<<TreeviewSelect>>", self.on_inv_select)

        self.load_stock_data()

    def auto_calculate(self, event=None):
        try:
            open_bal = float(self.opening_balance.get()) if self.opening_balance.get().strip() else 0.0
            rec_qty = float(self.Received_qty.get()) if self.Received_qty.get().strip() else 0.0
            used_qty = float(self.Used_qty.get()) if self.Used_qty.get().strip() else 0.0
            rate = float(self.Rate.get()) if self.Rate.get().strip() else 0.0

            balance = open_bal + rec_qty - used_qty
            total = balance * rate

            self.balance_var.set(f"{balance:.2f}".rstrip('0').rstrip('.'))
            self.total_var.set(f"{total:.2f}")
            return balance, total
        except ValueError:
            return 0.0, 0.0

    def add_stock(self):
        try:
            selected_date = self.stock_cal.get_date()
        except Exception:
            selected_date = datetime.now().strftime("%d-%m-%Y")

        sid = self.SID.get().strip()
        inv_no = self.Invoice.get().strip()
        inv_det = self.Invoice_detials.get().strip()
        rate_str = self.Rate.get().strip()
        clinic = self.Clinic.get().strip()
        address = self.Address.get().strip()
        particulars = self.Particulars.get().strip()
        rec_str = self.Received_qty.get().strip()
        used_str = self.Used_qty.get().strip()
        prod = self.Find_product.get().strip()

        balance, total = self.auto_calculate()

        try:
            rate_val = float(rate_str) if rate_str else 0.0
            rec_val = float(rec_str) if rec_str else 0.0
            used_val = float(used_str) if used_str else 0.0

            conn = self.get_db_connection()
            c = conn.cursor()
            # Migrate DB if Address column missing
            try:
                c.execute("ALTER TABLE Stock_Register ADD COLUMN Address TEXT DEFAULT ''")
                conn.commit()
            except Exception:
                pass
            c.execute("""
                INSERT INTO Stock_Register (Date, SID, Invoice_No, Invoice_Details, Rate, Clinic, Address, Particulars, Received_Qty, Used_Qty, Balance, Total, Product_Name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (selected_date, sid, inv_no, inv_det, rate_val, clinic, address, particulars, rec_val, used_val, balance, total, prod))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Stock record added successfully!")
            self.clear_stock()
            self.load_stock_data()
        except ValueError:
            messagebox.showerror("Error", "Rate, Received Qty, and Used Qty must be numbers.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error adding stock: {e}")

    def update_stock(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record from table to update.")
            return

        item_tags = self.inv_tree.item(selected[0]).get('tags', [])
        item_id = item_tags[0] if item_tags else None

        try:
            selected_date = self.stock_cal.get_date()
        except Exception:
            selected_date = datetime.now().strftime("%d-%m-%Y")

        sid = self.SID.get().strip()
        inv_no = self.Invoice.get().strip()
        inv_det = self.Invoice_detials.get().strip()
        rate_str = self.Rate.get().strip()
        clinic = self.Clinic.get().strip()
        address = self.Address.get().strip()
        particulars = self.Particulars.get().strip()
        rec_str = self.Received_qty.get().strip()
        used_str = self.Used_qty.get().strip()
        prod = self.Find_product.get().strip()

        balance, total = self.auto_calculate()

        try:
            rate_val = float(rate_str) if rate_str else 0.0
            rec_val = float(rec_str) if rec_str else 0.0
            used_val = float(used_str) if used_str else 0.0

            conn = self.get_db_connection()
            c = conn.cursor()
            if item_id:
                c.execute("""
                    UPDATE Stock_Register SET Date=?, SID=?, Invoice_No=?, Invoice_Details=?, Rate=?, Clinic=?, Address=?, Particulars=?, Received_Qty=?, Used_Qty=?, Balance=?, Total=?, Product_Name=?
                    WHERE id=?
                """, (selected_date, sid, inv_no, inv_det, rate_val, clinic, address, particulars, rec_val, used_val, balance, total, prod, item_id))
            else:
                c.execute("""
                    UPDATE Stock_Register SET Rate=?, Clinic=?, Address=?, Particulars=?, Received_Qty=?, Used_Qty=?, Balance=?, Total=?
                    WHERE Date=? AND Invoice_No=?
                """, (rate_val, clinic, address, particulars, rec_val, used_val, balance, total, selected_date, inv_no))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Stock record updated successfully!")
            self.clear_stock()
            self.load_stock_data()
        except ValueError:
            messagebox.showerror("Error", "Numeric values required for Rate and Qty.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error updating stock: {e}")

    def delete_stock(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this stock record?"):
            return

        item_tags = self.inv_tree.item(selected[0]).get('tags', [])
        item_id = item_tags[0] if item_tags else None
        vals = self.inv_tree.item(selected[0])['values']

        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            if item_id:
                c.execute("DELETE FROM Stock_Register WHERE id=?", (item_id,))
            else:
                c.execute("DELETE FROM Stock_Register WHERE Date=? AND Invoice_No=?", (vals[0], vals[2]))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Stock record deleted successfully!")
            self.clear_stock()
            self.load_stock_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error deleting stock: {e}")

    def clear_stock(self):
        for entry in [self.start_date, self.end_date, self.opening_balance, self.Find_product, self.SID, self.Invoice, self.Invoice_detials, self.Rate, self.Clinic, self.Address, self.Particulars, self.Received_qty, self.Used_qty]:
            entry.delete(0, tk.END)
        self.balance_var.set("0")
        self.total_var.set("0.00")

    def on_inv_select(self, event):
        selected = self.inv_tree.selection()
        if not selected:
            return
        vals = self.inv_tree.item(selected[0])['values']
        if len(vals) >= 12:
            try:
                self.stock_cal.set_date(vals[0])
            except Exception:
                pass
            self.SID.delete(0, tk.END); self.SID.insert(0, str(vals[1] or ""))
            self.Invoice.delete(0, tk.END); self.Invoice.insert(0, str(vals[2] or ""))
            self.Invoice_detials.delete(0, tk.END); self.Invoice_detials.insert(0, str(vals[3] or ""))
            self.Rate.delete(0, tk.END); self.Rate.insert(0, str(vals[4] or ""))
            self.Clinic.delete(0, tk.END); self.Clinic.insert(0, str(vals[5] or ""))
            self.Address.delete(0, tk.END); self.Address.insert(0, str(vals[6] or ""))
            self.Particulars.delete(0, tk.END); self.Particulars.insert(0, str(vals[7] or ""))
            self.Received_qty.delete(0, tk.END); self.Received_qty.insert(0, str(vals[8] or ""))
            self.Used_qty.delete(0, tk.END); self.Used_qty.insert(0, str(vals[9] or ""))
            self.balance_var.set(str(vals[10] or "0"))
            self.total_var.set(str(vals[11] or "0.00"))

    def update_tree_totals(self):
        tot_rec = 0.0
        tot_used = 0.0
        tot_bal = 0.0
        grand_total = 0.0

        for child in self.inv_tree.get_children():
            vals = self.inv_tree.item(child)['values']
            if len(vals) >= 12:
                try:
                    tot_rec += float(vals[8]) if vals[8] is not None else 0.0
                except (ValueError, TypeError):
                    pass
                try:
                    tot_used += float(vals[9]) if vals[9] is not None else 0.0
                except (ValueError, TypeError):
                    pass
                try:
                    tot_bal += float(vals[10]) if vals[10] is not None else 0.0
                except (ValueError, TypeError):
                    pass
                try:
                    grand_total += float(vals[11]) if vals[11] is not None else 0.0
                except (ValueError, TypeError):
                    pass

        if hasattr(self, 'total_rec_var'):
            self.total_rec_var.set(f"{tot_rec:.2f}".rstrip('0').rstrip('.'))
        if hasattr(self, 'total_used_var'):
            self.total_used_var.set(f"{tot_used:.2f}".rstrip('0').rstrip('.'))
        if hasattr(self, 'total_bal_var'):
            self.total_bal_var.set(f"{tot_bal:.2f}".rstrip('0').rstrip('.'))
        if hasattr(self, 'grand_total_var'):
            self.grand_total_var.set(f"{grand_total:.2f}")

    def on_product_select(self, event):
        selected = self.product_tree.selection()
        if not selected:
            return
        prod_name = self.product_tree.item(selected[0])['values'][0]
        self.Find_product.delete(0, tk.END)
        self.Find_product.insert(0, str(prod_name))

        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            for item in self.inv_tree.get_children():
                self.inv_tree.delete(item)

            c.execute("SELECT id, Date, SID, Invoice_No, Invoice_Details, Rate, Clinic, Address, Particulars, Received_Qty, Used_Qty, Balance, Total FROM Stock_Register WHERE Product_Name=?", (prod_name,))
            for idx, row in enumerate(c.fetchall()):
                row_id = row[0]
                values = row[1:]
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.inv_tree.insert("", "end", values=values, tags=(row_id, tag))
            conn.close()
            self.update_tree_totals()
        except Exception:
            pass

    def load_stock_data(self):
        try:
            conn = self.get_db_connection()
            c = conn.cursor()

            for item in self.product_tree.get_children():
                self.product_tree.delete(item)

            prods = []
            try:
                c.execute("SELECT DISTINCT Product_Name FROM Medicines WHERE Product_Name IS NOT NULL AND Product_Name != ''")
                prods = [p[0] for p in c.fetchall()]
            except Exception:
                pass

            try:
                c.execute("SELECT DISTINCT Product_Name FROM Stock_Register WHERE Product_Name IS NOT NULL AND Product_Name != ''")
                for p in c.fetchall():
                    if p[0] not in prods:
                        prods.append(p[0])
            except Exception:
                pass

            for idx, p in enumerate(prods):
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.product_tree.insert("", "end", values=(p,), tags=(tag,))

            for item in self.inv_tree.get_children():
                self.inv_tree.delete(item)

            c.execute("SELECT id, Date, SID, Invoice_No, Invoice_Details, Rate, Clinic, Address, Particulars, Received_Qty, Used_Qty, Balance, Total FROM Stock_Register ORDER BY id DESC")
            for idx, row in enumerate(c.fetchall()):
                row_id = row[0]
                values = row[1:]
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.inv_tree.insert("", "end", values=values, tags=(row_id, tag))

            conn.close()
            self.update_tree_totals()
        except Exception:
            pass

    def on_stock_register_complete(self):
        try:
            selected_date = self.stock_cal.get_date()
        except Exception:
            selected_date = None

        start_val = ''
        end_val = ''
        try:
            start_val = self.start_date.get()
        except Exception:
            pass
        try:
            end_val = self.end_date.get()
        except Exception:
            pass

        info = selected_date or start_val or end_val or 'no date or range provided'
        messagebox.showinfo('Stock Register', f'Stock register completed for: {info}')
