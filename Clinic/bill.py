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
    
        # Main frame
        self.main_frame = tk.Frame(self.app.workspace)
        self.main_frame.pack(fill="both", expand=True)
        
        # ================ LEFT PANEL ================
        self.left_frame = tk.LabelFrame(self.main_frame, text="Treatments", font=("Arial", 12, "bold"), width=350)
        self.left_frame.pack(side="left", fill="y", padx=5, pady=5)

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

        # --- Details / Action Buttons ---
        self.detials = tk.LabelFrame(self.left_frame, text="Actions", font=("Arial", 10, "bold"))
        self.detials.pack(fill="both", expand=True, padx=5, pady=5)

        # Treatment type variable
        self.treatment_type_var = tk.StringVar(value="Teeth Based")

        def set_teeth_based():
            self.treatment_type_var.set("Teeth Based")
            btn_teeth.config(relief="sunken", bg="#C0EBE7")
            btn_general.config(relief="raised", bg="SystemButtonFace")

        def set_general():
            self.treatment_type_var.set("General")
            btn_general.config(relief="sunken", bg="#C0EBE7")
            btn_teeth.config(relief="raised", bg="SystemButtonFace")

        btn_teeth = tk.Button(self.detials, text="Teeth Based", font=("Arial", 12),
                              relief="sunken", bg="#C0EBE7", command=set_teeth_based)
        btn_teeth.grid(row=0, column=0, sticky="w", padx=2, pady=2)

        btn_general = tk.Button(self.detials, text="General", font=("Arial", 12),
                                command=set_general)
        btn_general.grid(row=0, column=1, sticky="w", padx=2, pady=2)

        btn_add = tk.Button(self.detials, text="Add to Treatment", font=("Arial", 11, "bold"),
                    bg="#4CAF50", fg="white", command=lambda: add_to_treatment())
        btn_add.grid(row=0, column=2, sticky="w", padx=2, pady=2)

        # Treatment selection
        tk.Label(self.detials, text="Tooth No:", font=("Arial", 10)).grid(row=1, column=0, padx=2, pady=2, sticky="e")
        self.bill_tooth_no = tk.Entry(self.detials, width=6)
        self.bill_tooth_no.grid(row=1, column=1, padx=2, pady=2, sticky="w")
        tk.Label(self.detials, text="Treatment:", font=("Arial", 10)).grid(row=1, column=2, padx=2, pady=2, sticky="e")
        self.bill_treatment_combo = ttk.Combobox(self.detials,
            values=["Scaling", "Filling", "RCT", "Extraction", "Crown", "Bridge",
                    "Implant", "Denture", "Cleaning", "X-Ray", "Consultation"],
            width=15)
        self.bill_treatment_combo.grid(row=1, column=3, padx=2, pady=2, sticky="w")

        tk.Label(self.detials, text="Amount:", font=("Arial", 10)).grid(row=2, column=0, padx=2, pady=2, sticky="e")
        self.bill_amount = tk.Entry(self.detials, width=10)
        self.bill_amount.grid(row=2, column=1, padx=2, pady=2, sticky="w")

        tk.Label(self.detials, text="Doctor:", font=("Arial", 10)).grid(row=2, column=2, padx=2, pady=2, sticky="e")
        self.bill_doctor_combo = ttk.Combobox(self.detials, values=["Dr. Anoop", "Dr. Terry"], width=12)
        self.bill_doctor_combo.grid(row=2, column=3, padx=2, pady=2, sticky="w")

        # Bill tree to show added treatments
        bill_columns = ("Tooth No", "Treatment", "Amount", "Doctor", "Type")
        bill_tree = ttk.Treeview(self.left_frame, columns=bill_columns, show="headings", height=8)
        # keep a reference so other methods can access current treatments
        self.bill_tree = bill_tree
        for col in bill_columns:
            bill_tree.heading(col, text=col)
            bill_tree.column(col, width=80)
        bill_tree.pack(fill="both", expand=True, padx=5, pady=(5, 10))

        bill_total_label = tk.Label(self.left_frame, text="Total: ₹0.00", font=("Arial", 12, "bold"), fg="green")
        bill_total_label.pack(padx=10, pady=(0, 10), anchor="e")

        # Action buttons placed under the bill tree (inside left_frame)
        action_bar = tk.Frame(self.left_frame)
        action_bar.pack(fill="x", padx=5, pady=(0, 10))

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
            ttype = self.treatment_type_var.get()
            if treatment or amount:
                bill_tree.insert("", "end", values=(tooth, treatment, amount, doctor, ttype))
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

        def show_prescription():
            pass

        def show_treatment_details():
            detail_win = tk.Toplevel(self.app.root)
            detail_win.title("Treatment Details")
            detail_win.geometry("600x400")
            detail_win.transient(self.app.root)

            tk.Label(detail_win, text="Treatment Details", font=("Arial", 14, "bold")).pack(pady=10)

            cols = ("Tooth No", "Treatment", "Amount", "Doctor", "Type")
            detail_tree = ttk.Treeview(detail_win, columns=cols, show="headings", height=12)
            for col in cols:
                detail_tree.heading(col, text=col)
                detail_tree.column(col, width=100)
            detail_tree.pack(fill="both", expand=True, padx=10, pady=5)

            # Copy items from bill_tree
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
                "email": self.bill_email.get()
            }
            self.treatments_list = []
            for child in bill_tree.get_children():
                self.treatments_list.append(bill_tree.item(child)["values"])
            d = Doctors(self.app)
            d.patient_data = self.patient_data
            d.treatments_list = self.treatments_list
            if hasattr(self, 'accounts_list'):
                d.accounts_list = self.accounts_list
            d.doctors_detials()

        btn_prescription = tk.Button(action_bar, text="Prescription", font=("Arial", 11),
                         command=self.prescription)
        btn_prescription.grid(row=0, column=3, sticky="w", padx=2, pady=2)

        btn_treatment = tk.Button(action_bar, text="Treatment Details", font=("Arial", 11),
                      command=show_treatment_details)
        btn_treatment.grid(row=0, column=4, sticky="w", padx=2, pady=2)

        btn_removing = tk.Button(action_bar, text="Remove", font=("Arial", 11),
                     fg="red", command=remove_treatment)
        btn_removing.grid(row=0, column=5, sticky="w", padx=2, pady=2)

        btn_close = tk.Button(action_bar, text="Close", font=("Arial", 11),
                  command=self.close)
        btn_close.grid(row=0, column=6, sticky="w", padx=2, pady=2)

        btn_bill_next = tk.Button(action_bar, text="Bill →", font=("Arial", 11, "bold"),
                     bg="#2196F3", fg="white", command=save_and_go_to_details)
        btn_bill_next.grid(row=0, column=7, sticky="w", padx=2, pady=2)

        # ================ CENTER PANEL (Bills) ================
        self.center_frame = tk.LabelFrame(self.main_frame, text="Bills", font=("Arial", 12, "bold"))
        self.center_frame.pack(side="left", fill="both", expand=True)

        # Teeth chart buttons
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_columnconfigure(1, weight=1)

        button_adult = tk.Button(self.center_frame, text="Adult", font=("Arial", 12),
                                 fg="black", command=self.adult_teeth)
        button_adult.grid(row=0, column=0, pady=5, padx=10, sticky="e")

        button_child = tk.Button(self.center_frame, text="Child", font=("Arial", 12),
                                 fg="black", command=self.child_teeth)
        button_child.grid(row=0, column=1, pady=5, padx=10, sticky="w")

        # ================ RIGHT PANEL (Commits) ================
        self.right_frame = tk.LabelFrame(self.main_frame, text="Commits", font=("Arial", 12, "bold"))
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        disease = tk.Label(self.right_frame, text="Disease:", font=("Arial", 12))
        disease.grid(row=0, column=0, sticky="w", padx=10, pady=2)
        self.disease_entry = tk.Entry(self.right_frame)
        self.disease_entry.grid(row=0, column=1, sticky="we", padx=10, pady=2)
        
        read = tk.Label(self.right_frame, text="Reading:", font=("Arial", 12))
        read.grid(row=0, column=2, sticky="w", padx=10, pady=2)
        
        self.reading_entry = tk.Entry(self.right_frame)
        self.reading_entry.grid(row=0, column=3, sticky="we", padx=10, pady=2)
        
        # Disease treeview
        dis_columns = ("Disease", "Date", "Reading")
        dis = ttk.Treeview(self.right_frame, column=dis_columns, show="headings", height=2)
        dis.heading("Disease", text="Disease")
        dis.heading("Date", text="Date")
        dis.heading("Reading", text="Reading")

        dis.column("Disease", width=100)
        dis.column("Date", width=50)
        dis.column("Reading", width=220)

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

        btn_frame = tk.Frame(self.right_frame)
        btn_frame.grid(row=0, column=4, padx=5, pady=2)
        tk.Button(btn_frame, text="Add", command=add_disease).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Delete", fg="red", command=delete_disease).pack(side="left", padx=2)

        dis.grid(row=1, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)

        # Comments section
        comments = tk.Label(self.right_frame, text="Comments", font=("Arial", 12, "bold"))
        comments.grid(row=2, column=0, sticky="w", padx=10, pady=2)

        scroll = tk.Scrollbar(self.right_frame)
        scroll.grid(row=3, column=5, sticky="ns")

        self.bill_notes = tk.Text(self.right_frame, height=6, yscrollcommand=scroll.set)
        self.bill_notes.grid(row=3, column=0, columnspan=5, sticky="nsew", padx=10, pady=5)

        scroll.config(command=self.bill_notes.yview)

        # Doctor's Notes section
        comments1 = tk.Label(self.right_frame, text="Doctor's Notes", font=("Arial", 12, "bold"))
        comments1.grid(row=4, column=0, sticky="w", padx=10, pady=2)

        scroll1 = tk.Scrollbar(self.right_frame)
        scroll1.grid(row=5, column=5, sticky="ns")

        self.bill_doctor_notes = tk.Text(self.right_frame, height=6, yscrollcommand=scroll1.set)
        self.bill_doctor_notes.grid(row=5, column=0, columnspan=5, sticky="nsew", padx=10, pady=5)

        scroll1.config(command=self.bill_doctor_notes.yview)

        # Show adult teeth by default
        self.adult_teeth()

    def adult_teeth(self):
        if hasattr(self, 'canvas') and self.canvas is not None:
            self.canvas.destroy()
        self.canvas = tk.Canvas(self.center_frame, width=300, height=580)
        self.canvas.grid(row=2, column=0, columnspan=2, pady=10)
        canvas = self.canvas
        canvas.create_text(145, 10, text="Adult", font=("Arial", 14, "bold"))

        right= tk.Label(self.center_frame,font=("Arial",12),text="Right",bg="#C0EBE7")
        right.grid(padx=40,pady=270)

        left = tk.Label(self.center_frame,font=("Arial",12),text="Left",bg="#C0EBE7")
        left.grid(padx=40,pady=270)
        # Tooth positions
        teeth = [
            # Upper Right
            (18,20,270),(17,20,230),(16,20,190),(15,20,150),
            (14,40,110),(13,70,90),(12,100,70),(11,130,50),

            # Upper Left
            (21,170,50),(22,200,70),(23,230,90),(24,260,110),
            (25,280,150),(26,280,190),(27,280,230),(28,280,270),

            # Lower Left
            (38,280,350),(37,280,390),(36,280,430),(35,280,470),
            (34,265,510),(33,235,535),(32,205,555),(31,170,560),

            # Lower Right
            (41,135,560),(42,100,555),(43,70,535),(44,40,510),
            (45,20,470),(46,20,430),(47,20,390),(48,20,350)
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

            # Number inside the circle
            canvas.create_text(
                x, y,
                text=str(tooth),
                font=("Arial", 8, "bold")
            )

            # Clickable area
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
        self.canvas = tk.Canvas(self.center_frame, width=300, height=580)
        self.canvas.grid(row=2, column=0, columnspan=2, pady=10)
        canvas = self.canvas
        canvas.create_text(145, 10, text="Child", font=("Arial", 14, "bold"))

        # Tooth positions
        teeth = [
            # Upper Right
            (55,40,300),(54,40,260),
            (53,50,225),(52,80,195),(51,110,175),

            # Upper Left
            (61,150,175),(62,180,195),(63,210,225),
            (64,220,260),(65,220,300),

            # Lower Left
            (75,235,380),(74,235,420),
            (73,210,455),(72,180,480),(71,150,500),

            # Lower Right
            (81,110,500),(82,80,480),(83,50,455),
            (84,40,420),(85,40,380)
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
                outline="black",
                width=2
            )

            # Number inside the circle
            canvas.create_text(
                x, y,
                text=str(tooth),
                font=("Arial", 8, "bold")
            )

            # Clickable area
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
        self.app.registration()

def get_db_connection(app=None):
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))