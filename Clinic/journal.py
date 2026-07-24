import os
import sqlite3
from accounts import get_db_connection
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

class Joural:
    def __init__(self, accounts_view):
        self.accounts_view = accounts_view
        self.app = accounts_view.app
        self.root = self.app.root
        
        self.get_next_chs_no = accounts_view.get_next_chs_no
        self.get_ac_heads = accounts_view.get_ac_heads
        self.close = accounts_view.close
        
        self.joural()

    def joural(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        self.right_frame = tk.Frame(self.workspace, bd=2, relief="groove")
        self.right_frame.pack(side="right", padx=(20, 20), pady=20, fill="both", expand=True)

        title = tk.Label(self.right_frame, text="Journal Entries", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(side="top", pady=10)

        # Form Details Frame
        form = tk.LabelFrame(self.right_frame, text="Journal Voucher Details", font=('Arial', 10, 'bold'), padx=15, pady=10)
        form.pack(fill="x", padx=15, pady=5)

        heads = self.get_ac_heads()

        # Row 0
        tk.Label(form, text="Date:", font=('Arial', 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.jrn_date_entry = tk.Entry(form, font=('Arial', 10), width=14)
        self.jrn_date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        self.jrn_date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Voucher No:", font=('Arial', 10)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.jrn_no_var = tk.StringVar(value=self.get_next_chs_no("JRN"))
        self.jrn_no_entry = tk.Entry(form, font=('Arial', 10), width=14, textvariable=self.jrn_no_var, justify="center")
        self.jrn_no_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Row 1
        tk.Label(form, text="Debit A/c Head:", font=('Arial', 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.jrn_debit_combo = ttk.Combobox(form, values=heads, font=('Arial', 9), width=22)
        if heads:
            self.jrn_debit_combo.current(0)
        self.jrn_debit_combo.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Credit A/c Head:", font=('Arial', 10)).grid(row=1, column=3, sticky="e", padx=5, pady=5)
        self.jrn_credit_combo = ttk.Combobox(form, values=heads, font=('Arial', 9), width=22)
        if len(heads) > 1:
            self.jrn_credit_combo.current(1)
        elif heads:
            self.jrn_credit_combo.current(0)
        self.jrn_credit_combo.grid(row=1, column=4, columnspan=2, sticky="w", padx=5, pady=5)

        # Row 2
        tk.Label(form, text="Particulars:", font=('Arial', 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.jrn_narration_entry = tk.Entry(form, font=('Arial', 10), width=30)
        self.jrn_narration_entry.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Amount (₹):", font=('Arial', 10, 'bold')).grid(row=2, column=4, sticky="e", padx=5, pady=5)
        self.jrn_amount_entry = tk.Entry(form, font=('Arial', 10, 'bold'), width=14)
        self.jrn_amount_entry.grid(row=2, column=5, sticky="w", padx=5, pady=5)

        # Table Treeview Frame
        table_frame = tk.Frame(self.right_frame)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("ID", "Date", "Voucher_No", "Debit_Head", "Credit_Head", "Narration", "Amount")
        self.journal_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        headings = {
            "ID": "ID", "Date": "Date", "Voucher_No": "Voucher No", "Debit_Head": "Debit A/C Head",
            "Credit_Head": "Credit A/C Head", "Narration": "Particulars / Narration", "Amount": "Amount (₹)"
        }
        widths = {
            "ID": 40, "Date": 90, "Voucher_No": 100, "Debit_Head": 160,
            "Credit_Head": 160, "Narration": 220, "Amount": 100
        }
        for col in columns:
            self.journal_tree.heading(col, text=headings[col])
            self.journal_tree.column(col, width=widths[col], anchor="center" if col in ("ID", "Date", "Voucher_No") else "w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.journal_tree.yview)
        self.journal_tree.configure(yscrollcommand=vsb.set)
        self.journal_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Action Buttons Frame
        action_frame = tk.Frame(self.right_frame)
        action_frame.pack(fill="x", padx=15, pady=10)

        tk.Button(action_frame, text="Add", font=('Arial', 10), width=14, command=self.clear_journal_form).pack(side="left", padx=5)
        tk.Button(action_frame, text="Save Entry", font=('Arial', 10, 'bold'), bg="#2e7d32", fg="white", width=15, command=self.save_journal).pack(side="left", padx=5)
        tk.Button(action_frame, text="Delete Selected", font=('Arial', 10), width=15, command=self.delete_journal).pack(side="left", padx=5)
        tk.Button(action_frame, text="Close", font=('Arial', 10), width=12, command=self.close).pack(side="left", padx=5)

        self.total_journal_var = tk.StringVar(value="Total Journal: ₹0.00")
        total_lbl = tk.Label(action_frame, textvariable=self.total_journal_var, font=('Arial', 11, 'bold'), fg="navy")
        total_lbl.pack(side="right", padx=15)

        self.load_journal_data()

    def clear_journal_form(self):
        self.jrn_no_var.set(self.get_next_chs_no("JRN"))
        self.jrn_narration_entry.delete(0, "end")
        self.jrn_amount_entry.delete(0, "end")

    def save_journal(self):
        j_date = self.jrn_date_entry.get().strip()
        v_no = self.jrn_no_entry.get().strip()
        debit_head = self.jrn_debit_combo.get().strip()
        credit_head = self.jrn_credit_combo.get().strip()
        narration = self.jrn_narration_entry.get().strip()
        amount_raw = self.jrn_amount_entry.get().strip()

        if not debit_head or not credit_head:
            messagebox.showwarning("Validation Error", "Please select Debit and Credit A/c Heads.")
            return

        if debit_head == credit_head:
            messagebox.showwarning("Validation Error", "Debit A/c and Credit A/c heads cannot be identical.")
            return

        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid positive Amount.")
            return

        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Journal (voucher_no, date, debit_head, credit_head, narration, amount)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (v_no, j_date, debit_head, credit_head, narration, amount))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Journal entry saved successfully!")
            self.clear_journal_form()
            self.load_journal_data()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save journal entry: {e}")

    def load_journal_data(self):
        if not hasattr(self, 'journal_tree'):
            return
        for item in self.journal_tree.get_children():
            self.journal_tree.delete(item)

        total_amount = 0.0
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT id, date, voucher_no, debit_head, credit_head, narration, amount FROM Journal ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                j_id, j_date, v_no, debit_head, credit_head, narration, amount = row
                self.journal_tree.insert("", "end", values=(
                    j_id, j_date, v_no, debit_head, credit_head, narration, f"₹{amount:,.2f}"
                ))
                total_amount += amount

            self.total_journal_var.set(f"Total Journal: ₹{total_amount:,.2f}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading journal entries: {e}")

    def delete_journal(self):
        selected = self.journal_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a journal record to delete.")
            return

        j_id = self.journal_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete journal entry #{j_id}?"):
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Journal WHERE id=?", (j_id,))
                conn.commit()
                conn.close()
                self.load_journal_data()
                messagebox.showinfo("Deleted", "Journal entry deleted.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error deleting journal entry: {e}")
