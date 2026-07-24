import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import sqlite3
import os
import sys

CLINIC_DIR = os.path.dirname(os.path.abspath(__file__))
if CLINIC_DIR not in sys.path:
    sys.path.insert(0, CLINIC_DIR)

def get_db_connection(app=None):
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))


class Files:
    def __init__(self, app):
        self.app = app
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        buttons = [
            ("Patient Details", self.patient_details),
            ("Case " + chr(38) + " Collection Details", self.case_details),
            ("Patients Dues", self.patients_dues)
        ]
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(app.workspace, text=text, font=('Arial', 11), width=22, command=command)
            btn.place(x=40, y=280 + i * 45)

    def patient_details(self):
        from patient_details import Patient_Details
        Patient_Details(self.app)

    def case_details(self):
        from case_details import Case_Details
        Case_Details(self.app)

    def patients_dues(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        self.right_frame = tk.Frame(self.workspace, bd=2, relief="groove")
        self.right_frame.pack(side="right", padx=(200, 50), pady=50, fill="both", expand=True)

        column = (
            "Patient ID", "Name", "Address1", "Address2",
            "Mobile Number1", "Mobile Number2",
            "Sum of CR", "Sum of DR", "Balance"
        )
        tree = ttk.Treeview(self.right_frame, columns=column, show="headings", height=22)
        tree.pack(pady=20)
        widths = (150, 150, 150, 150, 100, 100, 100, 100, 100)
        for col, w in zip(column, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w)

        bottom_frame = tk.Frame(self.right_frame)
        bottom_frame.pack(side="bottom", padx=10, pady=10)
        tk.Button(bottom_frame, text="CLOSE", font=("Arial", 12), command=self.close).grid(row=1, column=0, padx=10, pady=10)
        tk.Button(bottom_frame, text="PRINT", font=("Arial", 12), command=self.print_report).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(bottom_frame, text="EXCEL", font=("Arial", 12), command=self.excel).grid(row=1, column=2, padx=10, pady=10)
        tk.Button(bottom_frame, text="CSV",   font=("Arial", 12), command=self.csv).grid(row=1, column=3, padx=10, pady=10)

    def print_report(self):
        messagebox.showinfo("Print", "Print")

    def excel(self):
        messagebox.showinfo("Excel", "Excel")

    def csv(self):
        messagebox.showinfo("CSV", "CSV")

    def close(self):
        self.app.files()