import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime 
import sqlite3
import os
from bill import Bill
from doctors_d import Doctors
from letter_paper import Letter

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
            Notes TEXT
        )
    ''')
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
        ]
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(app.workspace, text=text, font=('Arial', 11), width=22, command=command)
            btn.place(x=40, y=280 + i * 45)


    def todayapp(self):
        Letter(self.app, mode="form")

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
        self.Doctor_combo = ttk.Combobox(reg, textvariable=self.Doctor_var, values=["Dr. Anoop", "Dr. Terry"], state="readonly", font=('Arial', 8), width=15)
        self.Doctor_combo.grid(row=0, column=1, padx=(0, 20), pady=10, sticky='w')

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
            else:
                messagebox.showinfo("Not Found", "No patient record found.")
            conn.close()

        self.bill_patientid.bind("<Return>", search_patient_details)
        self.bill_patientid.bind("<FocusOut>", search_patient_details)
        self.bill_regno.bind("<Return>", search_patient_details)

        # --- Save Function ---
        def save():
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

            # Refresh patient tree
            for child in patient_tree.get_children():
                patient_tree.delete(child)
            for row in get_all_appointments(self.app):
                patient_tree.insert("", "end", values=(row[0], row[1], row[5], "", ""))

            # Refresh history tree
            for child in history_tree.get_children():
                history_tree.delete(child)
            for row in get_all_appointments(self.app):
                history_tree.insert("", "end", values=(row[0], row[1], row[5]))

            messagebox.showinfo("Success", "Appointment saved successfully!")
            # Open bill view
            self.bill()

        # --- Save & Bill buttons on row 7 ---
        btn_save = tk.Button(reg, text="Save Appointment", font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", command=save)
        btn_save.grid(row=7, column=1, pady=5, padx=5, sticky='ew')
        btn_bill = tk.Button(reg, text="Bill", font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", command=self.bill)
        btn_bill.grid(row=7, column=2, pady=5, padx=5, sticky='ew')
        btn_card= tk.Button(reg, text="ID Card",font=('Arial',12,'bold'), bg="#4CAF50", fg="white", command=self.idcard)
        btn_card.grid(row=7,column=3,padx=5,pady=5,sticky='ew')
        btn_close=tk.Button(reg, text="Close",font=('Arial',12,'bold'), bg="#4CAF50", fg="white", command=self.close)
        btn_close.grid(row=7,column=4,padx=5,pady=5,sticky='ew')
        treat=tk.Frame(right_frame)
        treat.pack(fill="both", expand=True)
        # --- Right Side: Treatment Treeview (top_frame2) ---
        treatment_columns = ("Date", "Purpose", "Doctor")
        treatment_tree = ttk.Treeview(treat, columns=treatment_columns, show="headings", height=2)
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
        acc_tree = ttk.Treeview(acc, columns=acc_columns, show="headings", height=4)
        acc_tree.pack(side="left", fill="both", expand=True)
        for col in acc_columns:
            acc_tree.heading(col, text=col)
            acc_tree.column(col, width=60)
        
        acc_scroll = ttk.Scrollbar(acc, orient="vertical", command=acc_tree.yview)
        acc_scroll.pack(side="right", fill="y")
        acc_tree.configure(yscrollcommand=acc_scroll.set)

        summary_frame = tk.Frame(right_frame, bg="#EAE6DF")
        summary_frame.pack(fill="x", side="bottom", padx=5, pady=2)

        self.balance_label = tk.Label(summary_frame, text="Balance: ₹0.00", font=("Arial", 8, "bold"), fg="blue")
        self.balance_label.pack(side="right",fill="x")


        app=tk.Frame(left_frame)
        app.pack(fill="both",expand="True",pady=10)
        
        # --- Bottom Frame: Patient Appointment Tree ---
        columns = ("Patient ID", "Patient Name", "Address 1", "Treatment", "Doctor Name")
        patient_tree = ttk.Treeview(app, columns=columns, show="headings", height=12)

        scroll = ttk.Scrollbar(app, orient="vertical", command=patient_tree.yview)
        scroll.pack(side="right", fill="y")
        
        patient_tree.pack(side="left", fill="both", expand=True)
        patient_tree.configure(yscrollcommand=scroll.set)

        for col in columns:
            patient_tree.heading(col, text=col)
            patient_tree.column(col, width=100)

        for row in get_all_appointments(self.app):
            # Map row details: ID (0), Name (1), Address1 (5)
            patient_tree.insert("", "end", values=(row[0], row[1], row[5], "", ""))

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
        
        patient_tree.bind("<<TreeviewSelect>>", on_patient_select)
        history_tree.bind("<<TreeviewSelect>>", on_patient_select)

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
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor
        from reportlab.lib.utils import ImageReader
        
        PAGE_W, PAGE_H = A4
        
        # ----------------------------------------------------------------------
        # Logo image - place "Dental_logo.png" next to this script (or point
        # LOGO_PATH elsewhere). A drawn placeholder is used if it's missing.
        # ----------------------------------------------------------------------
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        LOGO_PATH = os.path.join(SCRIPT_DIR, "Dental_logo.png")
        
        # ----------------------------------------------------------------------
        # Editable clinic data
        # ----------------------------------------------------------------------
        CLINIC_NAME = "ANUPAM DENTAL CLINIC"
        CLINIC_LINE = "West Gate Vaikom - 686141, Ph : 216878 Res : 216858"
        CLINIC_HOURS = "Clinic Hours :10:00 AM to 07:00 PM, Tuesday Holiday"
        FIELD_LABELS = ["Reg.No.", "PID", "Date", "Age", "Name", "Address"]
        
        # Reference aspect ratio taken from the original printed card (w / h)
        CARD_ASPECT = 716 / 492
        
        INK = HexColor("#1a1a1a")
        
        
        # ----------------------------------------------------------------------
        # Logo drawing (image with graceful fallback)
        # ----------------------------------------------------------------------
        def draw_logo(c: canvas.Canvas, cx: float, cy: float, box_w: float, box_h: float):
            """Draws the clinic logo centred at (cx, cy), fitted inside box_w x box_h."""
            if os.path.isfile(LOGO_PATH):
                img = ImageReader(LOGO_PATH)
                iw, ih = img.getSize()
                scale = min(box_w / iw, box_h / ih)
                w, h = iw * scale, ih * scale
                c.drawImage(
                    img,
                    cx - w / 2,
                    cy - h / 2,
                    width=w,
                    height=h,
                    mask="auto",
                    preserveAspectRatio=True,
                )
                return
        
            # ---- Fallback placeholder if the PNG can't be found ----
            r = min(box_w, box_h) / 2
            c.saveState()
            c.setStrokeColor(INK)
            c.setDash(1, 2)
            c.setLineWidth(0.7)
            c.circle(cx, cy, r, stroke=1, fill=0)
            c.circle(cx, cy, r - 1.5 * mm, stroke=1, fill=0)
            c.restoreState()
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", r * 0.22)
            c.drawCentredString(cx, cy + r * 0.15, "ANUPAM")
            c.setFont("Helvetica", r * 0.16)
            c.drawCentredString(cx, cy - r * 0.35, "DENTAL")
            c.drawCentredString(cx, cy - r * 0.60, "CLINIC")
        
        
        # ----------------------------------------------------------------------
        # Card drawing - all sizes are proportional to the card's own w / h.
        # ----------------------------------------------------------------------
        def draw_card(c: canvas.Canvas, x0: float, y0: float, w: float, h: float):
            """Draws one registration card inside the rectangle (x0, y0, w, h)."""
            c.setFillColor(INK)
            c.setStrokeColor(INK)
        
            def top_y(frac):
                """Convert a fraction-from-top (0=top edge, 1=bottom edge) to an
                absolute canvas y coordinate."""
                return y0 + h * (1 - frac)
        
            # ---------- outer card border ----------
            c.setLineWidth(0.4)
            c.roundRect(x0, y0, w, h, 2 * mm, stroke=1, fill=0)
        
            # ---------- title box ----------
            title_top = top_y(0.06)
            title_bottom = top_y(0.20)
            box_margin = w * 0.035
            c.setLineWidth(0.9)
            c.rect(x0 + box_margin, title_bottom, w - 2 * box_margin, title_top - title_bottom, stroke=1, fill=0)
            c.setFont("Times-Bold", h * 0.095)
            c.drawCentredString(x0 + w / 2, (title_top + title_bottom) / 2 - h * 0.028, CLINIC_NAME)
        
            # ---------- logo (top-right, alongside the field labels) ----------
            logo_cx = x0 + w * 0.685
            logo_cy = top_y(0.44)
            draw_logo(c, logo_cx, logo_cy, w * 0.30, h * 0.42)
        
            # ---------- field labels (left column) ----------
            field_x = x0 + w * 0.045
            field_fracs_top = 0.30
            field_fracs_bottom = 0.70
            n = len(FIELD_LABELS)
            step = (field_fracs_bottom - field_fracs_top) / (n - 1)
            c.setFont("Times-Roman", h * 0.062)
            for i, label in enumerate(FIELD_LABELS):
                frac = field_fracs_top + step * i
                c.drawString(field_x, top_y(frac), label)
        
            # ---------- horizontal rule ----------
            rule_y = top_y(0.755)
            c.setLineWidth(0.8)
            c.line(x0 + w * 0.045, rule_y, x0 + w * 0.955, rule_y)
        
            # ---------- address / phone line ----------
            c.setFont("Times-Roman", h * 0.052)
            c.drawCentredString(x0 + w / 2, top_y(0.815), CLINIC_LINE)
        
            # ---------- footer box: clinic hours ----------
            footer_top = top_y(0.865)
            footer_bottom = top_y(0.955)
            c.setLineWidth(0.9)
            c.rect(x0 + box_margin, footer_bottom, w - 2 * box_margin, footer_top - footer_bottom, stroke=1, fill=0)
            c.setFont("Times-Roman", h * 0.052)
            c.drawCentredString(x0 + w / 2, (footer_top + footer_bottom) / 2 - h * 0.017, CLINIC_HOURS)
        
        
        def generate_pdf(filepath: str):
            """Creates the 1-page single-card PDF at the given filepath."""
            c = canvas.Canvas(filepath, pagesize=A4)
        
            card_h = 120 * mm
            card_w = card_h * CARD_ASPECT
            x0 = (PAGE_W - card_w) / 2
            y0 = (PAGE_H - card_h) / 2
            draw_card(c, x0, y0, card_w, card_h)
        
            c.showPage()
            c.save()

    def close(self):
        self.app.registration()
        
#------create--------
def appointments(app, Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id, Notes):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Appointments (Patient_Name,Age,Gender,Contact,Address1,Address2,Mobile_Number1,Mobile_Number2,Date,Time,Email_id,Notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id, Notes))
    conn.commit()
    conn.close()

#-------Select--------
def get_all_appointments(app=None):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Appointments')
    rows = cursor.fetchall()
    conn.close()
    return rows

#-------update---------
def update_appointments(app, id, Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id, Notes):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Appointments SET Patient_Name=?,Age=?,Gender=?,Contact=?,Address1=?,Address2=?,Mobile_Number1=?,Mobile_Number2=?,Date=?,Time=?,Email_id=?,Notes=? WHERE id=?
    ''', (Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id, Notes, id))
    conn.commit()
    conn.close()
