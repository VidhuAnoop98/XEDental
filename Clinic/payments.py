import os
import sqlite3
from accounts import get_db_connection, ACCENT_CASH, ACCENT_BANK, INACTIVE_BG, INACTIVE_FG
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

class Payments:
    def __init__(self, accounts_view):
        self.accounts_view = accounts_view
        self.app = accounts_view.app
        self.root = self.app.root
        
        self.get_next_chs_no = accounts_view.get_next_chs_no
        self.get_banks = accounts_view.get_banks
        self.get_ac_heads = accounts_view.get_ac_heads
        self.close = accounts_view.close
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.payments()

    def _set_payment_account_type(self, kind):
        self.payment_account_type.set(kind)
        self._refresh_payment_toggle_style()

    def _refresh_payment_toggle_style(self):
        kind = self.payment_account_type.get()
        if hasattr(self, 'pay_chs_no_var'):
            self.pay_chs_no_var.set(self.get_next_chs_no(f"PAY-{kind}"))
        if hasattr(self, 'pay_btn_cash') and hasattr(self, 'pay_btn_bank'):
            if kind == "CASH":
                self.pay_btn_cash.config(bg=ACCENT_CASH, fg="white", relief="sunken")
                self.pay_btn_bank.config(bg=INACTIVE_BG, fg=INACTIVE_FG, relief="raised")
                if hasattr(self, 'pay_bank_name_combo'):
                    self.pay_bank_name_combo.config(state="disabled")
                    self.pay_bank_name_combo.set("")
                if hasattr(self, 'pay_cheque_no_entry'):
                    self.pay_cheque_no_entry.config(state="disabled")
                    self.pay_cheque_no_entry.delete(0, "end")
                if hasattr(self, 'pay_bank_date_entry'):
                    self.pay_bank_date_entry.config(state="disabled")
                    self.pay_bank_date_entry.delete(0, "end")
            else:
                self.pay_btn_bank.config(bg=ACCENT_BANK, fg="white", relief="sunken")
                self.pay_btn_cash.config(bg=INACTIVE_BG, fg=INACTIVE_FG, relief="raised")
                if hasattr(self, 'pay_bank_name_combo'):
                    self.pay_bank_name_combo.config(state="readonly")
                    banks = self.get_banks()
                    self.pay_bank_name_combo['values'] = banks
                    if banks:
                        self.pay_bank_name_combo.current(0)
                if hasattr(self, 'pay_cheque_no_entry'):
                    self.pay_cheque_no_entry.config(state="normal")
                if hasattr(self, 'pay_bank_date_entry'):
                    self.pay_bank_date_entry.config(state="normal")
                    if not self.pay_bank_date_entry.get():
                        self.pay_bank_date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
    def payments(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        self.right_frame = tk.Frame(self.workspace, bd=2, relief="groove")
        self.right_frame.pack(side="right", padx=(20, 20), pady=20, fill="both", expand=True)

        title = tk.Label(self.right_frame, text="Payments Ledger", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(side="top", pady=10)

        # Toggle Buttons Frame
        form_toggle = tk.Frame(self.right_frame)
        form_toggle.pack(padx=12, pady=(0, 10))

        self.pay_btn_cash = tk.Button(
            form_toggle, text="Cash Payment", width=16, font=('Arial', 10, 'bold'), relief="raised", bd=2, height=2,
            command=lambda: self._set_payment_account_type("CASH")
        )
        self.pay_btn_cash.pack(side="left", padx=5)

        self.pay_btn_bank = tk.Button(
            form_toggle, text="Bank Payment", width=16, font=('Arial', 10, 'bold'), relief="raised", bd=2, height=2,
            command=lambda: self._set_payment_account_type("BANK")
        )
        self.pay_btn_bank.pack(side="left", padx=5)

        # Form Details Grid Frame
        form = tk.LabelFrame(self.right_frame, text="Payment Details", font=('Arial', 10, 'bold'), padx=15, pady=10)
        form.pack(fill="x", padx=15, pady=5)

        # Row 0
        tk.Label(form, text="Date:", font=('Arial', 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.pay_date_entry = tk.Entry(form, font=('Arial', 10), width=12)
        self.pay_date_entry.insert(0, date.today().strftime("%d-%m-%Y"))
        self.pay_date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Payment No:", font=('Arial', 10)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.pay_chs_no_var = tk.StringVar()
        self.pay_chs_no_entry = tk.Entry(form, font=('Arial', 10), width=14, textvariable=self.pay_chs_no_var, justify="center")
        self.pay_chs_no_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Paid To:", font=('Arial', 10)).grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.pay_paid_to_entry = tk.Entry(form, font=('Arial', 10), width=22)
        self.pay_paid_to_entry.grid(row=0, column=5, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Address:", font=('Arial', 10)).grid(row=0, column=6, sticky="e", padx=5, pady=5)
        self.pay_address_entry = tk.Entry(form, font=('Arial', 10), width=20)
        self.pay_address_entry.grid(row=0, column=7, sticky="w", padx=5, pady=5)

        # Row 1
        tk.Label(form, text="Bank Name:", font=('Arial', 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.pay_bank_name_combo = ttk.Combobox(form, values=self.get_banks(), font=('Arial', 9), width=20, state="disabled")
        self.pay_bank_name_combo.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Cheque / Ref No:", font=('Arial', 10)).grid(row=1, column=3, sticky="e", padx=5, pady=5)
        self.pay_cheque_no_entry = tk.Entry(form, font=('Arial', 10), width=14, state="disabled")
        self.pay_cheque_no_entry.grid(row=1, column=4, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Cheque Date:", font=('Arial', 10)).grid(row=1, column=5, sticky="e", padx=5, pady=5)
        self.pay_bank_date_entry = tk.Entry(form, font=('Arial', 10), width=14, state="disabled")
        self.pay_bank_date_entry.grid(row=1, column=6, sticky="w", padx=5, pady=5)

        # Row 2
        tk.Label(form, text="A/c Head:", font=('Arial', 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        heads = self.get_ac_heads()
        self.pay_ac_head_combo = ttk.Combobox(form, values=heads, font=('Arial', 9), width=20)
        if heads:
            self.pay_ac_head_combo.current(0)
        self.pay_ac_head_combo.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Narration:", font=('Arial', 10)).grid(row=2, column=3, sticky="e", padx=5, pady=5)
        self.pay_narration_entry = tk.Entry(form, font=('Arial', 10), width=24)
        self.pay_narration_entry.grid(row=2, column=4, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Amount (₹):", font=('Arial', 10, 'bold')).grid(row=2, column=6, sticky="e", padx=5, pady=5)
        self.pay_amount_entry = tk.Entry(form, font=('Arial', 10, 'bold'), width=14)
        self.pay_amount_entry.grid(row=2, column=7, sticky="w", padx=5, pady=5)

        # Table Treeview Frame
        table_frame = tk.Frame(self.right_frame)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("ID", "Date", "CHS_NO", "Paid_To", "Mode", "Bank_Name", "A_C_Head", "Narration", "Amount")
        self.payment_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        headings = {
            "ID": "ID", "Date": "Date", "CHS_NO": "Payment No", "Paid_To": "Paid To",
            "Mode": "Mode", "Bank_Name": "Bank Name", "A_C_Head": "A/C Head", "Narration": "Narration", "Amount": "Amount (₹)"
        }
        widths = {
            "ID": 40, "Date": 90, "CHS_NO": 100, "Paid_To": 150, "Mode": 70,
            "Bank_Name": 130, "A_C_Head": 130, "Narration": 160, "Amount": 100
        }
        for col in columns:
            self.payment_tree.heading(col, text=headings[col])
            self.payment_tree.column(col, width=widths[col], anchor="center" if col in ("ID", "Date", "CHS_NO", "Mode") else "w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.payment_tree.yview)
        self.payment_tree.configure(yscrollcommand=vsb.set)
        self.payment_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.payment_tree.tag_configure("CASH", foreground=ACCENT_CASH)
        self.payment_tree.tag_configure("BANK", foreground=ACCENT_BANK)

        # Action Buttons Frame
        action_frame = tk.Frame(self.right_frame)
        action_frame.pack(fill="x", padx=15, pady=10)

        tk.Button(action_frame, text="Add", font=('Arial', 10), width=14, command=self.clear_payment_form).pack(side="left", padx=5)
        tk.Button(action_frame, text="Save Payment", font=('Arial', 10, 'bold'), bg="#2e7d32", fg="white", width=15, command=self.save_payment).pack(side="left", padx=5)
        tk.Button(action_frame, text="Delete Selected", font=('Arial', 10), width=15, command=self.delete_payment).pack(side="left", padx=5)
        tk.Button(action_frame, text="Print Voucher", font=('Arial', 10), width=14, command=lambda: self.print_voucher("Payment")).pack(side="left", padx=5)
        tk.Button(action_frame, text="Close", font=('Arial', 10), width=12, command=self.close).pack(side="left", padx=5)

        self.total_payment_var = tk.StringVar(value="Total Payments: ₹0.00")
        total_lbl = tk.Label(action_frame, textvariable=self.total_payment_var, font=('Arial', 11, 'bold'), fg="navy")
        total_lbl.pack(side="right", padx=15)

        self._refresh_payment_toggle_style()
        self.load_payments_data()

    def clear_payment_form(self):
        self.pay_paid_to_entry.delete(0, "end")
        self.pay_address_entry.delete(0, "end")
        if self.pay_cheque_no_entry['state'] == 'normal':
            self.pay_cheque_no_entry.delete(0, "end")
        self.pay_narration_entry.delete(0, "end")
        self.pay_amount_entry.delete(0, "end")
        self._refresh_payment_toggle_style()

    def save_payment(self):
        mode = self.payment_account_type.get()
        p_date = self.pay_date_entry.get().strip()
        chs_no = self.pay_chs_no_entry.get().strip()
        paid_to = self.pay_paid_to_entry.get().strip()
        address = self.pay_address_entry.get().strip()
        bank_name = self.pay_bank_name_combo.get().strip() if mode == "BANK" else ""
        cheque_no = self.pay_cheque_no_entry.get().strip() if mode == "BANK" else ""
        ac_head = self.pay_ac_head_combo.get().strip()
        narration = self.pay_narration_entry.get().strip()
        amount_raw = self.pay_amount_entry.get().strip()

        if not paid_to:
            messagebox.showwarning("Validation Error", "Please enter 'Paid To'.")
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
            ''', (f"Payment-{mode}", chs_no, p_date, paid_to, f"{address}|Bank:{bank_name}", full_narration, ac_head, amount))
            conn.commit()

            if mode == "BANK" and bank_name:
                cursor.execute("UPDATE Banks SET balance = balance - ? WHERE bank_name=?", (amount, bank_name))
                conn.commit()

            conn.close()

            messagebox.showinfo("Success", "Payment saved successfully!")
            self.clear_payment_form()
            self.load_payments_data()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save payment: {e}")

    def load_payments_data(self):
        if not hasattr(self, 'payment_tree'):
            return
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)

        total_amount = 0.0
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, DATE, CHS_NO, PAID_TO, transaction_type, ADDRESS, A_C_HEAD, Narration, AMOUNT "
                "FROM Receipts WHERE transaction_type LIKE 'Payment%' OR transaction_type='Payment' ORDER BY id DESC"
            )
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                rec_id, rec_date, chs_no, paid_to, t_type, address_raw, ac_head, narration, amount = row
                mode = "BANK" if "BANK" in str(t_type).upper() else "CASH"
                bank_name = ""
                if "|Bank:" in str(address_raw):
                    bank_name = str(address_raw).split("|Bank:")[1]

                self.payment_tree.insert("", "end", tags=(mode,), values=(
                    rec_id, rec_date, chs_no, paid_to, mode, bank_name, ac_head, narration, f"₹{amount:,.2f}"
                ))
                total_amount += amount

            self.total_payment_var.set(f"Total Payments: ₹{total_amount:,.2f}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading payments: {e}")

    def delete_payment(self):
        selected = self.payment_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a payment record to delete.")
            return

        rec_id = self.payment_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete payment record #{rec_id}?"):
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Receipts WHERE id=?", (rec_id,))
                conn.commit()
                conn.close()
                self.load_payments_data()
                messagebox.showinfo("Deleted", "Payment record deleted.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error deleting payment: {e}")

    # =========================================================================
    # VOUCHER PRINTING (PDF GENERATOR)
    # =========================================================================
    def print_voucher(self, v_type="Payment"):
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
        except ImportError:
            messagebox.showerror(
                "Missing Dependency",
                "reportlab is not installed. Install it with: pip install reportlab"
            )
            return

        tree = self.receipt_tree if v_type == "Receipt" else self.payment_tree
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Voucher", f"Please select a {v_type.lower()} record from the table to print.")
            return

        vals = tree.item(selected[0])['values']
        v_id, v_date, v_no, person, mode, bank, head, narration, amount = vals

        output_path = os.path.join(self.script_dir, f"{v_type.lower()}_voucher_{v_no}.pdf")
        pdf = canvas.Canvas(output_path, pagesize=A4)

        # Header
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(100, 800, "XE DENTAL CLINIC")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(100, 785, "West Gate, Vaikom, Kottayam Dist, Kerala - 686141")

        # Voucher Box Title
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, 750, f"{v_type.upper()} VOUCHER")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(420, 750, f"Date: {v_date}")
        pdf.drawString(420, 735, f"Voucher No: {v_no}")

        pdf.line(100, 725, 500, 725)

        # Fields
        y = 700
        pdf.drawString(100, y, f"{'Received From' if v_type == 'Receipt' else 'Paid To'}: {person}")
        y -= 20
        pdf.drawString(100, y, f"Payment Mode: {mode}" + (f" ({bank})" if bank else ""))
        y -= 20
        pdf.drawString(100, y, f"Account Head: {head}")
        y -= 20
        pdf.drawString(100, y, f"Narration / Details: {narration}")
        y -= 25

        pdf.line(100, y, 500, y)
        y -= 20

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y, f"Total Amount: {amount}")

        pdf.setFont("Helvetica", 10)
        pdf.drawString(100, 550, "Authorized Signature: __________________")

        pdf.save()
        messagebox.showinfo("Voucher Generated", f"{v_type} voucher PDF generated successfully:\n{output_path}")

        
