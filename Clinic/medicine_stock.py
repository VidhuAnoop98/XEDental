from PIL.ImageOps import expand
import xml.etree.ElementTree
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
from tkcalendar import Calendar

class MedicineStock:
    def __init__(self, materials_view):
        self.materials_view = materials_view
        self.app = materials_view.app
        self.root = self.app.root
        self._close_suppliers = materials_view._close_suppliers
        self.suppliers_register = materials_view.suppliers_register
        
        self.medicine_stock()

    def get_db_connection(self):
        if hasattr(self.materials_view, "get_db_connection"):
            return self.materials_view.get_db_connection()
        import os, sqlite3
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return sqlite3.connect(os.path.join(script_dir, "dental.db"))

    def _init_supplier_tables(self):
        if hasattr(self.materials_view, "_init_supplier_tables"):
            self.materials_view._init_supplier_tables()

    def medicine_stock(self):       
        self._init_supplier_tables()

        self.app.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)   
        title = tk.Label(self.workspace, text="Medicine Stock",
                         font=("Arial", 14, "bold"), fg="navy")
        title.pack(pady=(8, 4))

        # ── Main content ──────────────────────────────
        content_frame = tk.Frame(self.workspace)
        content_frame.pack(fill="both", expand=True, padx=6, pady=4)

        # ── TOP row: Supplier list | Form+Calendar ────
        top_frame = tk.Frame(content_frame)
        top_frame.pack(fill="both", expand=True)

        # --- Left: Supplier list ---
        left_lf = tk.LabelFrame(top_frame, text="Suppliers",
                                font=("Arial", 10, "bold"), bd=2, relief="groove")
        left_lf.pack(side="left", fill="both", padx=(0, 4), pady=4)

        # Add supplier entry + buttons
        sup_entry_frame = tk.Frame(left_lf)
        sup_entry_frame.pack(fill="x", padx=6, pady=(6, 2))

        sup_tree_frame = tk.Frame(left_lf)
        sup_tree_frame.pack(fill="both", expand=True, padx=6, pady=(2, 6))

        self.supplier_tree = ttk.Treeview(
            sup_tree_frame, columns=("ID", "Supplier Name", "Address"),
            show="headings", height=10
        )
        self.supplier_tree.heading("ID", text="ID")
        self.supplier_tree.heading("Supplier Name", text="Supplier Name")
        self.supplier_tree.heading("Address", text="Address")
        self.supplier_tree.column("ID", width=40, anchor="center")
        self.supplier_tree.column("Supplier Name", width=150, anchor="w")
        self.supplier_tree.column("Address", width=200, anchor="w")

        sup_vsb = ttk.Scrollbar(sup_tree_frame, orient="vertical",
                                command=self.supplier_tree.yview)
        self.supplier_tree.configure(yscrollcommand=sup_vsb.set)
        self.supplier_tree.pack(side="left", fill="both", expand=True)
        sup_vsb.pack(side="left", fill="y")

        if hasattr(self.app, 'setup_treeview_style'):
            self.app.setup_treeview_style(self.supplier_tree)
        else:
            self.supplier_tree.config(cursor="hand2")
            self.supplier_tree.tag_configure("evenrow", background="#E3F2FD", foreground="black")
            self.supplier_tree.tag_configure("oddrow", background="#F5F5F5", foreground="black")

        self.supplier_tree.bind("<<TreeviewSelect>>", self._on_supplier_select)

        # --- Middle: Form fields ---
        mid_lf = tk.LabelFrame(top_frame, text="Ledger Entry",
                               font=("Arial", 10, "bold"), bd=2, relief="groove")
        mid_lf.pack(side="left", expand=True, padx=4, pady=4)

        form = tk.Frame(mid_lf)
        form.pack(fill="x", padx=8, pady=6)

        labels_entries = [
            ("Start Date:",       "sr_start_date",  0, 0),
            ("End Date:",         "sr_end_date",    0, 2),
            ("Opening Balance:",  "sr_opening",     1, 0),
            ("Inv No:",           "sr_inv_no",      1, 2),
            ("Particulars:",      "sr_particulars",  2, 0),
            ("Receipt:",          "sr_receipt",      2, 2),
            ("Payment:",          "sr_payment",      3, 0),
        ]
        for lbl_text, attr, row, col in labels_entries:
            tk.Label(form, text=lbl_text, font=("Arial", 9)).grid(
                row=row, column=col, padx=(8, 2), pady=4, sticky="e")
            entry = tk.Entry(form, font=("Arial", 9), width=14)
            entry.grid(row=row, column=col + 1, padx=(0, 8), pady=4, sticky="w")
            setattr(self, attr, entry)

        # Ctrl+; → insert today's date into date fields
        def _bind_date(entry_widget):
            def _today(event=None):
                from datetime import datetime
                entry_widget.delete(0, "end")
                entry_widget.insert(0, datetime.now().strftime("%d-%m-%Y"))
                return "break"
            entry_widget.bind("<Control-semicolon>", _today)
        _bind_date(self.sr_start_date)
        _bind_date(self.sr_end_date)

        # Ledger entry buttons
        btn_row = tk.Frame(mid_lf)
        btn_row.pack(fill="x", padx=8, pady=4)
        btn_cfg = dict(font=("Arial", 9, "bold"), width=9, bd=2)
        tk.Button(btn_row, text="ADD ENTRY", bg="#2980B9", fg="white",
                  command=self._add_ledger_entry, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_row, text="DELETE", bg="#C0392B", fg="white",
                  command=self._delete_ledger_entry, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_row, text="REFRESH", bg="#16A085", fg="white",
                  command=self._refresh, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_row, text="CLOSE", bg="#7F8C8D", fg="white",
                  command=self._close_suppliers, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_row, text="Print", bg="#E74C3C", fg="white",
                  command=self._print_ledger, **btn_cfg).pack(side="left", padx=3)


        # --- Right: Calendar ---
        cal_lf = tk.LabelFrame(top_frame, text="Calendar",
                               font=("Arial", 10, "bold"), bd=2, relief="groove",
                               width=400, height=300)
        cal_lf.pack(side="right", padx=(10, 0), pady=2)
        cal_lf.pack_propagate(False)

        self.cal_target_var = tk.StringVar(value="start")

        def _on_start_focus(event=None):
            self.cal_target_var.set("start")
            val = self.sr_start_date.get().strip()
            if val:
                try:
                    dt_obj = datetime.strptime(val, "%d-%m-%Y")
                    self.sup_cal.selection_set(dt_obj)
                except Exception:
                    pass

        def _on_end_focus(event=None):
            self.cal_target_var.set("end")
            val = self.sr_end_date.get().strip()
            if val:
                try:
                    dt_obj = datetime.strptime(val, "%d-%m-%Y")
                    self.sup_cal.selection_set(dt_obj)
                except Exception:
                    pass

        self.sr_start_date.bind("<FocusIn>", _on_start_focus)
        self.sr_end_date.bind("<FocusIn>", _on_end_focus)

        self.sup_cal = Calendar(cal_lf, selectmode="day",
                                date_pattern="dd-mm-yyyy", font=("Arial", 10))
        self.sup_cal.pack(fill="both", expand=True, padx=5, pady=5)

        def _on_cal_select(event=None):
            selected = self.sup_cal.get_date()
            target = self.sr_end_date if self.cal_target_var.get() == "end" else self.sr_start_date
            target.delete(0, "end")
            target.insert(0, selected)
        self.sup_cal.bind("<<CalendarSelected>>", _on_cal_select)

        # ── BOTTOM row: Ledger table | Product table ──
        bottom_frame = tk.Frame(content_frame)
        bottom_frame.pack(fill="both", expand=True, pady=(4, 0))

        # --- Left bottom: Ledger entries ---
        ledger_lf = tk.LabelFrame(bottom_frame, text="Ledger Entries",
                                  font=("Arial", 10, "bold"), bd=2, relief="groove")
        ledger_lf.pack(side="left", fill="both", expand=True, padx=(0, 4), pady=4)

        ledger_cols = ("Date", "Inv No", "Particulars", "Receipt", "Payment")
        ledger_widths = (90, 80, 160, 90, 90)

        ledger_tf = tk.Frame(ledger_lf)
        ledger_tf.pack(fill="both", expand=True, padx=6, pady=6)

        self.ledger_tree = ttk.Treeview(
            ledger_tf, columns=ledger_cols, show="headings", height=10
        )
        for col, w in zip(ledger_cols, ledger_widths):
            self.ledger_tree.heading(col, text=col)
            self.ledger_tree.column(col, width=w, anchor="w")

        ledger_vsb = ttk.Scrollbar(ledger_tf, orient="vertical",
                                   command=self.ledger_tree.yview)
        self.ledger_tree.configure(yscrollcommand=ledger_vsb.set)
        self.ledger_tree.pack(side="left", fill="both", expand=True)
        ledger_vsb.pack(side="left", fill="y")

        if hasattr(self.app, 'setup_treeview_style'):
            self.app.setup_treeview_style(self.ledger_tree)
        else:
            self.ledger_tree.config(cursor="hand2")
            self.ledger_tree.tag_configure("evenrow", background="#E3F2FD", foreground="black")
            self.ledger_tree.tag_configure("oddrow", background="#F5F5F5", foreground="black")

        # Summary labels
        sum_frame = tk.Frame(ledger_lf)
        sum_frame.pack(fill="x", padx=6, pady=(0, 4))
        self.lbl_total_receipt = tk.Label(sum_frame, text="Total Receipt: 0.00",
                                          font=("Arial", 9, "bold"), fg="#27AE60")
        self.lbl_total_receipt.pack(side="left", padx=8)
        self.lbl_total_payment = tk.Label(sum_frame, text="Total Payment: 0.00",
                                          font=("Arial", 9, "bold"), fg="#C0392B")
        self.lbl_total_payment.pack(side="left", padx=8)
        self.lbl_balance = tk.Label(sum_frame, text="Balance: 0.00",
                                    font=("Arial", 9, "bold"), fg="navy")
        self.lbl_balance.pack(side="right", padx=8)

        # --- Right bottom: Product details ---
        product_lf = tk.LabelFrame(bottom_frame, text="Product Details",
                                   font=("Arial", 10, "bold"), bd=2, relief="groove")
        product_lf.pack(side="right", fill="both", expand=True, padx=(4, 0), pady=4)

        prod_cols = ("Product", "PRate","SRate", "Qty", "Amount")
        prod_widths = (150, 80, 80, 60, 90)

        prod_tf = tk.Frame(product_lf)
        prod_tf.pack(fill="both", expand=True, padx=6, pady=6)

        self.product_tree = ttk.Treeview(
            prod_tf, columns=prod_cols, show="headings", height=10
        )
        for col, w in zip(prod_cols, prod_widths):
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=w, anchor="w")

        prod_vsb = ttk.Scrollbar(prod_tf, orient="vertical",
                                 command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=prod_vsb.set)
        self.product_tree.pack(side="left", fill="both", expand=True)
        prod_vsb.pack(side="left", fill="y")

        if hasattr(self.app, 'setup_treeview_style'):
            self.app.setup_treeview_style(self.product_tree)
        else:
            self.product_tree.config(cursor="hand2")
            self.product_tree.tag_configure("evenrow", background="#E3F2FD", foreground="black")
            self.product_tree.tag_configure("oddrow", background="#F5F5F5", foreground="black")

        # Track selected supplier
        self._selected_supplier_id = None

        # Load initial data
        self._load_suppliers()

    # ── Supplier CRUD helpers ─────────────────────────
    def _load_suppliers(self):
        for ch in self.supplier_tree.get_children():
            self.supplier_tree.delete(ch)
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            try:
                c.execute("ALTER TABLE Suppliers ADD COLUMN Address TEXT DEFAULT ''")
                conn.commit()
            except Exception:
                pass
            c.execute("SELECT id, Supplier_Name, Address FROM Suppliers ORDER BY id ASC")
            for idx, row in enumerate(c.fetchall()):
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.supplier_tree.insert("", "end", iid=str(row[0]),
                                         values=(row[0], row[1], row[2] or ""),
                                         tags=(tag,))
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _add_supplier(self):
        if not hasattr(self, 'sup_name_entry'):
            return
        name = self.sup_name_entry.get().strip()
        address = self.sup_address_entry.get().strip() if hasattr(self, 'sup_address_entry') else ""
        if not name:
            messagebox.showwarning("Input", "Enter a supplier name.")
            return
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute(
                "INSERT OR IGNORE INTO Suppliers (Supplier_Name, Address) VALUES (?, ?)",
                (name, address)
            )
            conn.commit()
            conn.close()
            self.sup_name_entry.delete(0, "end")
            if hasattr(self, 'sup_address_entry'):
                self.sup_address_entry.delete(0, "end")
            self._load_suppliers()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _refresh(self):
        for attr in ("sr_start_date", "sr_end_date", "sr_opening", "sr_inv_no",
                     "sr_particulars", "sr_receipt", "sr_payment",
                     "sup_name_entry", "sup_address_entry"):
            if hasattr(self, attr):
                getattr(self, attr).delete(0, "end")
        self._selected_supplier_id = None
        for tree in (self.supplier_tree, self.ledger_tree, self.product_tree):
            if hasattr(self, tree.winfo_name()):
                try:
                    tree.selection_remove(tree.selection())
                except Exception:
                    pass
        self._load_suppliers()
        self._clear_ledger_table()
        self._clear_product_table()

    def _delete_supplier(self):
        sel = self.supplier_tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Select a supplier to delete.")
            return
        vals = self.supplier_tree.item(sel)["values"]
        if not messagebox.askyesno("Confirm", f"Delete supplier '{vals[1]}'?\nAll ledger entries will also be deleted."):
            return
        try:
            sid = int(sel)
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM Supplier_Ledger WHERE Supplier_ID=?", (sid,))
            c.execute("DELETE FROM Supplier_Products WHERE Supplier_ID=?", (sid,))
            c.execute("DELETE FROM Suppliers WHERE id=?", (sid,))
            conn.commit()
            conn.close()
            self._selected_supplier_id = None
            self._load_suppliers()
            self._clear_ledger_table()
            self._clear_product_table()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _on_supplier_select(self, event=None):
        sel = self.supplier_tree.focus()
        if not sel:
            return
        self._selected_supplier_id = int(sel)
        vals = self.supplier_tree.item(sel)["values"]
        if hasattr(self, 'sup_name_entry'):
            self.sup_name_entry.delete(0, "end")
            self.sup_name_entry.insert(0, vals[1])
        if hasattr(self, 'sup_address_entry'):
            self.sup_address_entry.delete(0, "end")
            self.sup_address_entry.insert(0, str(vals[2]) if len(vals) > 2 else "")
        self._load_ledger()
        self._load_products()

    # ── Ledger CRUD helpers ───────────────────────────
    def _load_ledger(self):
        self._clear_ledger_table()
        if not self._selected_supplier_id:
            return
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute(
                "SELECT id, Date, Inv_No, Particulars, Receipt, Payment "
                "FROM Supplier_Ledger WHERE Supplier_ID=? ORDER BY Date",
                (self._selected_supplier_id,)
            )
            total_r, total_p = 0.0, 0.0
            for idx, row in enumerate(c.fetchall()):
                rid, dt, inv, part, rcpt, pay = row
                rcpt = rcpt or 0
                pay = pay or 0
                total_r += rcpt
                total_p += pay
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.ledger_tree.insert("", "end", iid=str(rid),
                    values=(dt or "", inv or "", part or "",
                            f"{rcpt:.2f}", f"{pay:.2f}"),
                    tags=(tag,))
            conn.close()
            self.lbl_total_receipt.config(text=f"Total Receipt: {total_r:.2f}")
            self.lbl_total_payment.config(text=f"Total Payment: {total_p:.2f}")
            self.lbl_balance.config(text=f"Balance: {total_r - total_p:.2f}")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _clear_ledger_table(self):
        for ch in self.ledger_tree.get_children():
            self.ledger_tree.delete(ch)
        self.lbl_total_receipt.config(text="Total Receipt: 0.00")
        self.lbl_total_payment.config(text="Total Payment: 0.00")
        self.lbl_balance.config(text="Balance: 0.00")

    def _add_ledger_entry(self):
        if not self._selected_supplier_id:
            messagebox.showwarning("Select", "Select a supplier first.")
            return
        dt = self.sr_start_date.get().strip()
        inv = self.sr_inv_no.get().strip()
        part = self.sr_particulars.get().strip()
        try:
            rcpt = float(self.sr_receipt.get().strip() or 0)
        except ValueError:
            rcpt = 0
        try:
            pay = float(self.sr_payment.get().strip() or 0)
        except ValueError:
            pay = 0

        if not dt:
            messagebox.showwarning("Input", "Please select or enter a date.")
            return
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO Supplier_Ledger "
                "(Supplier_ID, Date, Inv_No, Particulars, Receipt, Payment) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (self._selected_supplier_id, dt, inv, part, rcpt, pay)
            )
            conn.commit()
            conn.close()
            for attr in ("sr_start_date", "sr_inv_no", "sr_particulars",
                         "sr_receipt", "sr_payment"):
                getattr(self, attr).delete(0, "end")
            self._load_ledger()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _delete_ledger_entry(self):
        sel = self.ledger_tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Select a ledger entry to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected ledger entry?"):
            return
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM Supplier_Ledger WHERE id=?", (int(sel),))
            conn.commit()
            conn.close()
            self._load_ledger()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _print_ledger(self):
        if not self._selected_supplier_id:
            messagebox.showwarning("Select", "Please select a supplier first.")
            return

        supplier_name = self.sup_name_entry.get().strip() if hasattr(self, 'sup_name_entry') else ""
        supplier_address = self.sup_address_entry.get().strip() if hasattr(self, 'sup_address_entry') else ""
        sup_info = f"{supplier_name} ---- {supplier_address}" if supplier_address else supplier_name

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            import os, sys
        except ImportError:
            messagebox.showerror("Error", "reportlab is not installed.")
            return

        file_path = "Supplier_Ledger.pdf"
        try:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=f"Ledger_{supplier_name}.pdf",
                title="Save Ledger PDF",
                filetypes=[("PDF files", "*.pdf")]
            )
            if not file_path:
                return
        except Exception:
            pass

        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2.0, height - 20*mm, "Medicine Supplier Ledger")

        c.setFont("Helvetica", 12)
        c.drawString(20*mm, height - 35*mm, f"Supplier: {sup_info}")
        c.drawString(width - 60*mm, height - 35*mm, f"Date: {datetime.now().strftime('%d-%m-%Y')}")

        # Table Header
        c.setFont("Helvetica-Bold", 10)
        y = height - 50*mm
        c.drawString(20*mm, y, "Date")
        c.drawString(45*mm, y, "Inv No")
        c.drawString(70*mm, y, "Particulars")
        c.drawString(140*mm, y, "Receipt")
        c.drawString(170*mm, y, "Payment")
        c.line(20*mm, y - 2*mm, width - 20*mm, y - 2*mm)

        y -= 8*mm
        c.setFont("Helvetica", 10)

        total_r = 0.0
        total_p = 0.0

        for child in self.ledger_tree.get_children():
            vals = self.ledger_tree.item(child)["values"]
            if y < 30*mm:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 20*mm

            dt_str, inv_str, part_str, r_str, p_str = vals
            try:
                total_r += float(r_str)
            except ValueError:
                pass
            try:
                total_p += float(p_str)
            except ValueError:
                pass

            c.drawString(20*mm, y, str(dt_str))
            c.drawString(45*mm, y, str(inv_str))
            c.drawString(70*mm, y, str(part_str)[:35])
            c.drawString(140*mm, y, str(r_str))
            c.drawString(170*mm, y, str(p_str))
            y -= 6*mm

        c.line(20*mm, y + 2*mm, width - 20*mm, y + 2*mm)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70*mm, y, "Total:")
        c.drawString(140*mm, y, f"{total_r:.2f}")
        c.drawString(170*mm, y, f"{total_p:.2f}")

        y -= 6*mm
        balance = total_r - total_p
        c.drawString(70*mm, y, "Balance:")
        c.drawString(140*mm, y, f"{balance:.2f}")

        c.save()

        try:
            if sys.platform == "win32":
                import os
                os.startfile(file_path)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.call(["open", file_path])
            else:
                import subprocess
                subprocess.call(["xdg-open", file_path])
        except Exception:
            messagebox.showinfo("Success", f"PDF saved as {file_path}")

    # ── Product helpers ───────────────────────────────
    def _load_products(self):
        self._clear_product_table()
        if not self._selected_supplier_id:
            return
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            try:
                c.execute("ALTER TABLE Supplier_Products ADD COLUMN PRate REAL DEFAULT 0")
            except Exception:
                pass
            try:
                c.execute("ALTER TABLE Supplier_Products ADD COLUMN SRate REAL DEFAULT 0")
            except Exception:
                pass
            c.execute(
                "SELECT Product, Rate, PRate, SRate, Qty, Amount "
                "FROM Supplier_Products WHERE Supplier_ID=? ORDER BY Product",
                (self._selected_supplier_id,)
            )
            for idx, row in enumerate(c.fetchall()):
                prod, rate, prate, srate, qty, amt = row
                prate_val = prate if (prate is not None and prate != 0) else (rate or 0)
                srate_val = srate if srate is not None else 0.0
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.product_tree.insert("", "end",
                    values=(prod or "", f"{prate_val:.2f}", f"{srate_val:.2f}",
                            qty or 0, f"{amt or 0:.2f}"),
                    tags=(tag,))
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _clear_product_table(self):
        for ch in self.product_tree.get_children():
            self.product_tree.delete(ch)
