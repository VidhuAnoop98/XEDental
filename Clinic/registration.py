import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime 
import sqlite3
import os
from bill import Bill
from doctors_d import Doctors
from letter_paper import Letter
from card import Card
from lab import Lab

def get_db_connection(app=None):
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))

def init_db(app=None):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Patient_Name TEXT NOT NULL,
            Age TEXT,
            Gender TEXT,
            Contact TEXT,
            Address1 TEXT,
            Address2 TEXT,
            Mobile_Number1 TEXT,
            Mobile_Number2 TEXT,
            Date TEXT,
            Time TEXT,
            Email_id TEXT,
            Notes TEXT,
            Doctor_Name TEXT
        )
    ''')
    try:
        cursor.execute("PRAGMA table_info(Appointments)")
        cols = [c[1] for c in cursor.fetchall()]
        if "Doctor_Name" not in cols:
            cursor.execute("ALTER TABLE Appointments ADD COLUMN Doctor_Name TEXT")
    except Exception:
        pass
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Patient_ID TEXT,
            Reg_No TEXT,
            Patient_Name TEXT,
            Date TEXT,
            Total_Amount REAL,
            Balance_Due REAL,
            Comments TEXT,
            Doctor_Notes TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bill_Treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Bill_ID INTEGER,
            Tooth_No TEXT,
            Treatment TEXT,
            Amount REAL,
            Doctor TEXT,
            Type TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bill_Accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Bill_ID INTEGER,
            Date TEXT,
            Debit REAL,
            Credit REAL,
            Particulars TEXT,
            Balance REAL
        )
    ''')
    conn.commit()
    conn.close()

class Registration:
    def __init__(self, app):
        self.app = app
        init_db(app)
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        buttons = [
            ("Appointments", self.registration_workspace),
            ("Preview Today's Appointments", self.todayapp),
            ("Lab Work",self.lab),
        ]
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(app.workspace, text=text, font=('Arial', 11), width=22, command=command)
            btn.place(x=40, y=280 + i * 45)


    def todayapp(self):
        Letter(self.app, mode="form")

    def lab(self):
        Lab(self.app)
        
    def registration_workspace(self):
        # Initialize patient_data dictionary
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

        self.only_four_digits = tk.BooleanVar(value=False)

        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        content_frame = tk.Frame(self.app.workspace)
        content_frame.pack(pady=10, fill="both", expand=True)

        left_frame = tk.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)
        middle_frame = tk.Frame(content_frame)
        middle_frame.pack(side="left", fill="both", expand=True, padx=5)
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=5)

        reg=tk.Frame(left_frame)
        reg.pack(fill="both", expand=True,pady=5)

        # --- Row 0: Doctor selection ---
        Doctor_name = tk.Label(reg, text="Doctor Name:", font=('Arial', 8))
        Doctor_name.grid(row=0, column=0, padx=(20, 5), pady=10, sticky='e')
        self.Doctor_var = tk.StringVar()
        doctor_names = get_doctor_names_from_db(self.app)
        self.Doctor_combo = ttk.Combobox(reg, textvariable=self.Doctor_var, values=doctor_names, state="readonly", font=('Arial', 8), width=15)
        if doctor_names:
            self.Doctor_combo.set(doctor_names[0])
        self.Doctor_combo.grid(row=0, column=1, padx=(0, 20), pady=10, sticky='w')

        def on_doctor_combo_select(event=None):
            selected_doc = self.Doctor_var.get()
            if hasattr(self, 'patient_tree') and self.patient_tree:
                selected_item = self.patient_tree.focus()
                if selected_item:
                    current_vals = list(self.patient_tree.item(selected_item)["values"])
                    if len(current_vals) >= 5:
                        current_vals[4] = selected_doc
                        self.patient_tree.item(selected_item, values=tuple(current_vals))

        self.Doctor_combo.bind("<<ComboboxSelected>>", on_doctor_combo_select)

        # --- Row 1: Patient Details ---
        Patient_Name = tk.Label(reg, text="Patient Name:", font=('Arial',8))
        Patient_Name.grid(row=0, column=2, padx=(20, 5), pady=10, sticky='e')
        self.entry_name = tk.Entry(reg, font=('Arial', 8), width=18)
        self.entry_name.grid(row=0, column=3, padx=(0, 20), pady=10, sticky='w')

        Age = tk.Label(reg, text="Age:", font=('Arial', 8))
        Age.grid(row=0, column=4, padx=(10, 5), pady=10, sticky='e')
        self.entry_age = tk.Entry(reg, font=('Arial', 8), width=4)
        self.entry_age.grid(row=0, column=5, padx=(0, 20), pady=10, sticky='w')

        tk.Label(reg, text="Gender:", font=('Arial', 8)).grid(row=1, column=0, padx=(10, 5), pady=10, sticky='e')
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(reg, textvariable=self.gender_var, values=["Male", "Female"], state="readonly", width=8)
        self.gender_combo.grid(row=1, column=1, padx=(0, 10), pady=10, sticky='w')

        tk.Label(reg, text="Email ID:", font=('Arial', 8)).grid(row=1, column=2, padx=(10, 5), pady=10, sticky='e')
        self.entry_email = tk.Entry(reg, font=('Arial', 8), width=18)
        self.entry_email.grid(row=1, column=3, padx=(0, 20), pady=10, sticky='w')

        tk.Label(reg, text="Date:", font=('Arial', 8)).grid(row=1, column=4, padx=(10, 5), pady=10, sticky='e')
        date_str = datetime.now().strftime("%d-%m-%Y")
        self.entry_date = tk.Entry(reg, font=('Arial', 8), width=10)
        self.entry_date.insert(0, date_str)
        self.entry_date.grid(row=1, column=5, padx=(0, 20), pady=10, sticky='w')

        tk.Label(reg, text="Time:", font=('Arial', 8)).grid(row=2, column=0, padx=(10, 5), pady=10, sticky='e')
        time_str = datetime.now().strftime("%I:%M %p")
        self.entry_time = tk.Entry(reg, font=('Arial', 8), width=8)
        self.entry_time.insert(0, time_str)
        self.entry_time.grid(row=2, column=1, padx=(0, 20), pady=10, sticky='w')

        # --- Row 2: Address & Mobiles ---
        tk.Label(reg, text="Address1:", font=('Arial', 8)).grid(row=2, column=2, padx=(20, 5), pady=10, sticky='e')
        self.entry_address1 = tk.Entry(reg, font=('Arial', 8), width=18)
        self.entry_address1.grid(row=2, column=3, padx=(0, 20), pady=10, sticky='w')

        tk.Label(reg, text="Address2:", font=('Arial', 8)).grid(row=2, column=4, padx=(10, 5), pady=10, sticky='e')
        self.entry_address2 = tk.Entry(reg, font=('Arial', 8), width=18)
        self.entry_address2.grid(row=2, column=5, padx=(0, 20), pady=10, sticky='w')

        tk.Label(reg, text="Mobile Number 1:", font=('Arial', 8)).grid(row=3, column=0, padx=(10, 5), pady=10, sticky='e')
        self.entry_mobile1 = tk.Entry(reg, font=('Arial', 8), width=15)
        self.entry_mobile1.grid(row=3, column=1, padx=(0, 20), pady=10, sticky='w')

        tk.Label(reg, text="Mobile Number 2:", font=('Arial', 8)).grid(row=3, column=2, padx=(10, 5), pady=10, sticky='e')
        self.entry_mobile2 = tk.Entry(reg, font=('Arial', 8), width=15)
        self.entry_mobile2.grid(row=3, column=3, padx=(0, 20), pady=10, sticky='w')


        pat = tk.Frame(middle_frame)
        pat.pack(fill="both", expand=True,pady=5)
        # Row 0: Patient ID & Reg No
        self.bill_patientid = tk.Entry(pat, justify="center", width=12)
        self.bill_patientid.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.bill_regno = tk.Entry(pat, justify="center", width=12)
        self.bill_regno.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # Row 1: Patient Name & Address 1
        self.bill_patientname = tk.Entry(pat, justify="center", width=18)
        self.bill_patientname.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        self.bill_address1 = tk.Entry(pat, justify="center", width=18)
        self.bill_address1.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # Row 2: Address 2
        self.bill_address2 = tk.Entry(pat, width=38)
        self.bill_address2.grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="we")

        # Row 3: Age & Sex
        tk.Label(pat, text="Age:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.bill_age = tk.Entry(pat, width=6)
        self.bill_age.grid(row=4, column=0, sticky="w", padx=5, pady=2)

        tk.Label(pat, text="Sex:", font=("Arial", 10, "bold")).grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.bill_gender = ttk.Combobox(pat, values=["Male", "Female"], state="readonly", width=10)
        self.bill_gender.grid(row=4, column=1, sticky="w", padx=5, pady=2)

        # Row 4: Phone Numbers (Office & Residence)
        self.bill_office = tk.Entry(pat, width=18)
        self.bill_office.grid(row=5, column=0, padx=5, pady=2, sticky="w")

        self.bill_residence = tk.Entry(pat, width=18)
        self.bill_residence.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        # Row 5: Email
        self.bill_email = tk.Entry(pat, width=38)
        self.bill_email.grid(row=6, column=0, columnspan=2, padx=5, pady=2, sticky="we")

        # --- Search bind on Return key ---
        def search_patient_details(event=None):
            pid = self.bill_patientid.get().strip()
            reg = self.bill_regno.get().strip()
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            row = None
            if pid:
                pid_val = self.parse_patient_id(pid)
                if pid_val:
                    cursor.execute("SELECT * FROM Appointments WHERE id=?", (pid_val,))
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
                self.bill_patientid.insert(0, self.format_patient_id(str(row[0])))
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
                
                # --- Populate Left Frame (reg) ---
                self.entry_name.delete(0, 'end')
                self.entry_name.insert(0, row[1] if row[1] else "")
                
                self.entry_age.delete(0, 'end')
                self.entry_age.insert(0, row[2] if row[2] else "")
                
                self.gender_var.set(row[3] if row[3] else "")
                
                self.entry_address1.delete(0, 'end')
                self.entry_address1.insert(0, row[5] if row[5] else "")
                
                self.entry_address2.delete(0, 'end')
                self.entry_address2.insert(0, row[6] if row[6] else "")
                
                self.entry_mobile1.delete(0, 'end')
                self.entry_mobile1.insert(0, row[7] if row[7] else "")
                
                self.entry_mobile2.delete(0, 'end')
                self.entry_mobile2.insert(0, row[8] if row[8] else "")
                
                self.entry_email.delete(0, 'end')
                self.entry_email.insert(0, row[11] if row[11] else "")
                
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
                treatment_val, doc_val = get_patient_latest_treatment(self.app, row[0])
                if doc_val:
                    self.Doctor_var.set(doc_val)
                elif len(row) > 13 and row[13]:
                    self.Doctor_var.set(row[13])
                self.load_patient_accounts(row[0])
                self.load_patient_treatments(row[0])
            else:
                messagebox.showinfo("Not Found", "No patient record found.")
            conn.close()

        self.bill_patientid.bind("<Return>", search_patient_details)
        self.bill_patientid.bind("<FocusOut>", search_patient_details)
        self.bill_regno.bind("<Return>", search_patient_details)

        # --- Save Function ---
        def save():
            selected_doc = self.Doctor_var.get().strip()
            appointments(
                self.app,
                self.entry_name.get(),
                self.entry_age.get(),
                self.gender_var.get(),
                self.entry_mobile1.get(),
                self.entry_address1.get(),
                self.entry_address2.get(),
                self.entry_mobile1.get(),
                self.entry_mobile2.get(),
                self.entry_date.get(),
                self.entry_time.get(),
                self.entry_email.get(),
                self.entry_notes.get("1.0", "end-1c"),
                selected_doc
            )
            
            # Retrieve last insert ID to populate patient_data
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(id) FROM Appointments")
                last_id = cursor.fetchone()[0]
                conn.close()
                pid_str = str(last_id) if last_id else "1"
                reg_str = f"REG-{last_id:04d}" if last_id else "REG-0001"
            except Exception:
                pid_str = "1"
                reg_str = "REG-0001"

            # Store entered patient details
            self.patient_data = {
                "patientid": pid_str,
                "regno": reg_str,
                "patientname": self.entry_name.get().strip(),
                "address1": self.entry_address1.get().strip(),
                "address2": self.entry_address2.get().strip(),
                "age": self.entry_age.get().strip(),
                "gender": self.gender_var.get().strip(),
                "office": self.entry_mobile1.get().strip(),
                "residence": self.entry_mobile2.get().strip(),
                "email": self.entry_email.get().strip()
            }
            
            # Pre-populate billing entry boxes
            self.bill_patientid.delete(0, 'end')
            self.bill_patientid.insert(0, self.format_patient_id(self.patient_data["patientid"]))
            self.bill_regno.delete(0, 'end')
            self.bill_regno.insert(0, self.patient_data["regno"])
            self.bill_patientname.delete(0, 'end')
            self.bill_patientname.insert(0, self.patient_data["patientname"])
            self.bill_address1.delete(0, 'end')
            self.bill_address1.insert(0, self.patient_data["address1"])
            self.bill_address2.delete(0, 'end')
            self.bill_address2.insert(0, self.patient_data["address2"])
            self.bill_age.delete(0, 'end')
            self.bill_age.insert(0, self.patient_data["age"])
            self.bill_gender.set(self.patient_data["gender"])
            self.bill_office.delete(0, 'end')
            self.bill_office.insert(0, self.patient_data["office"])
            self.bill_residence.delete(0, 'end')
            self.bill_residence.insert(0, self.patient_data["residence"])
            self.bill_email.delete(0, 'end')
            self.bill_email.insert(0, self.patient_data["email"])

            # Refresh patient tree (only today's appointments)
            for child in patient_tree.get_children():
                patient_tree.delete(child)
            for row in get_all_appointments(self.app):
                app_date = row[9] if len(row) > 9 and row[9] else ""
                if app_date and not is_today_date(app_date):
                    continue
                treatment, doc = get_patient_latest_treatment(self.app, row[0])
                if not doc and len(row) > 13 and row[13]:
                    doc = row[13]
                if not doc:
                    doc = selected_doc
                patient_tree.insert("", "end", values=(row[0], row[1], row[5], treatment, doc))

            # Refresh history tree
            for child in history_tree.get_children():
                history_tree.delete(child)
            for row in get_all_appointments(self.app):
                history_tree.insert("", "end", values=(row[0], row[1], row[5]))

            messagebox.showinfo("Success", "Appointment saved successfully!")
            # Open bill view
            self.bill()

        # --- Save, Bill, Card, Doctor & Close buttons on row 7 ---
        btn_save = tk.Button(reg, text="Save Appointment", font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", command=save)
        btn_save.grid(row=7, column=1, pady=5, padx=5, sticky='ew')
        btn_bill = tk.Button(reg, text="Bill", font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", command=self.bill)
        btn_bill.grid(row=7, column=2, pady=5, padx=5, sticky='ew')
        btn_card = tk.Button(reg, text="ID Card", font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", command=self.idcard)
        btn_card.grid(row=7, column=3, padx=5, pady=5, sticky='ew')
        btn_close = tk.Button(reg, text="Close", font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", command=self.close)
        btn_close.grid(row=7, column=4, padx=5, pady=5, sticky='ew')
        treat=tk.Frame(right_frame)
        treat.pack(fill="both", expand=True)
        # --- Right Side: Treatment Treeview (top_frame2) ---
        treatment_columns = ("Date", "Purpose", "Doctor")
        treatment_tree = ttk.Treeview(treat, columns=treatment_columns, show="headings", height=2)
        self.treatment_tree = treatment_tree
        treatment_tree.pack(side="left", fill="both", expand=True)
        treatment_tree.heading("Date", text="Date")
        treatment_tree.heading("Purpose", text="Purpose")
        treatment_tree.heading("Doctor", text="Doctor")
        treatment_tree.column("Date", width=100, anchor="center")
        treatment_tree.column("Purpose", width=100, anchor="w")
        treatment_tree.column("Doctor", width=100, anchor="center")
        
        tree_v_scrolly2 = ttk.Scrollbar(treat, orient="vertical", command=treatment_tree.yview)
        tree_v_scrolly2.pack(side="left", fill="y")
        treatment_tree.configure(yscrollcommand=tree_v_scrolly2.set)

        # tree_h_scrolly2 = ttk.Scrollbar(treat, orient="horizontal", command=treatment_tree.yview)
        # tree_h_scrolly2.pack(side="bottom", fill="x")
        # treatment_tree.configure(xscrollcommand=tree_h_scrolly2.set)

        notes=tk.Frame(right_frame)
        notes.pack(fill="both",expand="True",pady=10)
        self.entry_notes = tk.Text(notes, font=('Arial', 12), height=4, width=25)
        self.entry_notes.pack(side="left",pady=10, padx=10, fill="both", expand=True)

        med=tk.Frame(right_frame)
        med.pack(fill="both", expand=True,pady=5) 

        # --- Right Side: Medicine Treeview (middle_frame2) ---
        med_columns = ("Medicine", "Nos", "Dosage", "Days", "Amount")
        medicine_tree = ttk.Treeview(med, columns=med_columns, show="headings", height=2)
        medicine_tree.pack(side="left", fill="both", expand=True)
        medicine_tree.heading("Medicine", text="Medicine")
        medicine_tree.heading("Nos", text="Nos")
        medicine_tree.heading("Dosage", text="Dosage")
        medicine_tree.heading("Days", text="Days")
        medicine_tree.heading("Amount", text="Amount")
        medicine_tree.column("Medicine", width=100, anchor="center")
        medicine_tree.column("Nos", width=100, anchor="center")
        medicine_tree.column("Dosage", width=100, anchor="center")
        medicine_tree.column("Days", width=100, anchor="center")
        medicine_tree.column("Amount", width=100, anchor="w")

        treescrolly = ttk.Scrollbar(med, orient="vertical", command=medicine_tree.yview)
        treescrolly.pack(side="left", fill="y")
        medicine_tree.configure(yscrollcommand=treescrolly.set)

        acc=tk.Frame(right_frame)
        acc.pack(fill="both", expand=True)
        
        # --- Right Side: Accounts (bottom_frame2) ---
        acc_columns = ("Date", "Debit", "Credit", "Particulars", "Balance")
        self.acc_tree = ttk.Treeview(acc, columns=acc_columns, show="headings", height=4)
        self.acc_tree.pack(side="left", fill="both", expand=True)
        for col in acc_columns:
            self.acc_tree.heading(col, text=col)
            self.acc_tree.column(col, width=60)
        
        acc_scroll = ttk.Scrollbar(acc, orient="vertical", command=self.acc_tree.yview)
        acc_scroll.pack(side="right", fill="y")
        self.acc_tree.configure(yscrollcommand=acc_scroll.set)

        summary_frame = tk.Frame(right_frame, bg="#EAE6DF")
        summary_frame.pack(fill="x", side="bottom", padx=5, pady=2)

        self.balance_label = tk.Label(summary_frame, text="Balance: ₹0.00", font=("Arial", 8, "bold"), fg="blue")
        self.balance_label.pack(side="right",fill="x")


        app=tk.Frame(left_frame)
        app.pack(fill="both",expand="True",pady=10)
        
        # --- Bottom Frame: Patient Appointment Tree ---
        columns = ("Patient ID", "Patient Name", "Address 1", "Treatment", "Doctor Name")
        patient_tree = ttk.Treeview(app, columns=columns, show="headings", height=12)
        self.patient_tree = patient_tree

        scroll = ttk.Scrollbar(app, orient="vertical", command=patient_tree.yview)
        scroll.pack(side="right", fill="y")
        
        patient_tree.pack(side="left", fill="both", expand=True)
        patient_tree.configure(yscrollcommand=scroll.set)

        for col in columns:
            patient_tree.heading(col, text=col)
            patient_tree.column(col, width=100)

        for row in get_all_appointments(self.app):
            app_date = row[9] if len(row) > 9 and row[9] else ""
            if app_date and not is_today_date(app_date):
                continue
            treatment, doc = get_patient_latest_treatment(self.app, row[0])
            if not doc and len(row) > 13 and row[13]:
                doc = row[13]
            patient_tree.insert("", "end", values=(row[0], row[1], row[5], treatment, doc))

        history=tk.Frame(middle_frame)
        history.pack(fill="both",expand="True",pady=10)

        columns=["Patient id","Patient Name","Address"]
        history_tree=ttk.Treeview(history,columns=columns,show="headings",height=12)

        v_scroll=ttk.Scrollbar(history,orient="vertical",command=history_tree.yview)
        v_scroll.pack(side="right",fill="y")

        history_tree.pack(side="left",fill="both",expand=True)
        history_tree.configure(yscrollcommand=v_scroll.set)


        for col in columns:
            history_tree.heading(col,text=col)
            history_tree.column(col,width=100)

        for row in get_all_appointments(self.app):
            history_tree.insert("","end",values=(row[0],row[1],row[5]))

        # Tree selection bind
        def on_patient_select(event):
            tree = event.widget
            selected_item = tree.focus()
            if not selected_item:
                return
            values = tree.item(selected_item)["values"]
            if not values:
                return
            patient_id = values[0]
            
            # Fetch details from DB
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Appointments WHERE id=?", (patient_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Populate booking form
                self.entry_name.delete(0, 'end')
                self.entry_name.insert(0, row[1] if row[1] else "")
                self.entry_age.delete(0, 'end')
                self.entry_age.insert(0, row[2] if row[2] else "")
                self.gender_combo.set(row[3] if row[3] else "")
                self.entry_email.delete(0, 'end')
                self.entry_email.insert(0, row[11] if row[11] else "")
                self.entry_date.delete(0, 'end')
                self.entry_date.insert(0, row[9] if row[9] else "")
                self.entry_time.delete(0, 'end')
                self.entry_time.insert(0, row[10] if row[10] else "")
                self.entry_address1.delete(0, 'end')
                self.entry_address1.insert(0, row[5] if row[5] else "")
                self.entry_address2.delete(0, 'end')
                self.entry_address2.insert(0, row[6] if row[6] else "")
                self.entry_mobile1.delete(0, 'end')
                self.entry_mobile1.insert(0, row[7] if row[7] else "")
                self.entry_mobile2.delete(0, 'end')
                self.entry_mobile2.insert(0, row[8] if row[8] else "")
                self.entry_notes.delete("1.0", "end")
                self.entry_notes.insert("1.0", row[12] if row[12] else "")
                
                # Populate billing form
                self.bill_patientid.delete(0, 'end')
                self.bill_patientid.insert(0, self.format_patient_id(str(row[0])))
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
                treatment_val, doc_val = get_patient_latest_treatment(self.app, row[0])
                if doc_val:
                    self.Doctor_var.set(doc_val)
                elif len(row) > 13 and row[13]:
                    self.Doctor_var.set(row[13])
                elif len(values) > 4 and values[4]:
                    self.Doctor_var.set(values[4])
                self.load_patient_accounts(row[0])
                self.load_patient_treatments(row[0])
        
        patient_tree.bind("<<TreeviewSelect>>", on_patient_select)
        history_tree.bind("<<TreeviewSelect>>", on_patient_select)

        # Double click on history tree to connect / add patient to today's appointment (patient_tree)
        def on_history_double_click(event):
            selected_item = history_tree.focus()
            if not selected_item:
                return
            values = history_tree.item(selected_item)["values"]
            if not values:
                return
            patient_id = values[0]
            patient_name = values[1] if len(values) > 1 else ""
            address = values[2] if len(values) > 2 else ""

            today_str = datetime.now().strftime("%d-%m-%Y")
            time_str = datetime.now().strftime("%I:%M %p")
            selected_doc = self.Doctor_var.get().strip()

            # Update DB date & doctor for today's appointment
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("UPDATE Appointments SET Date=?, Time=?, Doctor_Name=? WHERE id=?", (today_str, time_str, selected_doc, patient_id))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error updating appointment date: {e}")

            treatment, doc = get_patient_latest_treatment(self.app, patient_id)
            if not doc:
                doc = selected_doc

            # Check if patient is already in patient_tree
            existing_item = None
            for child in patient_tree.get_children():
                c_vals = patient_tree.item(child)["values"]
                if c_vals and str(c_vals[0]) == str(patient_id):
                    existing_item = child
                    patient_tree.item(child, values=(patient_id, patient_name, address, treatment, doc))
                    break

            if not existing_item:
                existing_item = patient_tree.insert("", "end", values=(patient_id, patient_name, address, treatment, doc))

            # Focus and select in patient_tree
            patient_tree.selection_set(existing_item)
            patient_tree.focus(existing_item)
            patient_tree.see(existing_item)

            # Trigger selection to populate form fields
            on_patient_select(event)

        history_tree.bind("<Double-1>", on_history_double_click)

    def load_patient_accounts(self, patient_id):
        if not hasattr(self, 'acc_tree') or not self.acc_tree:
            return
        for item in self.acc_tree.get_children():
            self.acc_tree.delete(item)
        
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
                self.acc_tree.insert("", "end", values=(date_val, f"{d_num:.2f}", f"{c_num:.2f}", part_val, f"{balance:.2f}"))

            if hasattr(self, 'balance_label'):
                self.balance_label.config(text=f"Balance: ₹{balance:.2f}")
        except Exception as e:
            print(f"Error loading accounts: {e}")

    def load_patient_treatments(self, patient_id):
        if not hasattr(self, 'treatment_tree') or not self.treatment_tree:
            return
        for child in self.treatment_tree.get_children():
            self.treatment_tree.delete(child)
        
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            pid_str = str(patient_id).strip()
            reg_str = f"REG-{int(pid_str):04d}" if pid_str.isdigit() else pid_str
            cursor.execute("""
                SELECT b.Date, bt.Treatment, bt.Doctor
                FROM Bill_Treatments bt
                JOIN Bills b ON bt.Bill_ID = b.id
                WHERE b.Patient_ID = ? OR b.Reg_No = ?
                ORDER BY bt.id DESC
            """, (pid_str, reg_str))
            rows = cursor.fetchall()
            conn.close()

            for r in rows:
                date_val = r[0] if r[0] else ""
                treatment_val = r[1] if r[1] else ""
                doc_val = r[2] if r[2] else ""
                self.treatment_tree.insert("", "end", values=(date_val, treatment_val, doc_val))
        except Exception as e:
            print(f"Error loading patient treatments: {e}")

    def format_patient_id(self, patient_id):
        if not patient_id:
            return ""
        patient_id = str(patient_id).strip()
        if self.only_four_digits.get():
            return patient_id.zfill(4)[-4:]
        return patient_id

    def parse_patient_id(self, patient_id):
        if not patient_id:
            return ""
        digits = ''.join(filter(str.isdigit, str(patient_id)))
        return str(int(digits)) if digits else ""

    def update_patientid_display(self):
        current_id = self.bill_patientid.get().strip()
        parsed = self.parse_patient_id(current_id)
        self.bill_patientid.delete(0, 'end')
        self.bill_patientid.insert(0, self.format_patient_id(parsed))

    def bill(self):
        # Sync values from UI inputs
        self.patient_data = {
            "patientid": self.bill_patientid.get().strip(),
            "regno": self.bill_regno.get().strip(),
            "patientname": self.bill_patientname.get().strip(),
            "address1": self.bill_address1.get().strip(),
            "address2": self.bill_address2.get().strip(),
            "age": self.bill_age.get().strip(),
            "gender": self.bill_gender.get().strip(),
            "office": self.bill_office.get().strip(),
            "residence": self.bill_residence.get().strip(),
            "email": self.bill_email.get().strip()
        }
        b = Bill(self.app)
        b.patient_data = self.patient_data
        if hasattr(self, 'treatments_list'):
            b.treatments_list = self.treatments_list
        b.bill()

    def idcard(self):
        patient_data = {
            "patientid": self.bill_patientid.get().strip(),
            "regno": self.bill_regno.get().strip(),
            "patientname": self.bill_patientname.get().strip(),
            "address1": self.bill_address1.get().strip(),
            "address2": self.bill_address2.get().strip(),
            "age": self.bill_age.get().strip(),
            "gender": self.bill_gender.get().strip(),
        }
        c = Card(self.app)
        c.patient_data = patient_data
        c.idcard()

    def open_doctors(self):
        from doctors_d import Doctors
        d = Doctors(self.app)
        d.patient_data = {
            "patientid": self.bill_patientid.get().strip(),
            "regno": self.bill_regno.get().strip(),
            "patientname": self.bill_patientname.get().strip(),
            "address1": self.bill_address1.get().strip(),
            "address2": self.bill_address2.get().strip(),
            "age": self.bill_age.get().strip(),
            "gender": self.bill_gender.get().strip(),
            "office": self.bill_office.get().strip(),
            "residence": self.bill_residence.get().strip(),
            "email": self.bill_email.get().strip()
        }
        d.doctors_detials()

    def close(self):
        self.app.registration()
        
#------create--------
def appointments(app, Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id, Notes, Doctor_Name=""):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Appointments (Patient_Name,Age,Gender,Contact,Address1,Address2,Mobile_Number1,Mobile_Number2,Date,Time,Email_id,Notes,Doctor_Name) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id, Notes, Doctor_Name))
    conn.commit()
    conn.close()

def is_today_date(date_val):
    if not date_val:
        return True
    today_str = datetime.now().strftime("%d-%m-%Y")
    d_str = str(date_val).strip()
    if d_str == today_str:
        return True
    try:
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%y"):
            try:
                dt = datetime.strptime(d_str, fmt)
                if dt.date() == datetime.now().date():
                    return True
            except ValueError:
                pass
    except Exception:
        pass
    return False

#-------Select--------
def get_all_appointments(app=None):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Appointments')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_patient_latest_treatment(app, patient_id):
    try:
        conn = get_db_connection(app)
        cursor = conn.cursor()
        pid_str = str(patient_id).strip()
        reg_str = f"REG-{int(pid_str):04d}" if pid_str.isdigit() else pid_str
        cursor.execute("""
            SELECT bt.Treatment, bt.Doctor
            FROM Bill_Treatments bt
            JOIN Bills b ON bt.Bill_ID = b.id
            WHERE b.Patient_ID = ? OR b.Reg_No = ?
            ORDER BY bt.id DESC LIMIT 1
        """, (pid_str, reg_str))
        row = cursor.fetchone()
        conn.close()
        if row:
            treatment = row[0] if row[0] else ""
            doc = row[1] if row[1] else ""
            return treatment, doc
    except Exception:
        pass
    return "", ""

#-------update---------
def update_appointments(app, id, Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id, Notes, Doctor_Name=""):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Appointments SET Patient_Name=?,Age=?,Gender=?,Contact=?,Address1=?,Address2=?,Mobile_Number1=?,Mobile_Number2=?,Date=?,Time=?,Email_id=?,Notes=?,Doctor_Name=? WHERE id=?
    ''', (Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id, Notes, Doctor_Name, id))
    conn.commit()
    conn.close()

def get_doctor_names_from_db(app=None):
    names = []
    try:
        conn = get_db_connection(app)
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
    if not names:
        names = ["Dr. Anoop", "Dr. Terry"]
    return names
