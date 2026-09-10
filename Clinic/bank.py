import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

def get_db_connection(app=None):
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = getattr(app, "script_dir", os.path.dirname(os.path.abspath(__file__)))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))

class Bank:
    def __init__(self, accounts_view):
        self.accounts_view = accounts_view
        self.app = accounts_view.app
        self.root = self.app.root
        self.close = accounts_view.close
        
        self.bank_master()

    def get_db_connection(self):
        return get_db_connection(self.app)

    def bank_master(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        self.right_frame = tk.Frame(self.workspace, bd=2, relief="groove")
        self.right_frame.pack(side="right", padx=(20, 20), pady=20, fill="both", expand=True)

        title = tk.Label(self.right_frame, text="Bank Master", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=(10, 5))

        # Form outer frame
        form_outer = tk.LabelFrame(self.right_frame, text="Bank Details", font=('Arial', 10, 'bold'), padx=10, pady=5)
        form_outer.pack(padx=15, pady=5, fill="x")

        form = tk.Frame(form_outer)
        form.pack(padx=8, pady=6)

        fields = [
            ("Bank Code", "bb_bank_code", 0, 0, 1),
            ("Bank Name", "bb_bank_name", 0, 2, 3),
            ("Name", "bb_account_name", 0, 4, 5),
            ("Account Number", "bb_account_no", 1, 0, 1),
            ("Branch Name", "bb_branch", 1, 2, 3),
            ("IFSC Code", "bb_ifsc", 1, 4, 5),
            ("Opening Balance", "bb_balance", 2, 0, 1)
        ]

        for lbl_text, attr, row, col_lbl, col_ent in fields:
            tk.Label(form, text=lbl_text, font=("Arial", 9, "bold" if "Name" in lbl_text else "normal"), anchor="e").grid(
                row=row, column=col_lbl, padx=(8, 2), pady=4, sticky="e"
            )
            entry = tk.Entry(form, font=("Arial", 9), width=18)
            entry.grid(row=row, column=col_ent, padx=(0, 10), pady=4, sticky="w")
            setattr(self, attr, entry)

        # Treeview frame
        tree_frame = tk.Frame(self.right_frame)
        tree_frame.pack(padx=15, pady=5, fill="both", expand=True)

        col_bank = ("Bank ID", "Bank Code", "Bank Name", "Name", "Account Number", "Branch Name", "IFSC Code", "Balance (₹)")
        col_widths = (60, 80, 140, 130, 120, 120, 100, 100)

        self.bank_tree = ttk.Treeview(tree_frame, columns=col_bank, show="headings", height=9)
        for col, w in zip(col_bank, col_widths):
            self.bank_tree.heading(col, text=col)
            self.bank_tree.column(col, width=w, anchor="center" if col in ("Bank ID", "Bank Code", "IFSC Code", "Account Number") else ("e" if "Balance" in col else "w"))

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.bank_tree.yview)
        self.bank_tree.configure(yscrollcommand=vsb.set)
        self.bank_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.bank_tree.bind("<<TreeviewSelect>>", self._on_bank_select)

        # Action Buttons
        btn_frame = tk.Frame(self.right_frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add", font=('Arial', 10, 'bold'), bg="#2196F3", fg="white", width=12, command=self.clear_bank_form).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Save Bank", font=('Arial', 10, 'bold'), bg="#283593", fg="white", width=14, command=self.save_bank).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete Selected", font=('Arial', 10, 'bold'), bg="#D32F2F", fg="white", width=14, command=self.delete_bank).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete All", font=('Arial', 10, 'bold'), bg="#880E4F", fg="white", width=12, command=self.delete_all_banks).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Refresh", font=('Arial', 10, 'bold'), bg="#00897B", fg="white", width=10, command=self._load_banks).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Close", font=('Arial', 10, 'bold'), bg="#757575", fg="white", width=10, command=self.close).pack(side="left", padx=4)

        self._selected_bank_id = None
        self._load_banks()

    def _load_banks(self):
        if not hasattr(self, 'bank_tree'):
            return
        for item in self.bank_tree.get_children():
            self.bank_tree.delete(item)

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, bank_code, bank_name, account_name, account_no, branch_name, ifsc_code, balance FROM Banks ORDER BY id ASC")
            for r in cursor.fetchall():
                b_id, b_code, b_name, acc_name, acc_no, b_branch, ifsc, bal = r
                self.bank_tree.insert("", "end", values=(b_id, b_code or "", b_name or "", acc_name or "", acc_no or "", b_branch or "", ifsc or "", f"₹{bal:,.2f}"))
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading banks: {e}")

    def _on_bank_select(self, event):
        selected = self.bank_tree.selection()
        if not selected:
            return
        vals = self.bank_tree.item(selected[0])['values']
        self._selected_bank_id = vals[0]
        
        self.bb_bank_code.delete(0, "end")
        self.bb_bank_code.insert(0, vals[1])

        self.bb_bank_name.delete(0, "end")
        self.bb_bank_name.insert(0, vals[2])

        self.bb_account_name.delete(0, "end")
        self.bb_account_name.insert(0, vals[3])

        self.bb_account_no.delete(0, "end")
        self.bb_account_no.insert(0, vals[4])

        self.bb_branch.delete(0, "end")
        self.bb_branch.insert(0, vals[5])

        self.bb_ifsc.delete(0, "end")
        self.bb_ifsc.insert(0, vals[6])

        self.bb_balance.delete(0, "end")
        bal_clean = str(vals[7]).replace("₹", "").replace(",", "").strip()
        self.bb_balance.insert(0, bal_clean)

    def clear_bank_form(self):
        self._selected_bank_id = None
        self.bb_bank_code.delete(0, "end")
        self.bb_bank_name.delete(0, "end")
        self.bb_account_name.delete(0, "end")
        self.bb_account_no.delete(0, "end")
        self.bb_branch.delete(0, "end")
        self.bb_ifsc.delete(0, "end")
        self.bb_balance.delete(0, "end")

    def save_bank(self):
        b_code = self.bb_bank_code.get().strip()
        b_name = self.bb_bank_name.get().strip()
        acc_name = self.bb_account_name.get().strip()
        acc_no = self.bb_account_no.get().strip()
        b_branch = self.bb_branch.get().strip()
        b_ifsc = self.bb_ifsc.get().strip()
        b_bal_raw = self.bb_balance.get().strip() or "0"

        if not b_name:
            messagebox.showwarning("Validation Error", "Please enter Bank Name.")
            return

        try:
            b_bal = float(b_bal_raw)
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid numeric Balance.")
            return

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            if self._selected_bank_id:
                cursor.execute('''
                    UPDATE Banks SET bank_code=?, bank_name=?, account_name=?, account_no=?, branch_name=?, ifsc_code=?, balance=? WHERE id=?
                ''', (b_code, b_name, acc_name, acc_no, b_branch, b_ifsc, b_bal, self._selected_bank_id))
                messagebox.showinfo("Success", f"Bank '{b_name}' updated successfully.")
            else:
                cursor.execute('''
                    INSERT INTO Banks (bank_code, bank_name, account_name, account_no, branch_name, ifsc_code, balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (b_code, b_name, acc_name, acc_no, b_branch, b_ifsc, b_bal))
                messagebox.showinfo("Success", f"Bank '{b_name}' added successfully.")
            conn.commit()
            conn.close()

            self.clear_bank_form()
            self._load_banks()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Duplicate Bank", f"Bank '{b_name}' already exists in record.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save bank: {e}")

    def delete_bank(self):
        if not self._selected_bank_id:
            messagebox.showwarning("Warning", "Please select a bank from the table to delete.")
            return

        b_name = self.bb_bank_name.get().strip()
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete bank '{b_name}'?"):
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Banks WHERE id=?", (self._selected_bank_id,))
                conn.commit()
                conn.close()

                self.clear_bank_form()
                self._load_banks()
                messagebox.showinfo("Deleted", "Bank deleted successfully.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete bank: {e}")

    def delete_all_banks(self):
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete ALL bank records from the database?"):
            return
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Banks")
            conn.commit()
            conn.close()

            self.clear_bank_form()
            self._load_banks()
            messagebox.showinfo("Deleted", "All bank records deleted successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete all banks: {e}")