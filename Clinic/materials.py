from PIL.ImageOps import expand
import xml.etree.ElementTree
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
from tkcalendar import Calendar


class Materials:
    def __init__(self, app):
        self.app = app
        self.root = app.root

        app.clear_workspace()
        app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        buttons = [
            ("Suppliers Register",self.suppliers_register),
            ("Stock Register",self.stock_register),
            ("Medicine Stock",self.medicine_stock)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(app.workspace, text=text, font=('Arial', 11), width=22,command=command)
            btn.place(x=200, y=280 + i * 45)

    def get_db_connection(self):
        if hasattr(self.app, "get_db_connection"):
            return self.app.get_db_connection()
        import os, sqlite3
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return sqlite3.connect(os.path.join(script_dir, "dental.db"))

    def _init_supplier_tables(self):
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS Suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Supplier_Name TEXT UNIQUE NOT NULL,
                    Address TEXT,
                    Phone TEXT,
                    Opening_Balance REAL DEFAULT 0
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS Supplier_Ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Supplier_ID INTEGER NOT NULL,
                    Date TEXT,
                    Inv_No TEXT,
                    Particulars TEXT,
                    Receipt REAL DEFAULT 0,
                    Payment REAL DEFAULT 0,
                    FOREIGN KEY (Supplier_ID) REFERENCES Suppliers(id)
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS Supplier_Products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Supplier_ID INTEGER NOT NULL,
                    Product TEXT,
                    Rate REAL DEFAULT 0,
                    Qty INTEGER DEFAULT 0,
                    Amount REAL DEFAULT 0,
                    FOREIGN KEY (Supplier_ID) REFERENCES Suppliers(id)
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def suppliers_register(self):
        from suppliers_register import Suppliers_Register
        Suppliers_Register(self)
        
    def stock_register(self):
        from stock_register import Stock_Register
        Stock_Register(self)

    def medicine_stock(self):
        from medicine_stock import MedicineStock
        MedicineStock(self)

    def _close_suppliers(self):
        Materials(self.app)