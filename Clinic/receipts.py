import os
import sqlite3
from accounts import get_db_connection, ACCENT_CASH, ACCENT_BANK, INACTIVE_BG, INACTIVE_FG
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

class Receipt:
    def __init__(self, accounts_view):
        self.accounts_view = accounts_view
        self.app = accounts_view.app
        self.root = self.app.root
        
        self.get_next_chs_no = accounts_view.get_next_chs_no
        self.get_banks = accounts_view.get_banks
        self.get_ac_heads = accounts_view.get_ac_heads
        self.close = accounts_view.close
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.receipt()

    def _set_receipt_account_type(self, kind):
        self.receipt_account_type.set(kind)
        self._refresh_receipt_toggle_style()

    def _refresh_receipt_toggle_style(self):
        kind = self.receipt_account_type.get()
        if hasattr(self, 'rec_chs_no_var'):
            self.rec_chs_no_var.set(self.get_next_chs_no(f"REC-{kind}"))
        if hasattr(self, 'rec_btn_cash') and hasattr(self, 'rec_btn_bank'):
            if kind == "CASH":
                self.rec_btn_cash.config(bg=ACCENT_CASH, fg="white", relief="sunken")
                self.rec_btn_bank.config(bg=INACTIVE_BG, fg=INACTIVE_FG, relief="raised")
                if hasattr(self, 'rec_bank_name_combo'):
                    self.rec_bank_name_combo.config(state="disabled")
                    self.rec_bank_name_combo.set("")
                if hasattr(self, 'rec_cheque_no_entry'):
                    self.rec_cheque_no_entry.config(state="disabled")
                    self.rec_cheque_no_entry.delete(0, "end")
                if hasattr(self, 'rec_bank_date_entry'):
                    self.rec_bank_date_entry.config(state="disabled")
                    self.rec_bank_date_entry.delete(0, "end")
            else:
                self.rec_btn_bank.config(bg=ACCENT_BANK, fg="white", relief="sunken")
                self.rec_btn_cash.config(bg=INACTIVE_BG, fg=INACTIVE_FG, relief="raised")
                if hasattr(self, 'rec_bank_name_combo'):
                    self.rec_bank_name_combo.config(state="readonly")
                    banks = self.get_banks()
                    self.rec_bank_name_combo['values'] = banks
                    if banks:
                        self.rec_bank_name_combo.current(0)
                if hasattr(self, 'rec_cheque_no_entry'):
                    self.rec_cheque_no_entry.config(state="normal")
                if hasattr(self, 'rec_bank_date_entry'):
                    self.rec_bank_date_entry.config(state="normal")
                    if not self.rec_bank_date_entry.get():
                        self.rec_bank_date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        
    def receipt(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        self.right_frame = tk.Frame(self.workspace, bd=2, relief="groove")
        self.right_frame.pack(side="right", padx=(20, 20), pady=20, fill="both", expand=True)

        title = tk.Label(self.right_frame, text="Receipts Ledger", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(side="top", pady=10)

        # Toggle Buttons Frame
        form_toggle = tk.Frame(self.right_frame)
        form_toggle.pack(padx=12, pady=(0, 10))

        self.rec_btn_cash = tk.Button(
            form_toggle, text="Cash Receipt", width=16, font=('Arial', 10, 'bold'), relief="raised", bd=2, height=2,
            command=lambda: self._set_receipt_account_type("CASH")
        )
        self.rec_btn_cash.pack(side="left", padx=5)

        self.rec_btn_bank = tk.Button(
            form_toggle, text="Bank Receipt", width=16, font=('Arial', 10, 'bold'), relief="raised", bd=2, height=2,
            command=lambda: self._set_receipt_account_type("BANK")
        )
        self.rec_btn_bank.pack(side="left", padx=5)

        # Form Details Grid Frame
        form = tk.LabelFrame(self.right_frame, text="Receipt Details", font=('Arial', 10, 'bold'), padx=15, pady=10)
        form.pack(fill="x", padx=15, pady=5)

        # Row 0
        tk.Label(form, text="Date:", font=('Arial', 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.rec_date_entry = tk.Entry(form, font=('Arial', 10), width=12)
        self.rec_date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        self.rec_date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Receipt No:", font=('Arial', 10)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.rec_chs_no_var = tk.StringVar()
        self.rec_chs_no_entry = tk.Entry(form, font=('Arial', 10), width=14, textvariable=self.rec_chs_no_var, justify="center")
        self.rec_chs_no_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Received From:", font=('Arial', 10)).grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.rec_paid_to_entry = tk.Entry(form, font=('Arial', 10), width=22)
        self.rec_paid_to_entry.grid(row=0, column=5, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Address:", font=('Arial', 10)).grid(row=0, column=6, sticky="e", padx=5, pady=5)
        self.rec_address_entry = tk.Entry(form, font=('Arial', 10), width=20)
        self.rec_address_entry.grid(row=0, column=7, sticky="w", padx=5, pady=5)

        # Row 1
        tk.Label(form, text="Bank Name:", font=('Arial', 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.rec_bank_name_combo = ttk.Combobox(form, values=self.get_banks(), font=('Arial', 9), width=20, state="disabled")
        self.rec_bank_name_combo.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Cheque / Ref No:", font=('Arial', 10)).grid(row=1, column=3, sticky="e", padx=5, pady=5)
        self.rec_cheque_no_entry = tk.Entry(form, font=('Arial', 10), width=14, state="disabled")
        self.rec_cheque_no_entry.grid(row=1, column=4, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Cheque Date:", font=('Arial', 10)).grid(row=1, column=5, sticky="e", padx=5, pady=5)
        self.rec_bank_date_entry = tk.Entry(form, font=('Arial', 10), width=14, state="disabled")
        self.rec_bank_date_entry.grid(row=1, column=6, sticky="w", padx=5, pady=5)

        # Row 2
        tk.Label(form, text="A/c Head:", font=('Arial', 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        heads = self.get_ac_heads()
        self.rec_ac_head_combo = ttk.Combobox(form, values=heads, font=('Arial', 9), width=20)
        if heads:
            self.rec_ac_head_combo.current(0)
        self.rec_ac_head_combo.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Narration:", font=('Arial', 10)).grid(row=2, column=3, sticky="e", padx=5, pady=5)
        self.rec_narration_entry = tk.Entry(form, font=('Arial', 10), width=24)
        self.rec_narration_entry.grid(row=2, column=4, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Amount (₹):", font=('Arial', 10, 'bold')).grid(row=2, column=6, sticky="e", padx=5, pady=5)
        self.rec_amount_entry = tk.Entry(form, font=('Arial', 10, 'bold'), width=14)
        self.rec_amount_entry.grid(row=2, column=7, sticky="w", padx=5, pady=5)

        # Table Treeview Frame
        table_frame = tk.Frame(self.right_frame)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("ID", "Date", "CHS_NO", "Received_From", "Mode", "Bank_Name", "A_C_Head", "Narration", "Amount")
        self.receipt_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        headings = {
            "ID": "ID", "Date": "Date", "CHS_NO": "Receipt No", "Received_From": "Received From",
            "Mode": "Mode", "Bank_Name": "Bank Name", "A_C_Head": "A/C Head", "Narration": "Narration", "Amount": "Amount (₹)"
        }
        widths = {
            "ID": 40, "Date": 90, "CHS_NO": 100, "Received_From": 150, "Mode": 70,
            "Bank_Name": 130, "A_C_Head": 130, "Narration": 160, "Amount": 100
        }
        for col in columns:
            self.receipt_tree.heading(col, text=headings[col])
            self.receipt_tree.column(col, width=widths[col], anchor="center" if col in ("ID", "Date", "CHS_NO", "Mode") else "w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.receipt_tree.yview)
        self.receipt_tree.configure(yscrollcommand=vsb.set)
        self.receipt_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.receipt_tree.tag_configure("CASH", foreground=ACCENT_CASH)
        self.receipt_tree.tag_configure("BANK", foreground=ACCENT_BANK)

        # Action Buttons Frame
        action_frame = tk.Frame(self.right_frame)
        action_frame.pack(fill="x", padx=15, pady=10)

        tk.Button(action_frame, text="Add", font=('Arial', 10), width=14, command=self.clear_receipt_form).pack(side="left", padx=5)
        tk.Button(action_frame, text="Save Receipt", font=('Arial', 10, 'bold'), bg="#2e7d32", fg="white", width=15, command=self.save_receipt).pack(side="left", padx=5)
        tk.Button(action_frame, text="Delete Selected", font=('Arial', 10), width=15, command=self.delete_receipt).pack(side="left", padx=5)
        tk.Button(action_frame, text="Print Voucher", font=('Arial', 10), width=14, command=lambda: self.print_voucher("Receipt")).pack(side="left", padx=5)
        tk.Button(action_frame, text="Close", font=('Arial', 10), width=12, command=self.close).pack(side="left", padx=5)

        self.total_receipt_var = tk.StringVar(value="Total Receipts: ₹0.00")
        total_lbl = tk.Label(action_frame, textvariable=self.total_receipt_var, font=('Arial', 11, 'bold'), fg="navy")
        total_lbl.pack(side="right", padx=15)

        self._refresh_receipt_toggle_style()
        self.load_receipts_data()

    def clear_receipt_form(self):
        self.rec_paid_to_entry.delete(0, "end")
        self.rec_address_entry.delete(0, "end")
        if self.rec_cheque_no_entry['state'] == 'normal':
            self.rec_cheque_no_entry.delete(0, "end")
        self.rec_narration_entry.delete(0, "end")
        self.rec_amount_entry.delete(0, "end")
        self._refresh_receipt_toggle_style()

    def save_receipt(self):
        mode = self.receipt_account_type.get()
        p_date = self.rec_date_entry.get().strip()
        chs_no = self.rec_chs_no_entry.get().strip()
        received_from = self.rec_paid_to_entry.get().strip()
        address = self.rec_address_entry.get().strip()
        bank_name = self.rec_bank_name_combo.get().strip() if mode == "BANK" else ""
        cheque_no = self.rec_cheque_no_entry.get().strip() if mode == "BANK" else ""
        ac_head = self.rec_ac_head_combo.get().strip()
        narration = self.rec_narration_entry.get().strip()
        amount_raw = self.rec_amount_entry.get().strip()

        if not received_from:
            messagebox.showwarning("Validation Error", "Please enter 'Received From'.")
            return

        if mode == "BANK" and not bank_name:
            messagebox.showwarning("Validation Error", "Please select a Bank Name.")
            return

        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid positive Amount.")
            return

        full_narration = narration
        if mode == "BANK" and cheque_no:
            full_narration = f"{narration} (Chq: {cheque_no})" if narration else f"Chq: {cheque_no}"

        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Receipts (transaction_type, CHS_NO, DATE, PAID_TO, ADDRESS, Narration, A_C_HEAD, AMOUNT)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"Receipt-{mode}", chs_no, p_date, received_from, f"{address}|Bank:{bank_name}", full_narration, ac_head, amount))
            conn.commit()

            if mode == "BANK" and bank_name:
                cursor.execute("UPDATE Banks SET balance = balance + ? WHERE bank_name=?", (amount, bank_name))
                conn.commit()

            conn.close()

            messagebox.showinfo("Success", "Receipt saved successfully!")
            self.clear_receipt_form()
            self.load_receipts_data()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save receipt: {e}")

    def load_receipts_data(self):
        if not hasattr(self, 'receipt_tree'):
            return
        for item in self.receipt_tree.get_children():
            self.receipt_tree.delete(item)

        total_amount = 0.0
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, DATE, CHS_NO, PAID_TO, transaction_type, ADDRESS, A_C_HEAD, Narration, AMOUNT "
                "FROM Receipts WHERE transaction_type LIKE 'Receipt%' OR transaction_type='Receipt' ORDER BY id DESC"
            )
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                rec_id, rec_date, chs_no, received_from, t_type, address_raw, ac_head, narration, amount = row
                mode = "BANK" if "BANK" in str(t_type).upper() else "CASH"
                bank_name = ""
                if "|Bank:" in str(address_raw):
                    bank_name = str(address_raw).split("|Bank:")[1]

                self.receipt_tree.insert("", "end", tags=(mode,), values=(
                    rec_id, rec_date, chs_no, received_from, mode, bank_name, ac_head, narration, f"₹{amount:,.2f}"
                ))
                total_amount += amount

            self.total_receipt_var.set(f"Total Receipts: ₹{total_amount:,.2f}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading receipts: {e}")

    def delete_receipt(self):
        selected = self.receipt_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a receipt record to delete.")
            return

        rec_id = self.receipt_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete receipt record #{rec_id}?"):
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Receipts WHERE id=?", (rec_id,))
                conn.commit()
                conn.close()
                self.load_receipts_data()
                messagebox.showinfo("Deleted", "Receipt record deleted.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error deleting receipt: {e}")



        