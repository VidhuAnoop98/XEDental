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
        
        # Stubs for missing methods if they don't exist yet
        self._add_ledger_entry = getattr(self, '_add_ledger_entry', lambda: None)
        self._delete_ledger_entry = getattr(self, '_delete_ledger_entry', lambda: None)
        self._print_ledger = getattr(self, '_print_ledger', lambda: None)
        self._on_supplier_select = getattr(self, '_on_supplier_select', lambda e: None)
        self._load_suppliers = getattr(self, '_load_suppliers', lambda: None)
        
        self.medicine_stock()
        
    def medicine_stock(self):       
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)   
        title = tk.Label(self.workspace, text="Medicine Supplier Ledger",
                         font=("Arial", 14, "bold"), fg="navy")
        title.pack(pady=(8, 4))

        # ── Main content ──────────────────────────────
        content_frame = tk.Frame(self.workspace)
        content_frame.pack(fill="both", expand=True, padx=6, pady=4)

        # ── TOP row: Supplier list | Form+Calendar ────
        top_frame = tk.Frame(content_frame)
        top_frame.pack(fill="both", expand=True)

        # --- Left: Supplier list ---
        left_lf = tk.LabelFrame(top_frame, 
                                font=("Arial", 10, "bold"), bd=2, relief="groove")
        left_lf.pack(side="left", fill="both", padx=(0, 4), pady=4)

        # Add supplier entry + buttons
        sup_entry_frame = tk.Frame(left_lf)
        sup_entry_frame.pack(fill="x", padx=6, pady=(6, 2))
        tk.Button(sup_entry_frame, text="Supplier Ledger", font=("Arial", 9, "bold"), width=12,
                  bg="#27AE60", fg="white",
                  command=self.suppliers_register).pack(side="left", padx=2)

        sup_tree_frame = tk.Frame(left_lf)
        sup_tree_frame.pack(fill="both", expand=True, padx=6, pady=(2, 6))

        self.supplier_tree = ttk.Treeview(
            sup_tree_frame, columns=("ID", "Supplier Name"),
            show="headings", height=10
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
        cal_lf.pack(side="right", fill="y", padx=(4, 0), pady=2)

        self.sup_cal = Calendar(cal_lf, selectmode="day",
                                date_pattern="dd-mm-yyyy", font=("Arial", 10),width=500)
        self.sup_cal.pack(fill="both", expand=True, padx=20, pady=10)

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

        # Track selected supplier
        self._selected_supplier_id = None

        # Load initial data
        self._load_suppliers()
