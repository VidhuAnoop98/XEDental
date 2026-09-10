import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime 
import sqlite3
import os

class Doctors:
    def __init__(self,app):
        self.app = app
        self.patient_data = getattr(app, "patient_data", {})
        self.treatments_list = getattr(app, "treatments_list", [])
        self.accounts_list = getattr(app, "accounts_list", [])
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

    def get_doctor_list(self):
        names = []
        try:
            conn = sqlite3.connect(getattr(self.app, "db_path", "dental.db")) if not hasattr(self.app, "get_db_connection") else self.app.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT First_Name, Last_Name FROM Doctors ORDER BY First_Name, Last_Name")
            rows = cursor.fetchall()
            conn.close()
            for first, last in rows:
                fname = (first or "").strip()
                lname = (last or "").strip()
                full_name = f"{fname} {lname}".strip()
                if full_name:
                    if not full_name.lower().startswith("dr.") and not full_name.lower().startswith("dr "):
                        full_name = f"Dr. {full_name}"
                    if full_name not in names:
                        names.append(full_name)
        except Exception:
            pass
        return names

    def doctors_detials(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        # --- Top button bar ---
        top_bar = tk.Frame(self.app.workspace)
        top_bar.pack(side="top", fill="x", padx=5, pady=(5, 0))

        def back_to_bill():
            self.patient_data = {
                "patientid": self.bill_patientid.get(),
                "regno": self.bill_regno.get(),
                "patientname": self.bill_patientname.get(),
                "address1": self.bill_address1.get(),
                "address2": self.bill_address2.get(),
                "age": self.bill_age.get(),
                "gender": self.bill_gender.get(),
                "office": self.bill_office.get(),
                "residence": self.bill_residence.get(),
                "email": self.bill_email.get()
            }
            new_treatments = []
            for child in doc_tree.get_children():
                vals = doc_tree.item(child)["values"]
                tooth_val = str(vals[0]) if vals[0] and str(vals[0]) != "-" else ""
                treatment_val = str(vals[1])
                amount_val = str(vals[2])
                amount_paid_val = str(vals[3]) if len(vals) > 3 else ""
                doc_val = str(vals[4]) if len(vals) > 4 and vals[4] else "" 
                ttype_val = "General" if not tooth_val else "Teeth Based"
                new_treatments.append((tooth_val, treatment_val, amount_val, amount_paid_val, doc_val, ttype_val))
            self.treatments_list = new_treatments

            self.accounts_list = []
            for child in self.acc_tree.get_children():
                self.accounts_list.append(self.acc_tree.item(child)["values"])
            
            self.bill()

        # tk.Button(top_bar, text="← Back to Bill", font=("Arial", 10, "bold"),
        #           command=self.bill).pack(side="left", padx=5)

        # tk.Label(top_bar, text="Doctor's Details & Accounts", font=("Arial", 14, "bold")).pack(side="left", padx=20)

        # ================ Bottom Action Bar ================
        bottom_bar = tk.Frame(self.app.workspace)
        bottom_bar.pack(side="bottom", fill="x", padx=10, pady=5)

        btn_bill = tk.Button(bottom_bar, text="← Back to Bill", font=("Arial", 11, "bold"),
                             bg="#FF9800", fg="white", command=self.bill)
        btn_bill.pack(side="left", padx=10)

        btn_print = tk.Button(bottom_bar, text="Print Invoice / Receipt", font=("Arial", 11, "bold"),
                              bg="#4CAF50", fg="white", command=lambda: self.generate_bill_pdf(getattr(self, 'doc_tree', None), getattr(self, 'acc_tree', None)))
        btn_print.pack(side="left", padx=10)

        btn_save_db = tk.Button(bottom_bar, text="Save & Finalize Bill", font=("Arial", 11, "bold"),
                                bg="#2196F3", fg="white", command=lambda: self.save_bill_db(getattr(self, 'doc_tree', None), getattr(self, 'acc_tree', None)))
        btn_save_db.pack(side="left", padx=10)

        btn_close_details = tk.Button(bottom_bar, text="Close", font=("Arial", 11, "bold"),
                                      bg="#f44336", fg="white", command=self.close)
        btn_close_details.pack(side="right", padx=10)

        # --- Main content ---
        self.main_content = tk.Frame(self.app.workspace)
        self.main_content.pack(fill="both", expand=True, padx=5, pady=5)

        self.left_frame = tk.LabelFrame(self.main_content, text="Treatment Details", font=("Arial", 11, "bold"))
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.right_frame = tk.LabelFrame(self.main_content, text="Patient & Accounts", font=("Arial", 11, "bold"))
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # ================ Patient Details (Right) ================
        self.patient = tk.LabelFrame(self.right_frame, text="Patient Details", font=("Arial", 10, "bold"), width=330, height=330)
        self.patient.pack(side="top", padx=5, pady=5)
        self.patient.pack_propagate(False)

        # Row 0: Patient ID & Reg No
        self.bill_patientid = tk.Entry(self.patient, justify="center")
        self.bill_patientid.grid(row=0, column=0, padx=30, pady=2)

        self.bill_regno = tk.Entry(self.patient, justify="center")
        self.bill_regno.grid(row=0, column=1, padx=10, pady=2)

        # Row 1: Patient Name & Address 1
        self.bill_patientname = tk.Entry(self.patient, justify="center")
        self.bill_patientname.grid(row=1, column=0, padx=30, pady=2)

        self.bill_address1 = tk.Entry(self.patient, justify="center")
        self.bill_address1.grid(row=1, column=1, padx=10, pady=2)

        # Row 2: Address 2
        self.bill_address2 = tk.Entry(self.patient, width=36)
        self.bill_address2.grid(row=2, column=0, columnspan=2, padx=30, pady=2, sticky="we")

        # Row 3-4: Age & Sex
        tk.Label(self.patient, text="Age:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", padx=30)
        tk.Label(self.patient, text="Sex:", font=("Arial", 10, "bold")).grid(row=3, column=1, sticky="w", padx=2)

        self.bill_age = tk.Entry(self.patient, width=5)
        self.bill_age.grid(row=4, column=0, sticky="w", padx=30)

        self.bill_gender = ttk.Combobox(
            self.patient,
            values=["Male", "Female"],
            state="readonly",
            width=10
        )
        self.bill_gender.grid(row=4, column=1, sticky="w", padx=2)

        # Row 5: Phone Numbers
        self.bill_office = tk.Entry(self.patient, width=18)
        self.bill_office.grid(row=5, column=0, padx=30, pady=2, sticky="w")

        self.bill_residence = tk.Entry(self.patient, width=18)
        self.bill_residence.grid(row=5, column=1, padx=2, pady=2, sticky="w")

        # Row 6: Email
        self.bill_email = tk.Entry(self.patient, width=38)
        self.bill_email.grid(row=6, column=0, columnspan=2, padx=30, pady=2, sticky="we")

        # Populate patient details fields in doctors_details
        if self.patient_data.get("patientid"):
            self.bill_patientid.insert(0, self.patient_data["patientid"])
        if self.patient_data.get("regno"):
            self.bill_regno.insert(0, self.patient_data["regno"])
        if self.patient_data.get("patientname"):
            self.bill_patientname.insert(0, self.patient_data["patientname"])
        if self.patient_data.get("address1"):
            self.bill_address1.insert(0, self.patient_data["address1"])
        if self.patient_data.get("address2"):
            self.bill_address2.insert(0, self.patient_data["address2"])
        if self.patient_data.get("age"):
            self.bill_age.insert(0, self.patient_data["age"])
        if self.patient_data.get("gender"):
            self.bill_gender.set(self.patient_data["gender"])
        if self.patient_data.get("office"):
            self.bill_office.insert(0, self.patient_data["office"])
        if self.patient_data.get("residence"):
            self.bill_residence.insert(0, self.patient_data["residence"])
        if self.patient_data.get("email"):
            self.bill_email.insert(0, self.patient_data["email"])

        # Search bind on Return key
        def search_patient_details(event=None):
            pid = self.bill_patientid.get().strip()
            reg = self.bill_regno.get().strip()
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            row = None
            if pid:
                cursor.execute("SELECT * FROM Appointments WHERE id=?", (pid,))
                row = cursor.fetchone()
            elif reg:
                try:
                    num = int(reg.replace("REG-", ""))
                    cursor.execute("SELECT * FROM Appointments WHERE id=?", (num,))
                    row = cursor.fetchone()
                except ValueError:
                    cursor.execute("SELECT * FROM Appointments WHERE Contact=? OR Mobile_Number1=? OR Mobile_Number2=?", (reg, reg, reg))
                    row = cursor.fetchone()
            
            if row:
                self.bill_patientid.delete(0, 'end')
                self.bill_patientid.insert(0, str(row[0]))
                self.bill_regno.delete(0, 'end')
                self.bill_regno.insert(0, f"REG-{row[0]:04d}")
                self.bill_patientname.delete(0, 'end')
                self.bill_patientname.insert(0, row[1] if row[1] else "")
                self.bill_age.delete(0, 'end')
                self.bill_age.insert(0, row[2] if row[2] else "")
                self.bill_gender.set(row[3] if row[3] else "")
                self.bill_address1.delete(0, 'end')
                self.bill_address1.insert(0, row[5] if row[5] else "")
                self.bill_address2.delete(0, 'end')
                self.bill_address2.insert(0, row[6] if row[6] else "")
                self.bill_office.delete(0, 'end')
                self.bill_office.insert(0, row[7] if row[7] else "")
                self.bill_residence.delete(0, 'end')
                self.bill_residence.insert(0, row[8] if row[8] else "")
                self.bill_email.delete(0, 'end')
                self.bill_email.insert(0, row[11] if row[11] else "")
                
                # Sync back to local patient_data dict
                self.patient_data = {
                    "patientid": str(row[0]),
                    "regno": f"REG-{row[0]:04d}",
                    "patientname": row[1] if row[1] else "",
                    "address1": row[5] if row[5] else "",
                    "address2": row[6] if row[6] else "",
                    "age": row[2] if row[2] else "",
                    "gender": row[3] if row[3] else "",
                    "office": row[7] if row[7] else "",
                    "residence": row[8] if row[8] else "",
                    "email": row[11] if row[11] else ""
                }
                self.load_patient_accounts(row[0])
                self.load_patient_treatments(row[0])
            else:
                messagebox.showinfo("Not Found", "No patient record found.")
            conn.close()

        self.bill_patientid.bind("<Return>", search_patient_details)
        self.bill_regno.bind("<Return>", search_patient_details)

        # ================ Treatment Treeview (Left) ================
        self.tree_frame = tk.Frame(self.left_frame)
        self.tree_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # Treatment Treeview Container
        tree_container = tk.Frame(self.tree_frame)
        tree_container.pack(side="top", fill="both", expand=True, padx=5, pady=(5, 2))

        treat_columns = ("Tooth No", "Treatment", "Amount", "Amount Paid", "Doctor")
        doc_tree = ttk.Treeview(tree_container, column=treat_columns, show="headings", height=6)
        self.doc_tree = doc_tree
        for col in treat_columns:
            doc_tree.heading(col, text=col)
            doc_tree.column(col, width=80)
        doc_tree.pack(side="left", fill="both", expand=True)

        doc_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=doc_tree.yview)
        doc_scroll.pack(side="right", fill="y")
        doc_tree.configure(yscrollcommand=doc_scroll.set)

        # Treatment Control & Payment Bottom Bar
        treat_ctrl_frame = tk.Frame(self.tree_frame, bg="#EAE6DF", bd=1, relief="solid")
        treat_ctrl_frame.pack(side="bottom", fill="x", padx=5, pady=5)

        tk.Label(treat_ctrl_frame, text="Doctor:", font=("Arial", 9, "bold"), bg="#EAE6DF").pack(side="left", padx=(5, 2), pady=4)
        doc_list = self.get_doctor_list()

        def refresh_doctors_d_list():
            latest = self.get_doctor_list()
            self.doctors_entry['values'] = latest
            if latest and not self.doctors_entry.get():
                self.doctors_entry.set(latest[0])

        self.doctors_entry = ttk.Combobox(treat_ctrl_frame, values=doc_list, width=14, postcommand=refresh_doctors_d_list)
        if doc_list:
            self.doctors_entry.set(doc_list[0])
        self.doctors_entry.pack(side="left", padx=2, pady=4)

        tk.Label(treat_ctrl_frame, text="Amount Paid:", font=("Arial", 9, "bold"), bg="#EAE6DF").pack(side="left", padx=(8, 2), pady=4)
        self.amount_paid_entry = tk.Entry(treat_ctrl_frame, width=9)
        self.amount_paid_entry.pack(side="left", padx=2, pady=4)

        tk.Label(treat_ctrl_frame, text="Mode:", font=("Arial", 9, "bold"), bg="#EAE6DF").pack(side="left", padx=(6, 2), pady=4)
        self.pay_mode_combo = ttk.Combobox(treat_ctrl_frame, values=["Cash", "QR Code"], state="readonly", width=9, font=("Arial", 9))
        self.pay_mode_combo.set("Cash")
        self.pay_mode_combo.pack(side="left", padx=2, pady=4)

        self.total_label = tk.Label(treat_ctrl_frame, text="Total: ₹0.00", font=("Arial", 11, "bold"), fg="green", bg="#EAE6DF")
        self.total_label.pack(side="right", padx=8, pady=4)

        def update_total():
            total = 0.0
            for child in doc_tree.get_children():
                try:
                    total += float(doc_tree.item(child)["values"][2])
                except (ValueError, IndexError):
                    pass
            self.total_label.config(text=f"Total: ₹{total:.2f}")
            self.sync_doc_tree_to_acc_tree()

        self.update_total = update_total

        def add_payment(event=None):
            selected = doc_tree.selection()
            paid_str = self.amount_paid_entry.get().strip()
            selected_doc = self.doctors_entry.get().strip()
            pay_mode = self.pay_mode_combo.get().strip() if hasattr(self, 'pay_mode_combo') and self.pay_mode_combo else "Cash"

            if not paid_str:
                messagebox.showwarning("Input Required", "Please enter Amount Paid.")
                return

            try:
                p_val = float(paid_str)
                formatted_paid = f"{p_val:.2f}"
            except ValueError:
                messagebox.showwarning("Input Error", "Please enter a valid numeric Amount Paid.")
                return

            if selected:
                for item_id in selected:
                    vals = list(doc_tree.item(item_id)["values"])
                    while len(vals) < 5:
                        vals.append("")
                    vals[3] = formatted_paid
                    if not vals[4] or not str(vals[4]).strip():
                        vals[4] = selected_doc
                    if len(vals) > 5:
                        vals[5] = pay_mode
                    else:
                        vals.append(pay_mode)
                    doc_tree.item(item_id, values=vals)
            else:
                unpaid_item = None
                for child in doc_tree.get_children():
                    v = doc_tree.item(child)["values"]
                    if len(v) <= 3 or not v[3] or str(v[3]).strip() in ["", "0.00"]:
                        unpaid_item = child
                        break

                if unpaid_item:
                    vals = list(doc_tree.item(unpaid_item)["values"])
                    while len(vals) < 5:
                        vals.append("")
                    vals[3] = formatted_paid
                    if not vals[4] or not str(vals[4]).strip():
                        vals[4] = selected_doc
                    if len(vals) > 5:
                        vals[5] = pay_mode
                    else:
                        vals.append(pay_mode)
                    doc_tree.item(unpaid_item, values=vals)
                else:
                    payment_desc = f"Payment ({pay_mode})"
                    doc_tree.insert("", "end", values=("-", payment_desc, "0.00", formatted_paid, selected_doc, pay_mode))

            self.amount_paid_entry.delete(0, 'end')
            update_total()

        self.amount_paid_entry.bind("<Return>", add_payment)

        def delete_row():
            selected = doc_tree.selection()
            if selected:
                for item in selected:
                    doc_tree.delete(item)
                update_total()
            else:
                messagebox.showwarning("No Selection", "Please select a row to delete.")

        tk.Button(treat_ctrl_frame, text="Add Payment", command=add_payment, bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=4, pady=4)
        tk.Button(treat_ctrl_frame, text="Delete Row", command=delete_row, fg="red", font=("Arial", 9)).pack(side="left", padx=4, pady=4)

        def on_doc_tree_select(event):
            selected = doc_tree.selection()
            if selected:
                vals = doc_tree.item(selected[0])["values"]
                if len(vals) > 3 and vals[3] and str(vals[3]).strip():
                    self.amount_paid_entry.delete(0, 'end')
                    self.amount_paid_entry.insert(0, str(vals[3]))
                elif len(vals) > 2 and vals[2]:
                    self.amount_paid_entry.delete(0, 'end')
                    self.amount_paid_entry.insert(0, str(vals[2]))
                if len(vals) > 4 and vals[4]:
                    self.doctors_entry.set(str(vals[4]))

        doc_tree.bind("<<TreeviewSelect>>", on_doc_tree_select)

        # Populate doc_tree from treatments list
        for item in self.treatments_list:
            tooth = item[0] if len(item) > 0 and item[0] else "-"
            treatment = item[1] if len(item) > 1 else ""
            try:
                amount = f"{float(item[2]):.2f}" if len(item) > 2 and item[2] else "0.00"
            except (ValueError, TypeError):
                amount = item[2] if len(item) > 2 else "0.00"

            amount_paid = ""
            doc = ""
            if len(item) >= 5:
                # check if index 3 is amount_paid or doc
                try:
                    p_num = float(item[3])
                    amount_paid = f"{p_num:.2f}"
                    doc = item[4] if len(item) > 4 else ""
                except (ValueError, TypeError):
                    doc = item[3] if item[3] else ""
                    if len(item) > 4 and item[4]:
                        try:
                            p_num = float(item[4])
                            amount_paid = f"{p_num:.2f}"
                        except (ValueError, TypeError):
                            pass
            elif len(item) == 4:
                doc = item[3] if item[3] else ""

            doc_tree.insert("", "end", values=(tooth, treatment, amount, amount_paid, doc), tags=("present_row",))
        update_total()

        if self.patient_data.get("patientid") and not doc_tree.get_children():
            self.load_patient_treatments(self.patient_data["patientid"])

        # ================ Accounts Section (Right - Bottom) ================
        self.accounts = tk.LabelFrame(self.right_frame, text="Accounts", font=("Arial", 10, "bold"))
        self.accounts.pack(side="bottom", fill="both", expand=True, padx=5, pady=5)

        # Account input row for adding present entries
        # acc_input_frame = tk.Frame(self.accounts)
        # acc_input_frame.pack(fill="x", padx=10, pady=(5, 0))

        # tk.Label(acc_input_frame, text="Date:").grid(row=0, column=0, padx=2, pady=2)
        # self.acc_date_entry = tk.Entry(acc_input_frame, width=10)
        # self.acc_date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        # self.acc_date_entry.grid(row=0, column=1, padx=2, pady=2)

        # tk.Label(acc_input_frame, text="Particulars:").grid(row=0, column=2, padx=2, pady=2)
        # self.acc_particulars_entry = tk.Entry(acc_input_frame, width=14)
        # self.acc_particulars_entry.grid(row=0, column=3, padx=2, pady=2)

        # tk.Label(acc_input_frame, text="Debit:").grid(row=0, column=4, padx=2, pady=2)
        # self.acc_debit_entry = tk.Entry(acc_input_frame, width=8)
        # self.acc_debit_entry.grid(row=0, column=5, padx=2, pady=2)

        # tk.Label(acc_input_frame, text="Credit:").grid(row=0, column=6, padx=2, pady=2)
        # self.acc_credit_entry = tk.Entry(acc_input_frame, width=8)
        # self.acc_credit_entry.grid(row=0, column=7, padx=2, pady=2)

        # btn_add_acc = tk.Button(acc_input_frame, text="+ Add Present Entry", font=("Arial", 9, "bold"), bg="#4CAF50", fg="white", command=self.add_manual_acc_item)
        # btn_add_acc.grid(row=0, column=8, padx=4, pady=2)

        # btn_del_acc = tk.Button(acc_input_frame, text="Delete Entry", font=("Arial", 9, "bold"), bg="#F44336", fg="white", command=self.delete_acc_row)
        # btn_del_acc.grid(row=0, column=9, padx=4, pady=2)

        acc_columns = ("Date", "Debit", "Credit", "Particulars", "Balance")
        self.acc_tree = ttk.Treeview(self.accounts, columns=acc_columns, show="headings", height=4)
        for col in acc_columns:
            self.acc_tree.heading(col, text=col)
            self.acc_tree.column(col, width=80)

        # Configure row colors: Red for Debit/Negative, Green for Credit/Positive
        self.acc_tree.tag_configure("debit_row", foreground="#D32F2F")
        self.acc_tree.tag_configure("credit_row", foreground="#2E7D32")

        # Balance label
        self.balance_label = tk.Label(self.accounts, text="Balance: ₹0.00", font=("Arial", 11, "bold"), fg="#D32F2F")

        self.sync_doc_tree_to_acc_tree()

        self.acc_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.balance_label.pack(padx=10, pady=5, anchor="e")

        # Populate accounts list
        pid_val = self.patient_data.get("patientid") if hasattr(self, 'patient_data') and self.patient_data else ""
        if pid_val:
            self.load_patient_accounts(pid_val)
        elif not hasattr(self, 'accounts_list') or not self.accounts_list:
            self.accounts_list = []
            date_str = datetime.now().strftime("%d-%m-%Y")
            balance = 0.0
            for item in getattr(self, 'treatments_list', []):
                tooth = item[0] if len(item) > 0 and item[0] else "-"
                treatment = item[1] if len(item) > 1 else "Treatment"
                amount = item[2] if len(item) > 2 else "0.00"

                if len(item) >= 5 and (str(item[4]) in ("Teeth Based", "General") or str(item[3]).startswith("Dr.")):
                    amount_paid = "0.00"
                elif len(item) >= 5:
                    amount_paid = item[3] if item[3] else "0.00"
                else:
                    amount_paid = "0.00"

                deb = float(amount) if amount else 0.0
                crd = float(amount_paid) if amount_paid else 0.0
                balance += deb - crd
                self.acc_tree.insert("", "end", values=(date_str, f"{deb:.2f}", f"{crd:.2f}", treatment, f"{balance:.2f}"))
            calculate_balance()
        else:
            for item in self.accounts_list:
                self.acc_tree.insert("", "end", values=item)
            calculate_balance()



    def add_manual_acc_item(self):
        if not hasattr(self, 'manual_present_acc_items'):
            self.manual_present_acc_items = []

        date_val = self.acc_date_entry.get().strip() if hasattr(self, 'acc_date_entry') else datetime.now().strftime("%d-%m-%Y")
        particulars_val = self.acc_particulars_entry.get().strip() if hasattr(self, 'acc_particulars_entry') else ""
        
        try:
            debit_val = float(self.acc_debit_entry.get().strip()) if hasattr(self, 'acc_debit_entry') and self.acc_debit_entry.get().strip() else 0.0
        except ValueError:
            debit_val = 0.0

        try:
            credit_val = float(self.acc_credit_entry.get().strip()) if hasattr(self, 'acc_credit_entry') and self.acc_credit_entry.get().strip() else 0.0
        except ValueError:
            credit_val = 0.0

        if not particulars_val and debit_val == 0.0 and credit_val == 0.0:
            messagebox.showwarning("Input Error", "Please enter Particulars, Debit, or Credit amount.")
            return

        if not particulars_val:
            particulars_val = "Additional Charge" if debit_val > 0 else "Payment Received"

        self.manual_present_acc_items.append({
            "date": date_val or datetime.now().strftime("%d-%m-%Y"),
            "debit": debit_val,
            "credit": credit_val,
            "particulars": particulars_val
        })

        if hasattr(self, 'acc_debit_entry'): self.acc_debit_entry.delete(0, 'end')
        if hasattr(self, 'acc_credit_entry'): self.acc_credit_entry.delete(0, 'end')
        if hasattr(self, 'acc_particulars_entry'): self.acc_particulars_entry.delete(0, 'end')

        self.sync_doc_tree_to_acc_tree()

    def delete_acc_row(self):
        if not hasattr(self, 'acc_tree') or not self.acc_tree:
            return
        selected = self.acc_tree.selection()
        if selected:
            for item in selected:
                vals = self.acc_tree.item(item)["values"]
                tags = self.acc_tree.item(item).get("tags", [])
                if "past_row" in tags:
                    messagebox.showwarning("Cannot Delete", "Past finalized accounts cannot be deleted from present bill.")
                    continue
                if hasattr(self, 'manual_present_acc_items') and vals:
                    self.manual_present_acc_items = [
                        m for m in self.manual_present_acc_items
                        if not (m["particulars"] == str(vals[3]) and float(m["debit"]) == float(vals[1] or 0) and float(m["credit"]) == float(vals[2] or 0))
                    ]
                self.acc_tree.delete(item)
            self.sync_doc_tree_to_acc_tree()
        else:
            messagebox.showwarning("No Selection", "Please select a present entry to delete.")

    def sync_doc_tree_to_acc_tree(self):
        if not hasattr(self, 'acc_tree') or not self.acc_tree:
            return
        for child in self.acc_tree.get_children():
            self.acc_tree.delete(child)

        date_str = datetime.now().strftime("%d-%m-%Y")
        running_balance = 0.0

        pid_val = ""
        if hasattr(self, 'patient_data') and self.patient_data:
            pid_val = self.patient_data.get("patientid", "")
        if not pid_val and hasattr(self, 'bill_patientid') and self.bill_patientid:
            pid_val = self.bill_patientid.get().strip()

        past_rows = []
        if pid_val:
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                pid_str = str(pid_val).strip()
                reg_str = f"REG-{int(pid_str):04d}" if pid_str.isdigit() else pid_str
                cursor.execute("""
                    SELECT ba.Date, ba.Debit, ba.Credit, ba.Particulars, ba.Balance
                    FROM Bill_Accounts ba
                    JOIN Bills b ON ba.Bill_ID = b.id
                    WHERE b.Patient_ID = ? OR b.Reg_No = ?
                    ORDER BY ba.id ASC
                """, (pid_str, reg_str))
                past_rows = cursor.fetchall()
                conn.close()
            except Exception as e:
                print(f"Error fetching past accounts: {e}")

        has_today_in_past = False
        for row in past_rows:
            date_val, debit_val, credit_val, part_val, bal_val = row
            d_num = float(debit_val) if debit_val else 0.0
            c_num = float(credit_val) if credit_val else 0.0
            running_balance += d_num - c_num
            if str(date_val).strip() == date_str:
                has_today_in_past = True
            row_tag = ("past_row", "debit_row" if d_num > 0 or c_num == 0 else "credit_row")
            self.acc_tree.insert("", "end", values=(date_val, f"{d_num:.2f}", f"{c_num:.2f}", part_val, f"{running_balance:.2f}"), tags=row_tag)

        has_present_items = False
        if hasattr(self, 'doc_tree') and self.doc_tree:
            for child in self.doc_tree.get_children():
                tags = self.doc_tree.item(child).get("tags", [])
                if "past_row" in tags:
                    continue
                vals = self.doc_tree.item(child)["values"]
                if not vals:
                    continue
                particulars = str(vals[1]) if len(vals) > 1 and vals[1] else "Treatment"
                try:
                    debit = float(vals[2]) if len(vals) > 2 and vals[2] else 0.0
                except (ValueError, TypeError):
                    debit = 0.0
                try:
                    credit = float(vals[3]) if len(vals) > 3 and vals[3] else 0.0
                except (ValueError, TypeError):
                    credit = 0.0

                if debit == 0 and credit == 0:
                    continue

                has_present_items = True

                if debit > 0 or credit == 0:
                    running_balance += debit
                    self.acc_tree.insert("", "end", values=(
                        date_str,
                        f"{debit:.2f}",
                        "0.00",
                        particulars,
                        f"{running_balance:.2f}"
                    ), tags=("present_row", "debit_row"))

                if credit > 0:
                    running_balance -= credit
                    mode_str = str(vals[5]) if len(vals) > 5 and vals[5] else (self.pay_mode_combo.get().strip() if hasattr(self, 'pay_mode_combo') and self.pay_mode_combo else "Cash")
                    payment_desc = mode_str if mode_str in ["Cash", "QR Code"] else f"{mode_str} Payment"
                    self.acc_tree.insert("", "end", values=(
                        date_str,
                        "0.00",
                        f"{credit:.2f}",
                        payment_desc,
                        f"{running_balance:.2f}"
                    ), tags=("present_row", "credit_row"))

        # Also append manual present entries
        if hasattr(self, 'manual_present_acc_items'):
            for item in self.manual_present_acc_items:
                m_date = item.get("date", date_str)
                m_deb = float(item.get("debit", 0.0))
                m_crd = float(item.get("credit", 0.0))
                m_part = item.get("particulars", "Entry")

                if m_deb > 0 or m_crd == 0:
                    has_present_items = True
                    running_balance += m_deb
                    self.acc_tree.insert("", "end", values=(
                        m_date,
                        f"{m_deb:.2f}",
                        "0.00",
                        m_part,
                        f"{running_balance:.2f}"
                    ), tags=("present_row", "debit_row"))

                if m_crd > 0:
                    has_present_items = True
                    running_balance -= m_crd
                    self.acc_tree.insert("", "end", values=(
                        m_date,
                        "0.00",
                        f"{m_crd:.2f}",
                        m_part,
                        f"{running_balance:.2f}"
                    ), tags=("present_row", "credit_row"))

        if past_rows and not has_present_items and not has_today_in_past:
            row_tag = ("past_row", "debit_row" if running_balance > 0 else "credit_row")
            self.acc_tree.insert("", "end", values=(date_str, "0.00", "0.00", "Balance B/F", f"{running_balance:.2f}"), tags=row_tag)

        if hasattr(self, 'balance_label') and self.balance_label:
            lbl_color = "#D32F2F" if running_balance > 0 else "#2E7D32"
            self.balance_label.config(text=f"Balance: ₹{running_balance:.2f}", fg=lbl_color)

    def load_patient_treatments(self, patient_id):
        if not hasattr(self, 'doc_tree') or not self.doc_tree:
            return
        for child in self.doc_tree.get_children():
            self.doc_tree.delete(child)
        
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            pid_str = str(patient_id).strip()
            reg_str = f"REG-{int(pid_str):04d}" if pid_str.isdigit() else pid_str
            cursor.execute("""
                SELECT bt.Tooth_No, bt.Treatment, bt.Amount,
                       COALESCE((SELECT SUM(ba.Credit) FROM Bill_Accounts ba WHERE ba.Bill_ID = bt.Bill_ID AND (ba.Particulars = bt.Treatment OR ba.Particulars = 'Payment Received')), 0.0) AS Paid,
                       bt.Doctor
                FROM Bill_Treatments bt
                JOIN Bills b ON bt.Bill_ID = b.id
                WHERE b.Patient_ID = ? OR b.Reg_No = ?
                ORDER BY bt.id ASC
            """, (pid_str, reg_str))
            rows = cursor.fetchall()
            conn.close()

            for r in rows:
                tooth = r[0] if r[0] else "-"
                treatment = r[1] if r[1] else ""
                amount = f"{float(r[2]):.2f}" if r[2] else "0.00"
                paid_val = float(r[3]) if r[3] else 0.0
                paid_str = f"{paid_val:.2f}" if paid_val > 0 else ""
                doc = r[4] if r[4] else ""
                self.doc_tree.insert("", "end", values=(tooth, treatment, amount, paid_str, doc), tags=("past_row",))
            if hasattr(self, 'update_total') and callable(self.update_total):
                self.update_total()
        except Exception as e:
            print(f"Error loading doctor treatments: {e}")

    def load_patient_accounts(self, patient_id):
        if not hasattr(self, 'acc_tree') or not self.acc_tree:
            return
        for child in self.acc_tree.get_children():
            self.acc_tree.delete(child)
        
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            pid_str = str(patient_id).strip()
            reg_str = f"REG-{int(pid_str):04d}" if pid_str.isdigit() else pid_str
            cursor.execute("""
                SELECT ba.Date, ba.Debit, ba.Credit, ba.Particulars, ba.Balance
                FROM Bill_Accounts ba
                JOIN Bills b ON ba.Bill_ID = b.id
                WHERE b.Patient_ID = ? OR b.Reg_No = ?
                ORDER BY ba.id ASC
            """, (pid_str, reg_str))
            rows = cursor.fetchall()
            conn.close()

            balance = 0.0
            has_today = False
            today_str = datetime.now().strftime("%d-%m-%Y")

            for row in rows:
                date_val, debit_val, credit_val, part_val, bal_val = row
                d_num = float(debit_val) if debit_val else 0.0
                c_num = float(credit_val) if credit_val else 0.0
                balance += d_num - c_num
                if str(date_val).strip() == today_str:
                    has_today = True
                row_tag = "debit_row" if d_num > 0 or c_num == 0 else "credit_row"
                self.acc_tree.insert("", "end", values=(date_val, f"{d_num:.2f}", f"{c_num:.2f}", part_val, f"{balance:.2f}"), tags=(row_tag,))

            # If past transactions exist and today's save date ("now") is not present,
            # automatically append current save date row carrying forward past balance to now.
            if rows and not has_today:
                row_tag = "debit_row" if balance > 0 else "credit_row"
                self.acc_tree.insert("", "end", values=(today_str, "0.00", "0.00", "Balance B/F", f"{balance:.2f}"), tags=(row_tag,))

            if hasattr(self, 'balance_label'):
                lbl_color = "#D32F2F" if balance > 0 else "#2E7D32"
                self.balance_label.config(text=f"Balance: ₹{balance:.2f}", fg=lbl_color)
        except Exception as e:
            print(f"Error loading accounts: {e}")

    def bill(self):
        """Navigate back to the Bill view, passing updated patient data, treatment items, and account items."""
        if hasattr(self, 'bill_patientid') and self.bill_patientid:
            self.patient_data["patientid"] = self.bill_patientid.get().strip()
        if hasattr(self, 'bill_regno') and self.bill_regno:
            self.patient_data["regno"] = self.bill_regno.get().strip()
        if hasattr(self, 'bill_patientname') and self.bill_patientname:
            self.patient_data["patientname"] = self.bill_patientname.get().strip()
        if hasattr(self, 'bill_address1') and self.bill_address1:
            self.patient_data["address1"] = self.bill_address1.get().strip()
        if hasattr(self, 'bill_address2') and self.bill_address2:
            self.patient_data["address2"] = self.bill_address2.get().strip()
        if hasattr(self, 'bill_age') and self.bill_age:
            self.patient_data["age"] = self.bill_age.get().strip()
        if hasattr(self, 'bill_gender') and self.bill_gender:
            self.patient_data["gender"] = self.bill_gender.get().strip()
        if hasattr(self, 'bill_office') and self.bill_office:
            self.patient_data["office"] = self.bill_office.get().strip()
        if hasattr(self, 'bill_residence') and self.bill_residence:
            self.patient_data["residence"] = self.bill_residence.get().strip()
        if hasattr(self, 'bill_email') and self.bill_email:
            self.patient_data["email"] = self.bill_email.get().strip()
        if hasattr(self, 'bill_notes') and self.bill_notes:
            self.patient_data["comments"] = self.bill_notes.get("1.0", "end-1c").strip()

        # Sync doc_tree items back to treatments_list
        if hasattr(self, 'doc_tree') and self.doc_tree:
            updated_trts = []
            for child in self.doc_tree.get_children():
                vals = self.doc_tree.item(child)["values"]
                if vals:
                    tooth = str(vals[0]) if len(vals) > 0 and vals[0] else "-"
                    trt = str(vals[1]) if len(vals) > 1 and vals[1] else ""
                    amt = str(vals[2]) if len(vals) > 2 and vals[2] else "0.00"
                    paid = str(vals[3]) if len(vals) > 3 and vals[3] else ""
                    doc = str(vals[4]) if len(vals) > 4 and vals[4] else ""
                    updated_trts.append((tooth, trt, amt, paid, doc))
            if updated_trts:
                self.treatments_list = updated_trts

        # Sync acc_tree items back to accounts_list
        if hasattr(self, 'acc_tree') and self.acc_tree:
            updated_accs = []
            for child in self.acc_tree.get_children():
                vals = self.acc_tree.item(child)["values"]
                if vals:
                    updated_accs.append(vals)
            if updated_accs:
                self.accounts_list = updated_accs

        from bill import Bill  # lazy import to avoid circular dependency
        b = Bill(self.app)
        b.patient_data = self.patient_data
        b.treatments_list = getattr(self, 'treatments_list', [])
        b.accounts_list = getattr(self, 'accounts_list', [])
        b.bill()

    def close(self):
        self.bill()

    def save_bill_db(self, doc_tree, acc_tree):
        p_name = self.bill_patientname.get().strip()
        p_id = self.bill_patientid.get().strip()
        reg_no = self.bill_regno.get().strip()

        if not p_name:
            messagebox.showwarning("Save Failed", "Patient Name is required to save the bill.")
            return

        # Treatments summary
        total_amt = 0.0
        treatments = []
        for child in doc_tree.get_children():
            values = doc_tree.item(child)["values"]
            try:
                amt = float(values[2])
            except (ValueError, IndexError):
                amt = 0.0
            total_amt += amt
            treatments.append(values)

        # Accounts summary
        total_debit = 0.0
        total_credit = 0.0
        new_accounts = []
        all_accounts = []
        acc_tree_obj = acc_tree if acc_tree is not None else getattr(self, 'acc_tree', None)
        if acc_tree_obj:
            for child in acc_tree_obj.get_children():
                item_data = acc_tree_obj.item(child)
                values = item_data["values"]
                tags = item_data.get("tags", [])
                try:
                    deb = float(values[1]) if values[1] else 0.0
                except (ValueError, IndexError):
                    deb = 0.0
                try:
                    crd = float(values[2]) if values[2] else 0.0
                except (ValueError, IndexError):
                    crd = 0.0
                total_debit += deb
                total_credit += crd
                all_accounts.append(values)
                if "present_row" in tags or not tags or "past_row" not in tags:
                    new_accounts.append(values)

        balance_due = total_debit - total_credit
        current_date = datetime.now().strftime("%d-%m-%Y")
        comments = self.bill_notes.get("1.0", "end-1c") if hasattr(self, 'bill_notes') and self.bill_notes else ""
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()

            # Insert Bill header
            cursor.execute('''
                INSERT INTO Bills (Patient_ID, Reg_No, Patient_Name, Date, Total_Amount, Balance_Due, Comments)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (p_id, reg_no, p_name, current_date, total_amt, balance_due, comments))
            bill_id = cursor.lastrowid

            # Insert treatments
            for treat in treatments:
                ttype = "Teeth Based"
                for old in getattr(self, 'treatments_list', []):
                    if str(old[0]) == str(treat[0]) and str(old[1]) == str(treat[1]) and str(old[2]) == str(treat[2]) and str(old[3]) == str(treat[3]):
                        ttype = old[4] if len(old) > 4 else "Teeth Based"
                        break
                doctor_name = str(treat[4]).strip() if len(treat) > 4 and treat[4] else "" 
                cursor.execute('''
                    INSERT INTO Bill_Treatments (Bill_ID, Tooth_No, Treatment, Amount, Doctor, Type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (bill_id, str(treat[0]), str(treat[1]), float(treat[2]), doctor_name, ttype))

            # Insert accounts (saving newly added present entries)
            accounts_to_save = new_accounts if new_accounts else all_accounts
            for acc in accounts_to_save:
                cursor.execute('''
                    INSERT INTO Bill_Accounts (Bill_ID, Date, Debit, Credit, Particulars, Balance)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (bill_id, str(acc[0]), float(acc[1]) if acc[1] else 0.0, float(acc[2]) if acc[2] else 0.0, str(acc[3]), float(acc[4]) if acc[4] else 0.0))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Bill details successfully saved to Database (Bill ID: {bill_id})!")
            self.manual_present_acc_items = []
            if p_id:
                self.load_patient_treatments(p_id)
                self.load_patient_accounts(p_id)
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving bill: {e}")

    def generate_bill_pdf(self, doc_tree, acc_tree):
        p_name = self.bill_patientname.get().strip()
        p_id = self.bill_patientid.get().strip()
        reg_no = self.bill_regno.get().strip()
        age = self.bill_age.get().strip()
        gender = self.bill_gender.get().strip()
        addr1 = self.bill_address1.get().strip()
        addr2 = self.bill_address2.get().strip()
        office = self.bill_office.get().strip()
        residence = self.bill_residence.get().strip()
        email = self.bill_email.get().strip()
        
        # Collect treatments
        treatments = []
        total_treatment_cost = 0.0
        for child in doc_tree.get_children():
            values = doc_tree.item(child)["values"]
            try:
                amt = float(values[2])
            except (ValueError, IndexError):
                amt = 0.0
            total_treatment_cost += amt
            treatments.append(values)
            
        # Collect accounts
        accounts = []
        total_debit = 0.0
        total_credit = 0.0
        for child in acc_tree.get_children():
            values = acc_tree.item(child)["values"]
            try:
                deb = float(values[1]) if values[1] else 0.0
            except (ValueError, IndexError):
                deb = 0.0
            try:
                crd = float(values[2]) if values[2] else 0.0
            except (ValueError, IndexError):
                crd = 0.0
            total_debit += deb
            total_credit += crd
            accounts.append(values)
            
        balance_due = total_debit - total_credit

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
        except ImportError:
            messagebox.showerror("Error", "ReportLab library is required. Install it using 'pip install reportlab'.")
            return
            
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, f"dental_bill_{p_id}.pdf" if p_id else "dental_bill.pdf")
        pdf = canvas.Canvas(output_path, pagesize=A4)
        
        # Page size and dimensions
        width, height = A4
        
        # Draw Header & Logo matching letter_paper.py style
        logo_path = os.path.join(script_dir, "Dental_logo.png")
        if os.path.isfile(logo_path):
            try:
                from reportlab.lib.utils import ImageReader
                img = ImageReader(logo_path)
                iw, ih = img.getSize()
                box = 50.0
                scale = min(box / iw, box / ih)
                w, h = iw * scale, ih * scale
                pdf.drawImage(img, 40, height - 60, width=w, height=h, mask="auto", preserveAspectRatio=True)
            except Exception:
                pass
        
        # Header text & Clinic Settings lookup
        c_name = "ANUPAM DENTAL CLINIC"
        c_addr = "West Gate Vaikom - 686141"
        phone_str, resi_str = "Clinic : 9446046868", "Resi   : 216858"
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM Clinic_Settings")
            c_rows = dict(cursor.fetchall())
            conn.close()
            c_name = (c_rows.get("clinic_work_name") or c_rows.get("clinic_name") or "ANUPAM DENTAL CLINIC").strip()
            c_addr_name = (c_rows.get("clinic_address_name") or "West Gate Vaikom").strip()
            c_pin = (c_rows.get("clinic_pincode") or "686141").strip()
            if c_pin and c_pin not in c_addr_name:
                c_addr = f"{c_addr_name} - {c_pin}"
            else:
                c_addr = c_addr_name if c_addr_name else "West Gate Vaikom - 686141"

            mob = c_rows.get("clinic_mobile") or c_rows.get("clinic_phone") or "9446046868"
            wrk = c_rows.get("clinic_work") or c_rows.get("clinic_resi") or "216858"
            phone_str = mob if ("Clinic" in mob or "clinic" in mob) else f"Clinic : {mob}"
            resi_str = wrk if ("Resi" in wrk or "resi" in wrk) else f"Resi   : {wrk}"
        except Exception:
            pass

        pdf.setFont("Times-Bold", 20)
        pdf.setFillColor(colors.HexColor("#1A365D")) # Premium dark blue
        pdf.drawCentredString(width / 2.0, height - 35, c_name)
        
        pdf.setFont("Helvetica", 9)
        pdf.setFillColor(colors.HexColor("#4A5568"))
        pdf.drawCentredString(width / 2.0, height - 50, c_addr)
            
        pdf.setFont("Helvetica", 9)
        pdf.drawRightString(width - 40, height - 38, phone_str)
        pdf.drawRightString(width - 40, height - 50, resi_str)
        
        # Header separator line
        pdf.setStrokeColor(colors.HexColor("#1A365D"))
        pdf.setLineWidth(1)
        pdf.line(40, height - 68, width - 40, height - 68)
        
        # Invoice Title
        pdf.setFont("Helvetica-Bold", 14)
        pdf.setFillColor(colors.HexColor("#1A365D"))
        pdf.drawString(40, height - 92, "INVOICE / RECEIPT")
        
        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(colors.HexColor("#4A5568"))
        pdf.drawRightString(width - 40, height - 92, f"Date: {datetime.now().strftime('%d-%m-%Y')}")
        pdf.drawRightString(width - 40, height - 107, f"Invoice No: INV-{datetime.now().strftime('%Y%m')}-{p_id if p_id else '0000'}")
        
        # Patient Info Block (Left Column)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.setFillColor(colors.HexColor("#2D3748"))
        pdf.drawString(45, height - 132, "Billed To:")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(45, height - 147, f"Patient Name: {p_name}")
        pdf.drawString(45, height - 162, f"Patient ID: {p_id}   |   Reg No: {reg_no}")
        pdf.drawString(45, height - 177, f"Age / Sex: {age} / {gender}")
        pdf.drawString(45, height - 192, f"Address: {addr1}, {addr2}")
        pdf.drawString(45, height - 207, f"Phone: {office} (O), {residence} (R)")
        pdf.drawString(45, height - 222, f"Email: {email}")
        
        # Box background for Patient Info
        pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
        pdf.setLineWidth(0.5)
        pdf.rect(40, height - 230, width - 80, 110)
        
        # Treatment details table header
        y = height - 260
        pdf.setFont("Helvetica-Bold", 11)
        pdf.setFillColor(colors.HexColor("#1A365D"))
        pdf.drawString(40, y, "Treatment Details")
        
        y -= 15
        # Draw treatment table headers
        pdf.setFillColor(colors.HexColor("#F7FAFC"))
        pdf.rect(40, y - 20, width - 80, 20, fill=True, stroke=False)
        pdf.setFillColor(colors.HexColor("#2D3748"))
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(45, y - 14, "SI No.")
        pdf.drawString(90, y - 14, "Tooth No")
        pdf.drawString(170, y - 14, "Treatment Description")
        pdf.drawString(370, y - 14, "Doctor")
        pdf.drawRightString(width - 45, y - 14, "Amount (INR)")
        
        pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
        pdf.line(40, y - 20, width - 40, y - 20)
        
        y -= 20
        pdf.setFont("Helvetica", 9)
        si = 1
        for treat in treatments:
            if y < 150:
                pdf.showPage()
                y = height - 100
                pdf.setFont("Helvetica", 9)
            
            # Row alternating background (subtle)
            if si % 2 == 0:
                pdf.setFillColor(colors.HexColor("#F7FAFC"))
                pdf.rect(40, y - 18, width - 80, 18, fill=True, stroke=False)
                pdf.setFillColor(colors.HexColor("#2D3748"))
                
            pdf.drawString(45, y - 13, str(si))
            pdf.drawString(90, y - 13, str(treat[0]))
            pdf.drawString(170, y - 13, str(treat[1]))
            doctor_name = str(treat[4]) if len(treat) > 4 and treat[4] else "" 
            pdf.drawString(370, y - 13, doctor_name)
            pdf.drawRightString(width - 45, y - 13, f"{float(treat[2]):.2f}" if treat[2] else "0.00")
            pdf.line(40, y - 18, width - 40, y - 18)
            y -= 18
            si += 1
            
        # Draw treatment total
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(370, y - 15, "Subtotal:")
        pdf.drawRightString(width - 45, y - 15, f"{total_treatment_cost:.2f}")
        y -= 25
        
        # Accounts section
        if accounts:
            if y < 180:
                pdf.showPage()
                y = height - 100
                
            pdf.setFont("Helvetica-Bold", 11)
            pdf.setFillColor(colors.HexColor("#1A365D"))
            pdf.drawString(40, y, "Account Statement / Payments")
            
            y -= 15
            pdf.setFillColor(colors.HexColor("#F7FAFC"))
            pdf.rect(40, y - 20, width - 80, 20, fill=True, stroke=False)
            pdf.setFillColor(colors.HexColor("#2D3748"))
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(45, y - 14, "Date")
            pdf.drawString(130, y - 14, "Particulars")
            pdf.drawRightString(320, y - 14, "Debit (Dr)")
            pdf.drawRightString(420, y - 14, "Credit (Cr)")
            pdf.drawRightString(width - 45, y - 14, "Running Balance")
            
            pdf.line(40, y - 20, width - 40, y - 20)
            y -= 20
            
            pdf.setFont("Helvetica", 9)
            si_acc = 1
            for acc in accounts:
                if y < 100:
                    pdf.showPage()
                    y = height - 100
                    pdf.setFont("Helvetica", 9)
                    
                if si_acc % 2 == 0:
                    pdf.setFillColor(colors.HexColor("#F7FAFC"))
                    pdf.rect(40, y - 18, width - 80, 18, fill=True, stroke=False)
                    pdf.setFillColor(colors.HexColor("#2D3748"))
                    
                pdf.drawString(45, y - 13, str(acc[0]))
                pdf.drawString(130, y - 13, str(acc[3]))
                
                dr_val = f"{float(acc[1]):.2f}" if acc[1] else "0.00"
                cr_val = f"{float(acc[2]):.2f}" if acc[2] else "0.00"
                bal_val = f"{float(acc[4]):.2f}" if acc[4] else "0.00"
                
                pdf.drawRightString(320, y - 13, dr_val)
                pdf.drawRightString(420, y - 13, cr_val)
                pdf.drawRightString(width - 45, y - 13, bal_val)
                
                pdf.line(40, y - 18, width - 40, y - 18)
                y -= 18
                si_acc += 1
        
        # Summary Box
        if y < 140:
            pdf.showPage()
            y = height - 100
            
        y -= 15
        pdf.setStrokeColor(colors.HexColor("#1A365D"))
        pdf.setFillColor(colors.HexColor("#F8FAFC"))
        pdf.rect(340, y - 75, width - 380, 70, fill=True, stroke=True)
        
        pdf.setFillColor(colors.HexColor("#2D3748"))
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(350, y - 20, "Total Treatment Cost:")
        pdf.drawRightString(width - 50, y - 20, f"INR {total_treatment_cost:.2f}")
        
        pdf.drawString(350, y - 38, "Total Paid (Credit):")
        pdf.drawRightString(width - 50, y - 38, f"INR {total_credit:.2f}")
        
        pdf.setFillColor(colors.HexColor("#E53E3E") if balance_due > 0 else colors.HexColor("#38A169"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(350, y - 58, "Balance Due:")
        pdf.drawRightString(width - 50, y - 58, f"INR {balance_due:.2f}")
        
        # Footer
        pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
        pdf.line(40, 110, width - 40, 110)
        
        pdf.setFillColor(colors.HexColor("#718096"))
        pdf.setFont("Helvetica-Oblique", 8)
        pdf.drawString(40, 95, "* This is a computer-generated document and does not require a physical signature.")
        pdf.drawString(40, 82, "* For any queries, please reach out to XE Dental Clinic / Dr. Anoop.")
        
        # Signature block
        pdf.setFillColor(colors.HexColor("#2D3748"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawRightString(width - 40, 95, "For Anupam Dental Clinic")
        pdf.setFont("Helvetica", 9)
        pdf.drawRightString(width - 40, 60, "Authorized Signatory")
        
        pdf.save()
        messagebox.showinfo("Success", f"Invoice PDF generated successfully!")
        
        try:
            os.startfile(output_path)
        except Exception as e:
            messagebox.showerror("Error Opening PDF", f"Could not open PDF automatically: {e}")


def get_db_connection(app=None):
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))
