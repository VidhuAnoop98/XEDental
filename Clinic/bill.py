import tkinter as tk 
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import os
from doctors_d import Doctors
from prescription import Prescription

class Bill:
    def __init__(self,app):
        self.app = app
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

    def get_doctor_names_from_db(self):
        names = []
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT First_Name, Last_Name FROM Doctors ORDER BY First_Name, Last_Name")
            rows = cursor.fetchall()
            conn.close()

            for first, last in rows:
                fname = (first or "").strip()
                lname = (last or "").strip()
                full_name = f"{fname} {lname}".strip()
                if not full_name:
                    continue
                if not full_name.lower().startswith("dr.") and not full_name.lower().startswith("dr "):
                    full_name = f"Dr. {full_name}"
                if full_name not in names:
                    names.append(full_name)
        except Exception:
            pass
        return names


    def get_treatments_and_fees(self):
        default_fees = {
            "Cleaning": 500.0,
            "Consultation": 200.0,
            "Crown": 4500.0,
            "Denture": 12000.0,
            "Extraction": 1000.0,
            "Filling": 750.0,
            "Implant": 25000.0,
            "RCT": 3500.0,
            "Scaling": 600.0,
            "X-Ray": 300.0,
        }
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT Treatment, Rate, Amount FROM Treatment_Fees ORDER BY Treatment")
            rows = cursor.fetchall()
            conn.close()

            if rows:
                fee_map = {}
                for treatment, rate, amount in rows:
                    if treatment:
                        fee_map[treatment] = amount if (amount is not None and amount > 0) else (rate if rate is not None else 0.0)
                return fee_map if fee_map else default_fees
            return default_fees
        except Exception:
            return default_fees

    def bill(self):
        # Initialize patient_data if not already present
        if not hasattr(self, 'patient_data'):
            self.patient_data = {
                "patientid": "",
                "regno": "",
                "patientname": "",
                "address1": "",
                "address2": "",
                "age": "",
                "gender": "",
                "office": "",
                "residence": "",
                "email": ""
            }
            if hasattr(self, 'entry_name'):
                self.patient_data["patientname"] = self.entry_name.get()
                self.patient_data["age"] = self.entry_age.get()
                self.patient_data["gender"] = self.gender_combo.get()
                self.patient_data["email"] = self.entry_email.get()
                self.patient_data["address1"] = self.entry_address1.get()
                self.patient_data["address2"] = self.entry_address2.get()
                self.patient_data["office"] = self.entry_mobile1.get()
                self.patient_data["residence"] = self.entry_mobile2.get()
            
            # Query sequential ID
            if not self.patient_data["patientid"]:
                try:
                    conn = get_db_connection(self.app)
                    cursor = conn.cursor()
                    cursor.execute("SELECT MAX(id) FROM Appointments")
                    last_id = cursor.fetchone()[0]
                    conn.close()
                    self.patient_data["patientid"] = str(last_id if last_id else 1)
                    self.patient_data["regno"] = f"REG-{last_id if last_id else 1:04d}"
                except Exception:
                    self.patient_data["patientid"] = "1"
                    self.patient_data["regno"] = "REG-0001"

        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        # ================ MAIN CONTENT FRAME ================
        self.main_frame = tk.Frame(self.app.workspace)
        self.main_frame.pack(fill="both", expand=True)
        
        # ================ LEFT PANEL ================
        self.left_frame = tk.LabelFrame(self.main_frame, text="Treatments", font=("Arial", 12, "bold"), width=350)
        self.left_frame.pack(side="left", fill="both", expand=False, padx=5, pady=5)

        # ================ CENTER PANEL (Bills, Comments & Action Bar) ================
        self.center_frame = tk.LabelFrame(self.main_frame, text="Bills", font=("Arial", 12, "bold"))
        self.center_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Action bar at bottom of center panel only
        action_bar = tk.Frame(self.center_frame, bd=1, relief="groove")
        action_bar.pack(side="bottom", fill="x", padx=5, pady=5)

        # --- Patient Details ---
        self.patient = tk.LabelFrame(self.left_frame, text="Patient Details", font=("Arial", 10, "bold"), width=330, height=330)
        self.patient.pack(padx=5, pady=5)
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

        # Populate patient details fields
        if self.patient_data["patientid"]:
            self.bill_patientid.insert(0, self.patient_data["patientid"])
        if self.patient_data["regno"]:
            self.bill_regno.insert(0, self.patient_data["regno"])
        if self.patient_data["patientname"]:
            self.bill_patientname.insert(0, self.patient_data["patientname"])
        if self.patient_data["address1"]:
            self.bill_address1.insert(0, self.patient_data["address1"])
        if self.patient_data["address2"]:
            self.bill_address2.insert(0, self.patient_data["address2"])
        if self.patient_data["age"]:
            self.bill_age.insert(0, self.patient_data["age"])
        if self.patient_data["gender"]:
            self.bill_gender.set(self.patient_data["gender"])
        if self.patient_data["office"]:
            self.bill_office.insert(0, self.patient_data["office"])
        if self.patient_data["residence"]:
            self.bill_residence.insert(0, self.patient_data["residence"])
        if self.patient_data["email"]:
            self.bill_email.insert(0, self.patient_data["email"])

        # If registration form inputs exist, prefer those values to populate patient details
        if hasattr(self, 'entry_name'):
            try:
                name = self.entry_name.get().strip()
                if name:
                    self.bill_patientname.delete(0, 'end')
                    self.bill_patientname.insert(0, name)

                age = self.entry_age.get().strip()
                if age:
                    self.bill_age.delete(0, 'end')
                    self.bill_age.insert(0, age)

                gender = self.gender_var.get().strip() if hasattr(self, 'gender_var') else ''
                if gender:
                    self.bill_gender.set(gender)

                addr1 = self.entry_address1.get().strip()
                if addr1:
                    self.bill_address1.delete(0, 'end')
                    self.bill_address1.insert(0, addr1)

                addr2 = self.entry_address2.get().strip()
                if addr2:
                    self.bill_address2.delete(0, 'end')
                    self.bill_address2.insert(0, addr2)

                mob1 = self.entry_mobile1.get().strip()
                if mob1:
                    self.bill_office.delete(0, 'end')
                    self.bill_office.insert(0, mob1)

                mob2 = self.entry_mobile2.get().strip()
                if mob2:
                    self.bill_residence.delete(0, 'end')
                    self.bill_residence.insert(0, mob2)

                email = self.entry_email.get().strip()
                if email:
                    self.bill_email.delete(0, 'end')
                    self.bill_email.insert(0, email)
            except Exception:
                pass

        # Search bind on Return key
        def search_patient(event=None):
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
            else:
                messagebox.showinfo("Not Found", "No patient record found.")
            conn.close()

        self.bill_patientid.bind("<Return>", search_patient)
        self.bill_regno.bind("<Return>", search_patient)

        # --- Disease / Commits Section (placed below Patient Details) ---
        self.disease_frame = tk.LabelFrame(self.left_frame, text="Disease", font=("Arial", 10, "bold"))
        self.disease_frame.pack(fill="x", padx=5, pady=5)

        disease_lbl = tk.Label(self.disease_frame, text="Disease:", font=("Arial", 9))
        disease_lbl.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.disease_entry = tk.Entry(self.disease_frame, width=10)
        self.disease_entry.grid(row=0, column=1, sticky="w", padx=2, pady=2)

        read_lbl = tk.Label(self.disease_frame, text="Reading:", font=("Arial", 9))
        read_lbl.grid(row=0, column=2, sticky="w", padx=2, pady=2)
        self.reading_entry = tk.Entry(self.disease_frame, width=10)
        self.reading_entry.grid(row=0, column=3, sticky="w", padx=2, pady=2)

        def add_disease():
            d = self.disease_entry.get()
            r = self.reading_entry.get()
            if d or r:
                current_date = datetime.now().strftime("%d-%m-%Y")
                dis.insert("", "end", values=(d, current_date, r))
                self.disease_entry.delete(0, 'end')
                self.reading_entry.delete(0, 'end')

        def delete_disease():
            selected = dis.selection()
            if selected:
                for item in selected:
                    dis.delete(item)
            else:
                messagebox.showwarning("No Selection", "Please select a disease row to delete.")

        btn_disease_frame = tk.Frame(self.disease_frame)
        btn_disease_frame.grid(row=0, column=4, padx=2, pady=2)
        tk.Button(btn_disease_frame, text="Add", font=("Arial", 8), command=add_disease).pack(side="left", padx=1)
        tk.Button(btn_disease_frame, text="Delete", font=("Arial", 8), fg="red", command=delete_disease).pack(side="left", padx=1)

        dis_columns = ("Disease", "Date", "Reading")
        dis = ttk.Treeview(self.disease_frame, columns=dis_columns, show="headings", height=2)
        dis.heading("Disease", text="Disease")
        dis.heading("Date", text="Date")
        dis.heading("Reading", text="Reading")

        dis.column("Disease", width=80)
        dis.column("Date", width=70)
        dis.column("Reading", width=110)

        dis.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=2, pady=2)

        # --- Details / Action Buttons ---
        self.detials = tk.LabelFrame(self.left_frame, text="Actions", font=("Arial", 10, "bold"))
        self.detials.pack(fill="both", padx=5, pady=5)

        # Treatment type variable
        self.treatment_type_var = tk.StringVar(value="Teeth Based")

        btn_add = tk.Button(self.detials, text="Add to Treatment", font=("Arial", 11, "bold"),
                    bg="#4CAF50", fg="white", command=lambda: add_to_treatment())
        btn_add.grid(row=0, column=2, sticky="w", padx=2, pady=2)

        # Treatment selection
        tk.Label(self.detials, text="Tooth No:", font=("Arial", 10)).grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.bill_tooth_no = tk.Entry(self.detials, width=6)
        self.bill_tooth_no.grid(row=1, column=1, padx=2, pady=2, sticky="w")
        tk.Label(self.detials, text="Treatment:", font=("Arial", 10)).grid(row=1, column=2, padx=2, pady=2, sticky="e")
        
        self.fee_map = self.get_treatments_and_fees()
        treatment_list = list(self.fee_map.keys())

        self.bill_treatment_combo = ttk.Combobox(self.detials,
            values=treatment_list,
            width=15)
        self.bill_treatment_combo.grid(row=1, column=3, padx=2, pady=2, sticky="w")

        tk.Label(self.detials, text="Amount:", font=("Arial", 10)).grid(row=2, column=0, padx=2, pady=2, sticky="e")
        self.bill_amount = tk.Entry(self.detials, width=10)
        self.bill_amount.grid(row=2, column=1, padx=2, pady=2, sticky="w")

        def on_treatment_selected(event=None):
            selected_treatment = self.bill_treatment_combo.get().strip()
            if selected_treatment in self.fee_map:
                amount_val = self.fee_map[selected_treatment]
                self.bill_amount.delete(0, 'end')
                amount_str = f"{amount_val:.2f}".rstrip('0').rstrip('.') if amount_val % 1 == 0 else f"{amount_val:.2f}"
                self.bill_amount.insert(0, amount_str)

        self.bill_treatment_combo.bind("<<ComboboxSelected>>", on_treatment_selected)
        self.bill_treatment_combo.bind("<FocusOut>", on_treatment_selected)

        tk.Label(self.detials, text="Doctor:", font=("Arial", 10)).grid(row=2, column=2, padx=2, pady=2, sticky="e")
        doctor_names = self.get_doctor_names_from_db()

        def refresh_bill_doctors():
            latest = self.get_doctor_names_from_db()
            self.bill_doctor_combo['values'] = latest
            if latest and not self.bill_doctor_combo.get():
                self.bill_doctor_combo.set(latest[0])

        self.bill_doctor_combo = ttk.Combobox(self.detials, values=doctor_names, width=12, postcommand=refresh_bill_doctors)
        if doctor_names:
            self.bill_doctor_combo.set(doctor_names[0])
        self.bill_doctor_combo.grid(row=2, column=3, padx=2, pady=2, sticky="w")

        # Bill tree to show added treatments
        bill_columns = ("Tooth No", "Treatment", "Amount", "Doctor")
        bill_tree = ttk.Treeview(self.left_frame, columns=bill_columns, show="headings", height=7)
        self.bill_tree = bill_tree
        for col in bill_columns:
            bill_tree.heading(col, text=col)
            bill_tree.column(col, width=40)
        bill_tree.pack(fill="both", padx=5, pady=(5, 10))

        bill_total_label = tk.Label(self.left_frame, text="Total: ₹0.00", font=("Arial", 12, "bold"), fg="green")
        bill_total_label.pack(padx=10, pady=(0, 10), anchor="e")

        def update_bill_total():
            total = 0.0
            for child in bill_tree.get_children():
                try:
                    total += float(bill_tree.item(child)["values"][2])
                except (ValueError, IndexError, TypeError):
                    pass
            bill_total_label.config(text=f"Total: ₹{total:.2f}")

        def add_to_treatment():
            treatment = self.bill_treatment_combo.get()
            tooth = self.bill_tooth_no.get()
            amount = self.bill_amount.get()
            doctor = self.bill_doctor_combo.get()
            if treatment or amount:
                bill_tree.insert("", "end", values=(tooth, treatment, amount, doctor))
                self.bill_treatment_combo.set('')
                self.bill_tooth_no.delete(0, 'end')
                self.bill_amount.delete(0, 'end')
                self.bill_doctor_combo.set('')
                update_bill_total()

        def remove_treatment():
            selected = bill_tree.selection()
            if selected:
                for item in selected:
                    bill_tree.delete(item)
                update_bill_total()
            else:
                messagebox.showwarning("No Selection", "Please select a treatment to remove.")

        def show_treatment_details():
            detail_win = tk.Toplevel(self.app.root)
            detail_win.title("Treatment Details")
            detail_win.geometry("600x400")
            detail_win.transient(self.app.root)

            tk.Label(detail_win, text="Treatment Details", font=("Arial", 14, "bold")).pack(pady=10)

            cols = ("Tooth No", "Treatment", "Amount", "Doctor")
            detail_tree = ttk.Treeview(detail_win, columns=cols, show="headings", height=12)
            for col in cols:
                detail_tree.heading(col, text=col)
                detail_tree.column(col, width=40)
            detail_tree.pack(fill="both", expand=True, padx=10, pady=5)

            for child in bill_tree.get_children():
                values = bill_tree.item(child)["values"]
                detail_tree.insert("", "end", values=values)

            tk.Button(detail_win, text="Close", font=("Arial", 11),
                      command=detail_win.destroy).pack(pady=10)

        # Restore treatments if any
        if not hasattr(self, 'treatments_list'):
            self.treatments_list = []
        else:
            for item in self.treatments_list:
                bill_tree.insert("", "end", values=item)
            update_bill_total()

        def save_and_go_to_details():
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
                "email": self.bill_email.get(),
                "comments": self.bill_notes.get("1.0", "end-1c") if hasattr(self, 'bill_notes') else ""
            }
            self.treatments_list = []
            for child in bill_tree.get_children():
                raw_values = bill_tree.item(child)["values"]
                tooth = str(raw_values[0]) if len(raw_values) > 0 else ""
                treatment = str(raw_values[1]) if len(raw_values) > 1 else ""
                amount = str(raw_values[2]) if len(raw_values) > 2 else "0.00"
                doctor = str(raw_values[3]) if len(raw_values) > 3 else ""
                self.treatments_list.append((tooth, treatment, amount, "", doctor))
            d = Doctors(self.app)
            d.patient_data = self.patient_data
            d.treatments_list = self.treatments_list
            if hasattr(self, 'accounts_list'):
                d.accounts_list = self.accounts_list
            d.doctors_detials()

        # Action bar buttons
        btn_prescription = tk.Button(action_bar, text="Prescription", font=("Arial", 11),
                         command=self.prescription)
        btn_prescription.pack(side="left", padx=5, pady=5)

        btn_treatment = tk.Button(action_bar, text="Treatment Details", font=("Arial", 11),
                      command=show_treatment_details)
        btn_treatment.pack(side="left", padx=5, pady=5)

        btn_removing = tk.Button(action_bar, text="Remove", font=("Arial", 11),
                     fg="red", command=remove_treatment)
        btn_removing.pack(side="left", padx=5, pady=5)

        btn_bill_next = tk.Button(action_bar, text="Bill →", font=("Arial", 11, "bold"),
                     bg="#2196F3", fg="white", command=save_and_go_to_details)
        btn_bill_next.pack(side="right", padx=5, pady=5)

        btn_close = tk.Button(action_bar, text="Close", font=("Arial", 11),
                  command=self.close)
        btn_close.pack(side="right", padx=5, pady=5)

        # Teeth chart buttons (top of center frame)
        teeth_btn_frame = tk.Frame(self.center_frame)
        teeth_btn_frame.pack(side="top", pady=5)

        button_adult = tk.Button(teeth_btn_frame, text="Adult", font=("Arial", 11, "bold"),
                                 fg="black", command=self.adult_teeth)
        button_adult.pack(side="left", padx=10)

        button_child = tk.Button(teeth_btn_frame, text="Child", font=("Arial", 11, "bold"),
                                 fg="black", command=self.child_teeth)
        button_child.pack(side="left", padx=10)

        # Teeth chart canvas container (middle of center frame)
        self.teeth_container = tk.Frame(self.center_frame)
        self.teeth_container.pack(side="top", fill="both", expand=True, pady=5)

        # Comments section (above action bar in center frame)
        comments_frame = tk.LabelFrame(self.center_frame, text="Comments", font=("Arial", 11, "bold"))
        comments_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=5)

        scroll = tk.Scrollbar(comments_frame)
        scroll.pack(side="right", fill="y")

        self.bill_notes = tk.Text(comments_frame, height=5, font=("Arial", 10), yscrollcommand=scroll.set)
        self.bill_notes.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scroll.config(command=self.bill_notes.yview)

        # Show adult teeth by default
        self.adult_teeth()

    def adult_teeth(self):
        if hasattr(self, 'canvas') and self.canvas is not None:
            self.canvas.destroy()

        self.canvas = tk.Canvas(self.teeth_container, width=850, height=320)
        self.canvas.pack(fill="both", expand=True, pady=2)
        canvas = self.canvas
        canvas.create_text(500, 15, text="Adult Teeth Chart", font=("Arial", 13, "bold"))

        canvas.create_text(200, 160, text="Right", font=("Arial", 12, "bold"), fill="#008080")
        canvas.create_text(800, 160, text="Left", font=("Arial", 12, "bold"), fill="#008080")

        teeth = [
            # Upper Right
            (18,200,120),(17,240,110),(16,280,100),(15,320,90),
            (14,360,80),(13,400,70),(12,440,60),(11,480,50), 

            # Upper Left
            (21,520,50),(22,560,60),(23,600,70),(24,640,80),
            (25,680,90),(26,720,100),(27,760,110),(28,800,120),

            # Lower Left
            (38,800,200),(37,760,210),(36,720,220),(35,680,230),
            (34,640,240),(33,600,250),(32,560,260),(31,520,270),

            # Lower Right
            (41,480,270),(42,440,260),(43,400,250),(44,360,240),
            (45,320,230),(46,280,220),(47,240,210),(48,200,200)
        ]

        r = 15

        def tooth_click(number):
            current = self.bill_tooth_no.get()
            if current:
                self.bill_tooth_no.delete(0, 'end')
                self.bill_tooth_no.insert(0, f"{current},{number}")
            else:
                self.bill_tooth_no.insert(0, str(number))

        for tooth, x, y in teeth:
            canvas.create_oval(
                x-r, y-r, x+r, y+r,
                fill="white",
                outline="black",
                width=2
            )

            canvas.create_text(
                x, y,
                text=str(tooth),
                font=("Arial", 8, "bold")
            )

            canvas.tag_bind(
                canvas.create_oval(
                    x-r, y-r, x+r, y+r,
                    outline="",
                    fill=""
                ),
                "<Button-1>",
                lambda e, n=tooth: tooth_click(n)
            )

    def child_teeth(self): 
        if hasattr(self, 'canvas') and self.canvas is not None:
            self.canvas.destroy()

        self.canvas = tk.Canvas(self.teeth_container, width=850, height=320)
        self.canvas.pack(fill="both", expand=True, pady=2)
        canvas = self.canvas
        canvas.create_text(500, 15, text="Child Teeth Chart", font=("Arial", 13, "bold"))

        canvas.create_text(300, 160, text="Right", font=("Arial", 12, "bold"), fill="#008080")
        canvas.create_text(700, 160, text="Left", font=("Arial", 12, "bold"), fill="#008080")

        teeth = [
            # Upper Right
            (55,320,90),(54,360,80),
            (53,400,70),(52,440,60),(51,480,50),

            # Upper Left
            (61,520,50),(62,560,60),(63,600,70),
            (64,640,80),(65,680,90),

            # Lower Left
            (75,680,230),(74,640,240),
            (73,600,250),(72,560,260),(71,520,270),

            # Lower Right
            (81,480,270),(82,440,260),(83,400,250),
            (84,360,240),(85,320,230)
        ]

        r = 15

        def tooth_click(number):
            current = self.bill_tooth_no.get()
            if current:
                self.bill_tooth_no.delete(0, 'end')
                self.bill_tooth_no.insert(0, f"{current},{number}")
            else:
                self.bill_tooth_no.insert(0, str(number))

        for tooth, x, y in teeth:
            canvas.create_oval(
                x-r, y-r, x+r, y+r,
                fill="white",
                outline="black",
                width=2
            )

            canvas.create_text(
                x, y,
                text=str(tooth),
                font=("Arial", 8, "bold")
            )

            canvas.tag_bind(
                canvas.create_oval(
                    x-r, y-r, x+r, y+r,
                    outline="",
                    fill=""
                ),
                "<Button-1>",
                lambda e, n=tooth: tooth_click(n)
            )

    def prescription(self):
        p = Prescription(self.app)
        p.patient_data = self.patient_data
        p.prescription()

    def close(self):
        from registration import Registration
        r = Registration(self.app)
        r.registration_workspace()

def get_db_connection(app=None):
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))