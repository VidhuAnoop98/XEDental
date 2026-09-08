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
            btn.place(x=200, y=280 + i * 45)

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

        title_lbl = tk.Label(self.workspace, text="Patients Dues Statement", font=("Arial", 14, "bold"))
        title_lbl.pack(side="top", pady=10)

        self.right_frame = tk.Frame(self.workspace, bd=2, relief="groove")
        self.right_frame.pack(side="top", padx=20, pady=10, fill="both", expand=True)

        column = (
            "Patient ID", "Name", "Address1", "Address2",
            "Mobile Number1", "Mobile Number2",
            "Sum of CR", "Sum of DR", "Balance"
        )
        tree = ttk.Treeview(self.right_frame, columns=column, show="headings", height=18)
        self.dues_tree = tree

        vsb = ttk.Scrollbar(self.right_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(self.right_frame, orient="horizontal", command=tree.xview)
        hsb.pack(side="bottom", fill="x")
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.pack(side="left", fill="both", expand=True)

        widths = (90, 150, 150, 150, 110, 110, 100, 100, 100)
        for col, w in zip(column, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center" if "ID" in col or "Mobile" in col else ("e" if "Sum" in col or "Balance" in col else "w"))

        tree.tag_configure("due_row", foreground="#D32F2F")
        tree.tag_configure("clear_row", foreground="#2E7D32")

        self.load_patients_dues_data()

        def on_dues_select(event):
            selected = tree.selection()
            if not selected:
                return
            vals = tree.item(selected[0])["values"]
            if vals and len(vals) > 0:
                patient_id = vals[0]
                if hasattr(self.app, 'registration'):
                    self.app.registration(patient_id)

        tree.bind("<Double-1>", on_dues_select)

        bottom_frame = tk.Frame(self.workspace)
        bottom_frame.pack(side="bottom", padx=10, pady=10)
        tk.Button(bottom_frame, text="CLOSE", font=("Arial", 11, "bold"), bg="#7F8C8D", fg="white", command=self.close).grid(row=1, column=0, padx=10, pady=5)
        tk.Button(bottom_frame, text="PRINT", font=("Arial", 11, "bold"), bg="#2980B9", fg="white", command=self.print_report).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(bottom_frame, text="EXCEL", font=("Arial", 11, "bold"), bg="#27AE60", fg="white", command=self.excel).grid(row=1, column=2, padx=10, pady=5)
        tk.Button(bottom_frame, text="CSV",   font=("Arial", 11, "bold"), bg="#16A085", fg="white", command=self.csv).grid(row=1, column=3, padx=10, pady=5)

    def load_patients_dues_data(self):
        if not hasattr(self, 'dues_tree') or not self.dues_tree:
            return
        for item in self.dues_tree.get_children():
            self.dues_tree.delete(item)

        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, Patient_Name, Address1, Address2, Mobile_Number1, Mobile_Number2
                FROM Appointments
                ORDER BY id ASC
            """)
            patients = cursor.fetchall()

            for pid, name, addr1, addr2, mob1, mob2 in patients:
                pid_str = str(pid).strip()
                reg_str = f"REG-{int(pid_str):04d}" if pid_str.isdigit() else pid_str

                cursor.execute("""
                    SELECT SUM(COALESCE(ba.Debit, 0)), SUM(COALESCE(ba.Credit, 0))
                    FROM Bill_Accounts ba
                    JOIN Bills b ON ba.Bill_ID = b.id
                    WHERE b.Patient_ID = ? OR b.Reg_No = ?
                """, (pid_str, reg_str))
                acc_row = cursor.fetchone()
                
                sum_dr = float(acc_row[0]) if acc_row and acc_row[0] is not None else 0.0
                sum_cr = float(acc_row[1]) if acc_row and acc_row[1] is not None else 0.0
                
                if sum_dr == 0.0 and sum_cr == 0.0:
                    cursor.execute("""
                        SELECT SUM(COALESCE(Total_Amount, 0)), SUM(COALESCE(Balance_Due, 0))
                        FROM Bills
                        WHERE Patient_ID = ? OR Reg_No = ?
                    """, (pid_str, reg_str))
                    b_row = cursor.fetchone()
                    if b_row and (b_row[0] is not None or b_row[1] is not None):
                        total_amt = float(b_row[0]) if b_row[0] is not None else 0.0
                        bal_due = float(b_row[1]) if b_row[1] is not None else 0.0
                        sum_dr = total_amt
                        sum_cr = total_amt - bal_due

                balance = sum_dr - sum_cr
                tag = "due_row" if balance > 0 else "clear_row"

                formatted_pid = str(pid)
                try:
                    from registration import Registration
                    r_obj = Registration.__new__(Registration)
                    r_obj.app = self.app
                    formatted_pid = r_obj.format_patient_id(pid)
                except Exception:
                    pass

                self.dues_tree.insert(
                    "", "end",
                    values=(
                        formatted_pid,
                        name or "",
                        addr1 or "",
                        addr2 or "",
                        mob1 or "",
                        mob2 or "",
                        f"{sum_cr:.2f}",
                        f"{sum_dr:.2f}",
                        f"{balance:.2f}"
                    ),
                    tags=(tag,)
                )
            conn.close()
        except Exception as e:
            print(f"Error loading patients dues data: {e}")

    def print_report(self):
        try:
            from tkinter import filedialog
            path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt"), ("All Files", "*.*")])
            if not path:
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write("PATIENT DUES REPORT\n")
                f.write("=" * 100 + "\n")
                f.write(f"{'ID':<8} {'Name':<20} {'Mobile':<15} {'Sum CR':<12} {'Sum DR':<12} {'Balance':<12}\n")
                f.write("-" * 100 + "\n")
                for child in self.dues_tree.get_children():
                    v = self.dues_tree.item(child)["values"]
                    f.write(f"{v[0]:<8} {str(v[1]):<20} {str(v[4]):<15} {str(v[6]):<12} {str(v[7]):<12} {str(v[8]):<12}\n")
            messagebox.showinfo("Print Report", f"Report saved successfully to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not print report: {e}")

    def excel(self):
        self.csv()

    def csv(self):
        try:
            import csv
            from tkinter import filedialog
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv"), ("All Files", "*.*")])
            if not path:
                return
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Patient ID", "Name", "Address1", "Address2", "Mobile 1", "Mobile 2", "Sum of CR", "Sum of DR", "Balance"])
                for child in self.dues_tree.get_children():
                    writer.writerow(self.dues_tree.item(child)["values"])
            messagebox.showinfo("Export CSV", f"Data exported successfully to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export CSV: {e}")

    def close(self):
        self.app.files()