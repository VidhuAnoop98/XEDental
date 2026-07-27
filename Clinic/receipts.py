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
        self.receipt_account_type = tk.StringVar(value="CASH")
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
        tk.Button(action_frame, text="Print Voucher", font=('Arial', 10), width=14, command=self.print_voucher).pack(side="left", padx=5)
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

    def print_voucher(self):
        import os
        import sys
        import subprocess
        import tempfile
        from datetime import date

        import tkinter as tk
        from tkinter import ttk, messagebox

        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor

        # ----------------------------------------------------------------------
        # Organisation details shown on the voucher header - edit these
        # ----------------------------------------------------------------------
        ORG_NAME = "Dr.Anoop's Anupam Dental Clinic"
        ORG_ADDRESS = "West Gate, Vaikom 686141"
        ORG_PHONE = "+91 9446046868"  # e.g. "Ph : 0000000000" - leave blank to omit

        # Half A4, landscape (A4 cut horizontally)
        PAGE_W, PAGE_H = 210 * mm, 148.5 * mm

        INK = HexColor("#1a1a1a")


        # ----------------------------------------------------------------------
        # Amount -> words (Indian numbering: crore / lakh / thousand)
        # ----------------------------------------------------------------------
        _ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
                "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
                "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        _TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
                "Eighty", "Ninety"]


        def _two_digit_words(n: int) -> str:
            if n < 20:
                return _ONES[n]
            tens, ones = divmod(n, 10)
            return _TENS[tens] + (" " + _ONES[ones] if ones else "")


        def _three_digit_words(n: int) -> str:
            if n >= 100:
                hundred, rest = divmod(n, 100)
                return _ONES[hundred] + " Hundred" + (" " + _two_digit_words(rest) if rest else "")
            return _two_digit_words(n)


        def amount_to_words(amount: float) -> str:
            """Converts a rupee amount (e.g. 12500.50) to words, Indian numbering
            system: 'Rupees Twelve Thousand Five Hundred and Fifty Paise Only'."""
            rupees = int(amount)
            paise = round((amount - rupees) * 100)

            if rupees == 0:
                words = "Zero"
            else:
                parts = []
                crore, rupees = divmod(rupees, 10000000)
                lakh, rupees = divmod(rupees, 100000)
                thousand, rupees = divmod(rupees, 1000)
                hundred = rupees

                if crore:
                    parts.append(_three_digit_words(crore) + " Crore")
                if lakh:
                    parts.append(_three_digit_words(lakh) + " Lakh")
                if thousand:
                    parts.append(_three_digit_words(thousand) + " Thousand")
                if hundred:
                    parts.append(_three_digit_words(hundred))
                words = " ".join(parts)

            result = f"Rupees {words} Only"
            if paise:
                result = f"Rupees {words} and {_two_digit_words(paise)} Paise Only"
            return result


        # ----------------------------------------------------------------------
        # Voucher drawing (half-A4 landscape, 210 x 148.5mm)
        # ----------------------------------------------------------------------
        def draw_voucher(c: canvas.Canvas, data: dict):
            """
            Draws one receipt/payment voucher filling the whole half-A4 page.
            `data` keys: voucher_type, date_str, voucher_no, received_from,
            address, mode, bank_name, cheque_no, cheque_date, ac_head,
            narration, amount (float).
            """
            c.setFillColor(INK)
            c.setStrokeColor(INK)
            margin = 8 * mm

            # ---------- outer border ----------
            c.setLineWidth(0.8)
            c.rect(margin, margin, PAGE_W - 2 * margin, PAGE_H - 2 * margin, stroke=1, fill=0)

            # ---------- header ----------
            c.setFont("Times-Bold", 16)
            c.drawCentredString(PAGE_W / 2, PAGE_H - margin - 9 * mm, ORG_NAME)

            c.setFont("Helvetica", 8.5)
            header_line2 = ORG_ADDRESS + (f"   {ORG_PHONE}" if ORG_PHONE else "")
            c.drawCentredString(PAGE_W / 2, PAGE_H - margin - 14 * mm, header_line2)

            rule_y = PAGE_H - margin - 18 * mm
            c.setLineWidth(0.6)
            c.line(margin + 2 * mm, rule_y, PAGE_W - margin - 2 * mm, rule_y)

            # ---------- voucher title + no/date ----------
            mode = data.get("mode", "CASH")
            voucher_title = f"{mode.title()} {data.get('voucher_type', 'Receipt')} Voucher"
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(PAGE_W / 2, rule_y - 8 * mm, voucher_title.upper())

            c.setFont("Helvetica", 9.5)
            c.drawString(margin + 4 * mm, rule_y - 8 * mm, f"No : {data.get('voucher_no') or '-'}")
            c.drawRightString(PAGE_W - margin - 4 * mm, rule_y - 8 * mm, f"Date : {data.get('date_str') or ''}")

            # ---------- field lines ----------
            field_x_label = margin + 4 * mm
            field_x_value = margin + 34 * mm
            field_right_edge = PAGE_W - margin - 4 * mm
            y = rule_y - 16 * mm
            line_gap = 8.5 * mm

            def field_row(label, value, underline=True):
                nonlocal y
                c.setFont("Helvetica-Bold", 9.5)
                c.drawString(field_x_label, y, label)
                c.setFont("Helvetica", 10)
                c.drawString(field_x_value, y, str(value) if value else "")
                if underline:
                    c.setLineWidth(0.4)
                    c.line(field_x_value, y - 1.5 * mm, field_right_edge, y - 1.5 * mm)
                y -= line_gap

            field_row("Received From :" if data.get("voucher_type", "Receipt") == "Receipt" else "Paid To :",
                    data.get("received_from", ""))
            field_row("Address :", data.get("address", ""))
            field_row("Sum of Rupees :", amount_to_words(data.get("amount", 0.0)))

            # Mode-specific line (bank details) or narration, whichever mode
            if mode == "BANK":
                bank_bits = []
                if data.get("bank_name"):
                    bank_bits.append(f"Bank: {data['bank_name']}")
                if data.get("cheque_no"):
                    bank_bits.append(f"Cheque/Ref No: {data['cheque_no']}")
                if data.get("cheque_date"):
                    bank_bits.append(f"Dated: {data['cheque_date']}")
                field_row("Bank Details :", "   ".join(bank_bits))
            else:
                field_row("Mode :", "Cash")

            field_row("A/c Head :", data.get("ac_head", ""))
            field_row("Towards (Narration) :", data.get("narration", ""))

            # ---------- amount box (bottom-right) ----------
            box_w, box_h = 55 * mm, 16 * mm
            box_x = PAGE_W - margin - 4 * mm - box_w
            box_y = margin + 16 * mm
            c.setLineWidth(0.9)
            c.rect(box_x, box_y, box_w, box_h, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(box_x + 3 * mm, box_y + box_h - 6 * mm, "Amount")
            c.setFont("Helvetica-Bold", 15)
            c.drawRightString(box_x + box_w - 4 * mm, box_y + 4.5 * mm, f"Rs. {data.get('amount', 0.0):,.2f}")

            # ---------- signatures ----------
            sig_y = margin + 6 * mm
            c.setFont("Helvetica", 9)
            c.setLineWidth(0.4)
            c.line(margin + 4 * mm, sig_y + 6 * mm, margin + 55 * mm, sig_y + 6 * mm)
            c.drawString(margin + 4 * mm, sig_y, "Receiver's Signature")

            c.line(box_x - 60 * mm, sig_y + 6 * mm, box_x - 5 * mm, sig_y + 6 * mm)
            c.drawString(box_x - 60 * mm, sig_y, "Authorised Signatory")


        def generate_voucher_pdf(data: dict, filepath: str = None) -> str:
            """Builds the half-A4 voucher PDF and returns the file path."""
            if filepath is None:
                fd, filepath = tempfile.mkstemp(prefix="voucher_", suffix=".pdf")
                os.close(fd)

            c = canvas.Canvas(filepath, pagesize=(PAGE_W, PAGE_H))
            draw_voucher(c, data)
            c.showPage()
            c.save()
            return filepath


        def open_for_printing(filepath: str):
            """Opens the PDF with the system's default viewer so the user can
            review and print it (Ctrl+P)."""
            try:
                if sys.platform.startswith("win"):
                    os.startfile(filepath)  # noqa: S606 (Windows only)
                elif sys.platform == "darwin":
                    subprocess.run(["open", filepath], check=False)
                else:
                    subprocess.run(["xdg-open", filepath], check=False)
            except Exception as exc:
                messagebox.showwarning(
                    "Could not open automatically",
                    f"The voucher was saved to:\n{filepath}\n\n"
                    f"Please open it manually to print. ({exc})",
                )
        # ---- get selected row from treeview ----
        selected = self.receipt_tree.selection()
        if not selected:
            messagebox.showwarning("Select Voucher", "Please select a receipt record from the table to print.")
            return

        vals = self.receipt_tree.item(selected[0])['values']
        # Treeview columns: ID, Date, CHS_NO, Received_From, Mode, Bank_Name, A_C_Head, Narration, Amount
        rec_id = vals[0]

        # Fetch full record from DB (treeview doesn't show address, cheque details)
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, DATE, CHS_NO, PAID_TO, transaction_type, ADDRESS, A_C_HEAD, Narration, AMOUNT "
                "FROM Receipts WHERE id=?", (rec_id,)
            )
            row = cursor.fetchone()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching record: {e}")
            return

        if not row:
            messagebox.showerror("Error", "Could not find the selected record in the database.")
            return

        rec_id, rec_date, chs_no, received_from, t_type, address_raw, ac_head, narration, amount = row
        mode = "BANK" if "BANK" in str(t_type).upper() else "CASH"

        # Parse address and bank info from stored format "address|Bank:bank_name"
        address = ""
        bank_name = ""
        cheque_no = ""
        cheque_date = ""
        if address_raw:
            if "|Bank:" in str(address_raw):
                parts = str(address_raw).split("|Bank:")
                address = parts[0]
                bank_name = parts[1] if len(parts) > 1 else ""
            else:
                address = str(address_raw)

        # Extract cheque info from narration if present
        if narration and "(Chq: " in str(narration):
            chq_start = str(narration).find("(Chq: ")
            chq_end = str(narration).find(")", chq_start)
            if chq_end > chq_start:
                cheque_no = str(narration)[chq_start + 6:chq_end]

        data = dict(
            voucher_type="Receipt",
            date_str=rec_date,
            voucher_no=chs_no,
            received_from=received_from,
            address=address,
            mode=mode,
            bank_name=bank_name,
            cheque_no=cheque_no,
            cheque_date=cheque_date,
            ac_head=ac_head,
            narration=narration,
            amount=float(amount),
        )

        try:
            filepath = generate_voucher_pdf(data)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not generate voucher PDF:\n{exc}")
            return

        open_for_printing(filepath)