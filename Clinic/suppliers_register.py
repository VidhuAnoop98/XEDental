from PIL.ImageOps import expand
import xml.etree.ElementTree
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
from tkcalendar import Calendar

class Suppliers_Register:
    def __init__(self, materials_view):
        self.materials_view = materials_view
        self.app = materials_view.app
        self.root = self.app.root
        self.get_db_connection = materials_view.get_db_connection
        self._init_supplier_tables = materials_view._init_supplier_tables
        self._close_suppliers = materials_view._close_suppliers
        self.suppliers_register()

    def suppliers_register(self):
        self._init_supplier_tables()

        self.app.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        # ── Title ──────────────────────────────────────
        title = tk.Label(self.workspace, text="Suppliers Ledger",
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
        self.sup_name_entry = tk.Entry(sup_entry_frame, font=("Arial", 10), width=20)
        self.sup_name_entry.pack(side="left", padx=(0, 4))
        tk.Button(sup_entry_frame, text="ADD", font=("Arial", 9, "bold"), width=6,
                  bg="#27AE60", fg="white",
                  command=self._add_supplier).pack(side="left", padx=2)
        tk.Button(sup_entry_frame, text="DEL", font=("Arial", 9, "bold"), width=6,
                  bg="#C0392B", fg="white",
                  command=self._delete_supplier).pack(side="left", padx=2)

        sup_tree_frame = tk.Frame(left_lf)
        sup_tree_frame.pack(fill="both", expand=True, padx=6, pady=(2, 6))

        self.supplier_tree = ttk.Treeview(
            sup_tree_frame, columns=("ID", "Supplier Name"),
            show="headings", height=14
        )
        self.supplier_tree.heading("ID", text="ID")
        self.supplier_tree.heading("Supplier Name", text="Supplier Name")
        self.supplier_tree.column("ID", width=40, anchor="center")
        self.supplier_tree.column("Supplier Name", width=180, anchor="w")

        sup_vsb = ttk.Scrollbar(sup_tree_frame, orient="vertical",
                                command=self.supplier_tree.yview)
        self.supplier_tree.configure(yscrollcommand=sup_vsb.set)
        self.supplier_tree.pack(side="left", fill="both", expand=True)
        sup_vsb.pack(side="left", fill="y")

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

        # Ledger entry buttons
        btn_row = tk.Frame(mid_lf)
        btn_row.pack(fill="x", padx=8, pady=4)
        btn_cfg = dict(font=("Arial", 9, "bold"), width=9, bd=2)
        tk.Button(btn_row, text="ADD ENTRY", bg="#2980B9", fg="white",
                  command=self._add_ledger_entry, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_row, text="DELETE", bg="#C0392B", fg="white",
                  command=self._delete_ledger_entry, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_row, text="CLOSE", bg="#7F8C8D", fg="white",
                  command=self._close_suppliers, **btn_cfg).pack(side="left", padx=3)
        tk.Button(btn_row, text="Print", bg="#E74C3C", fg="white",
                  command=self._print_ledger, **btn_cfg).pack(side="left", padx=3)


        # --- Right: Calendar ---
        cal_lf = tk.LabelFrame(top_frame,
                               font=("Arial", 10, "bold"), bd=2, relief="groove")
        cal_lf.pack(side="right", fill="y", padx=(4, 0), pady=4)

        self.sup_cal = Calendar(cal_lf, selectmode="day",
                                date_pattern="dd-mm-yyyy", font=("Arial", 10))
        self.sup_cal.pack(padx=8, pady=8)

        def _on_cal_select(event=None):
            selected = self.sup_cal.get_date()
            self.sr_start_date.delete(0, "end")
            self.sr_start_date.insert(0, selected)
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

        prod_cols = ("Product", "Rate", "Qty", "Amount")
        prod_widths = (150, 80, 60, 90)

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
            c.execute("SELECT id, Supplier_Name FROM Suppliers ORDER BY Supplier_Name")
            for row in c.fetchall():
                self.supplier_tree.insert("", "end", iid=str(row[0]),
                                         values=(row[0], row[1]))
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _add_supplier(self):
        name = self.sup_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input", "Enter a supplier name.")
            return
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO Suppliers (Supplier_Name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            self.sup_name_entry.delete(0, "end")
            self._load_suppliers()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

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
        self.sup_name_entry.delete(0, "end")
        self.sup_name_entry.insert(0, vals[1])
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
            for row in c.fetchall():
                rid, dt, inv, part, rcpt, pay = row
                rcpt = rcpt or 0
                pay = pay or 0
                total_r += rcpt
                total_p += pay
                self.ledger_tree.insert("", "end", iid=str(rid),
                    values=(dt or "", inv or "", part or "",
                            f"{rcpt:.2f}", f"{pay:.2f}"))
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
            # Clear entry fields
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

        supplier_name = self.sup_name_entry.get().strip()

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
        c.drawCentredString(width/2.0, height - 20*mm, "Supplier Ledger")

        c.setFont("Helvetica", 12)
        c.drawString(20*mm, height - 35*mm, f"Supplier: {supplier_name}")
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

        # Rows
        for child in self.ledger_tree.get_children():
            values = self.ledger_tree.item(child)["values"]
            dt = str(values[0]) if len(values) > 0 else ""
            inv = str(values[1]) if len(values) > 1 else ""
            part = str(values[2]) if len(values) > 2 else ""
            rcpt = str(values[3]) if len(values) > 3 else "0.00"
            pay = str(values[4]) if len(values) > 4 else "0.00"

            c.drawString(20*mm, y, dt)
            c.drawString(45*mm, y, inv)
            c.drawString(70*mm, y, part[:35]) # limit length
            c.drawString(140*mm, y, rcpt)
            c.drawString(170*mm, y, pay)

            try:
                total_r += float(rcpt) if rcpt else 0.0
                total_p += float(pay) if pay else 0.0
            except ValueError:
                pass

            y -= 6*mm
            if y < 20*mm:
                c.showPage()
                y = height - 20*mm
                c.setFont("Helvetica", 10)

        c.line(20*mm, y + 2*mm, width - 20*mm, y + 2*mm)
        y -= 6*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70*mm, y, "Totals:")
        c.drawString(140*mm, y, f"{total_r:.2f}")
        c.drawString(170*mm, y, f"{total_p:.2f}")

        y -= 6*mm
        balance = total_r - total_p
        c.drawString(70*mm, y, "Balance:")
        c.drawString(140*mm, y, f"{balance:.2f}")

        c.save()

        # open file
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.call(["open", file_path])
            else:
                import subprocess
                subprocess.call(["xdg-open", file_path])
        except Exception as e:
            messagebox.showinfo("Success", f"PDF saved as {file_path}")

    # ── Product helpers ───────────────────────────────
    def _load_products(self):
        self._clear_product_table()
        if not self._selected_supplier_id:
            return
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute(
                "SELECT Product, Rate, Qty, Amount "
                "FROM Supplier_Products WHERE Supplier_ID=? ORDER BY Product",
                (self._selected_supplier_id,)
            )
            for row in c.fetchall():
                self.product_tree.insert("", "end",
                    values=(row[0] or "", f"{row[1] or 0:.2f}",
                            row[2] or 0, f"{row[3] or 0:.2f}"))
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _clear_product_table(self):
        for ch in self.product_tree.get_children():
            self.product_tree.delete(ch)
    
    def close(self):
        self.app.materials()