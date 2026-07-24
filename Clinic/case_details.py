import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import sqlite3
import os

class Case_Details:
    def __init__(self, app):
        self.app = app
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        self.case_details()

    def close(self):
        self.app.files()

    def case_details(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        tk.Label(self.app.workspace, text="Case " + chr(38) + " Collection Details",
                 font=("Arial", 14, "bold"), fg="navy").pack(pady=10)

        main = tk.Frame(self.app.workspace)
        main.pack()

        top_frame = tk.Frame(main)
        top_frame.pack()

        left   = tk.Frame(top_frame); left.pack(side="left")
        middle = tk.Frame(top_frame); middle.pack(side="left")
        right  = tk.Frame(top_frame); right.pack(side="right")

        bottom_frame = tk.Frame(main)
        bottom_frame.pack()

        bm_left  = tk.Frame(bottom_frame); bm_left.pack(side="left")
        bm_right = tk.Frame(bottom_frame); bm_right.pack(side="right")

        self.stock_cal = Calendar(right, selectmode="day", date_pattern="dd-mm-yyyy")
        self.stock_cal.pack(padx=20, pady=20)

        btn_data = [
            ("All", 0, 0), ("Nation Wise", 0, 1),
            ("Treatment Report", 1, 0), ("Treatment Key Word wise", 1, 1),
            ("Treatment Register", 2, 0), ("Daily Cash Transactions", 2, 1),
            ("Not Paid List", 3, 0), ("Patient Balance", 3, 1),
            ("Collection Chart", 4, 0), ("Consultant Wise", 4, 1),
        ]
        for text, row, col in btn_data:
            tk.Button(left, text=text, font=("Arial", 12)).grid(row=row, column=col, padx=10, pady=10)

        tk.Label(middle, text="Start Date",          font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.start_date = tk.Entry(middle)
        self.start_date.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(middle, text="End Date",            font=("Arial", 12)).grid(row=0, column=2, padx=10, pady=10)
        self.end_date = tk.Entry(middle)
        self.end_date.grid(row=0, column=3, padx=10, pady=10)

        tk.Label(middle, text="Find Treatment Code", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        self.Find_treatment = tk.Entry(middle)
        self.Find_treatment.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(middle, text="Treatment Code",      font=("Arial", 12)).grid(row=1, column=2, padx=10, pady=10)
        self.SID = tk.Entry(middle)
        self.SID.grid(row=1, column=3, padx=10, pady=10)

        tk.Label(middle, text="Treatment",           font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
        self.Invoice = tk.Entry(middle)
        self.Invoice.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(middle, text="ADD",    font=("Arial", 12), command=getattr(self, "add_stock",    lambda: None)).grid(row=4, column=0, padx=10, pady=10)
        tk.Button(middle, text="DELETE", font=("Arial", 12), command=getattr(self, "delete_stock", lambda: None)).grid(row=4, column=1, padx=10, pady=10)
        tk.Button(middle, text="Close",  font=("Arial", 12), command=self.close).grid(row=4, column=2, padx=10, pady=10)
        tk.Button(middle, text="View Consultants Ledger", font=("Arial", 12), bg="red",
                  command=getattr(self, "view", lambda: None)).grid(row=5, column=2, padx=10, pady=10)

        tc_columns = ("Treatment Code", "Treatment")
        tc_tree = ttk.Treeview(bm_left, columns=tc_columns, show="headings",height=5)
        tc_tree.pack(pady=20)
        for col in tc_columns:
            tc_tree.heading(col, text=col)
            tc_tree.column(col, width=100)

        tk.Label(bm_right, text="Refby", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Entry(bm_right).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        tk.Button(bm_right, text="Previous").grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ref_columns = ("Patient id", "Name", "Tooth", "Address", "Contact No", "Mobile No")
        ref_tree = ttk.Treeview(bm_right, columns=ref_columns, show="headings",height=10)
        ref_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        for col in ref_columns:
            ref_tree.heading(col, text=col)
            ref_tree.column(col, width=100)

    def on_stock_register_complete(self):
        try:
            selected_date = self.stock_cal.get_date()
        except Exception:
            selected_date = None
        start_val = ""
        end_val = ""
        try: start_val = self.start_date.get()
        except Exception: pass
        try: end_val = self.end_date.get()
        except Exception: pass
        info = selected_date or start_val or end_val or "no date or range provided"
        messagebox.showinfo("Stock Register", f"Stock register completed for: {info}")