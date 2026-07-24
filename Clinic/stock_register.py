from PIL.ImageOps import expand
import xml.etree.ElementTree
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
from tkcalendar import Calendar

class Stock_Register:
    def __init__(self, materials_view):
        self.materials_view = materials_view
        self.app = materials_view.app
        self.root = self.app.root
        self._close_suppliers = materials_view._close_suppliers
        self.stock_register()

    def stock_register(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        title = tk.Label(self.app.workspace, text="Stock Register", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=10)

        main = tk.Frame(self.app.workspace)
        main.pack()

        top_frame = tk.Frame(main)
        top_frame.pack()

        left = tk.Frame(top_frame)
        left.pack(side="left")

        middle = tk.Frame(top_frame)
        middle.pack(side="left")

        right = tk.Frame(top_frame)
        right.pack(side="right")
        
        bottom_frame = tk.Frame(main)
        bottom_frame.pack()

        # Calendar (keep as an instance attribute so handler can access it)
        self.stock_cal = Calendar(right, selectmode="day", date_pattern="dd-mm-yyyy")
        self.stock_cal.pack(padx=20, pady=20)

        columns = ("Products Name",)
        tree = ttk.Treeview(left, columns=columns, show="headings")
        tree.pack(pady=20)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tk.Label(middle, text="Start Date", font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=10)
        self.start_date = tk.Entry(middle)
        self.start_date.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(middle, text="End Date", font=('Arial', 12)).grid(row=0, column=2, padx=10, pady=10)
        self.end_date = tk.Entry(middle)
        self.end_date.grid(row=0, column=3, padx=10, pady=10)

        tk.Label(middle, text="Opening Balance", font=('Arial', 12)).grid(row=0, column=4, padx=10, pady=10)
        self.opening_balance = tk.Entry(middle)
        self.opening_balance.grid(row=0, column=5, padx=10, pady=10)

        tk.Label(middle, text="Find Product", font=('Arial', 12)).grid(row=1, column=0, padx=10, pady=10)
        self.Find_product = tk.Entry(middle)
        self.Find_product.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(middle, text="SID", font=('Arial', 12)).grid(row=1, column=2, padx=10, pady=10)
        self.SID = tk.Entry(middle)
        self.SID.grid(row=1, column=3, padx=10, pady=10)

        tk.Label(middle, text="Invoice No", font=('Arial', 12)).grid(row=1, column=4, padx=10, pady=10)
        self.Invoice = tk.Entry(middle)
        self.Invoice.grid(row=1, column=5, padx=10, pady=10)

        tk.Label(middle, text="Invoice Details", font=('Arial', 12)).grid(row=2, column=0, padx=10, pady=10)
        self.Invoice_detials = tk.Entry(middle)
        self.Invoice_detials.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(middle, text="Rate", font=('Arial', 12)).grid(row=2, column=2, padx=10, pady=10)
        self.Rate = tk.Entry(middle)
        self.Rate.grid(row=2, column=3, padx=10, pady=10)

        tk.Label(middle, text="Clinic", font=('Arial', 12)).grid(row=2, column=4, padx=10, pady=10)
        self.Clinic = tk.Entry(middle)
        self.Clinic.grid(row=2, column=5, padx=10, pady=10)

        tk.Label(middle, text="Particulars", font=('Arial', 12)).grid(row=3, column=0, padx=10, pady=10)
        self.Particulars = tk.Entry(middle)
        self.Particulars.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(middle, text="Received Qty", font=('Arial', 12)).grid(row=3, column=2, padx=10, pady=10)
        self.Received_qty = tk.Entry(middle)
        self.Received_qty.grid(row=3, column=3, padx=10, pady=10)

        tk.Label(middle, text="Used Qty", font=('Arial', 12)).grid(row=3, column=4, padx=10, pady=10)
        self.Used_qty = tk.Entry(middle)
        self.Used_qty.grid(row=3, column=5, padx=10, pady=10)

        btn_add = tk.Button(middle, text="ADD", font=('Arial', 12), command=getattr(self, 'add_stock', lambda: None))
        btn_add.grid(row=4, column=0, padx=10, pady=10)

        btn_delete = tk.Button(middle, text="DELETE", font=('Arial', 12), command=getattr(self, 'delete_stock', lambda: None))
        btn_delete.grid(row=4, column=1, padx=10, pady=10)

        btn_clear = tk.Button(middle, text="CLEAR", font=('Arial', 12), command=getattr(self, 'clear_stock', lambda: None))
        btn_clear.grid(row=4, column=2, padx=10, pady=10)

        btn_update = tk.Button(middle, text="UPDATE", font=('Arial', 12), command=getattr(self, 'update_stock', lambda: None))
        btn_update.grid(row=4, column=3, padx=10, pady=10)

        btn_close = tk.Button(middle, text="Close", font=('Arial', 12), command=self._close_suppliers)
        btn_close.grid(row=4, column=4, padx=10, pady=10)


        inv_columns = ("Date", "SID", "Invoice No", "Invoice Detials", "Rate", "Clinic", "Particulars", "Received Qty", "Used Qty")
        inv_tree = ttk.Treeview(bottom_frame, columns=inv_columns, show="headings")
        inv_tree.pack(pady=20)
        for col in inv_columns:
            inv_tree.heading(col, text=col)
            inv_tree.column(col, width=100)

    def on_stock_register_complete(self):
        # Read the calendar and form fields and show a simple confirmation
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
