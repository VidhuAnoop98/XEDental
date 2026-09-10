import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime 
import sqlite3
import os
from bill import Bill
from doctors_d import Doctors
from card import Card
from letter_paper import Letter
from lab import Lab


def get_db_connection(app=None):
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    if app and hasattr(app, "db_path") and app.db_path and os.path.exists(app.db_path):
        return sqlite3.connect(app.db_path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
    root_db = os.path.join(parent_dir, "dental.db")
    if os.path.exists(root_db):
        return sqlite3.connect(root_db)
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
            Email_id TEXT
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
            Comments TEXT
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
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        buttons = [
            ("Appointments", self.registration_workspace),
            ("Preview Today's Appointments", self.todayapp),
            ("Lab Work", self.lab),
        ]
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(self.app.workspace, text=text, font=('Arial', 11), width=22, command=command)
            btn.place(x=200, y=280 + i * 45)


    def todayapp(self):
        Letter(self.app, mode="form")

    def lab(self):
        Lab(self.app)

    def open_calendar(self, entry_widget):
        try:
            from tkcalendar import Calendar
        except ImportError:
            messagebox.showinfo("Calendar", "Please enter date manually in format DD-MM-YYYY (e.g. 01-04-2026).")
            return

        win = tk.Toplevel(self.app.root)
        win.title("Select Date")
        win.geometry("280x260")
        win.transient(self.app.root)

        try:
            win.grab_set()
        except Exception:
            pass

        cal = Calendar(win, selectmode="day", date_pattern="dd-mm-yyyy")
        cal.pack(padx=10, pady=10, fill="both", expand=True)

        def close_win():
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        def select():
            sel_d = cal.get_date()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, sel_d)
            close_win()
            if hasattr(self, 'filter_appointments_by_date'):
                self.filter_appointments_by_date(sel_d)

        win.protocol("WM_DELETE_WINDOW", close_win)
        tk.Button(win, text="OK", font=("Arial", 9, "bold"), bg="#28a745", fg="white", width=10, command=select).pack(pady=5)

    def filter_appointments_by_date(self, target_date=None):
        if not hasattr(self, 'patient_tree') or not self.patient_tree:
            return

        sel_date = target_date or (self.entry_date.get().strip() if hasattr(self, 'entry_date') else "")

        for child in self.patient_tree.get_children():
            self.patient_tree.delete(child)

        selected_doc = self.Doctor_var.get().strip() if hasattr(self, 'Doctor_var') and self.Doctor_var else ""
        for row in get_all_appointments(self.app):
            app_date = row[9] if len(row) > 9 and row[9] else ""
            if not sel_date or app_date == sel_date:
                treatment, doc = get_patient_latest_treatment(self.app, row[0])
                doc_name = doc if doc else selected_doc
                self.patient_tree.insert("", "end", values=(self.format_patient_id(str(row[0])), row[1], row[5], treatment, doc_name))
        
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
        reg.pack(fill="both",pady=5)

        # --- Row 0: Doctor selection ---
        Doctor_name = tk.Label(reg, text="Doctor Name:", font=('Arial', 8))
        Doctor_name.grid(row=0, column=0, padx=(20, 5), pady=10, sticky='e')
        self.Doctor_var = tk.StringVar()
        doctor_names = get_doctor_names_from_db(self.app)

        def refresh_reg_doctors():
            latest = get_doctor_names_from_db(self.app)
            self.Doctor_combo['values'] = latest
            if latest and not self.Doctor_var.get():
                self.Doctor_combo.set(latest[0])

        self.Doctor_combo = ttk.Combobox(reg, textvariable=self.Doctor_var, values=doctor_names, state="readonly", font=('Arial', 8), width=15, postcommand=refresh_reg_doctors)
        if doctor_names:
            self.Doctor_combo.set(doctor_names[0])
        self.Doctor_combo.grid(row=0, column=1, padx=(0, 20), pady=10, sticky='w')

        def on_doctor_combo_change(event=None):
            sel_doc = self.Doctor_combo.get().strip()
            if hasattr(self, 'patient_tree') and self.patient_tree:
                selected = self.patient_tree.selection()
                if selected:
                    for item in selected:
                        vals = list(self.patient_tree.item(item)["values"])
                        if len(vals) >= 5:
                            vals[4] = sel_doc
                            self.patient_tree.item(item, values=vals)

        self.Doctor_combo.bind("<<ComboboxSelected>>", on_doctor_combo_change)

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
        date_frame = tk.Frame(reg)
        date_frame.grid(row=1, column=5, padx=(0, 20), pady=10, sticky='w')

        self.entry_date = tk.Entry(date_frame, font=('Arial', 8), width=10)
        self.entry_date.insert(0, date_str)
        self.entry_date.pack(side="left")
        self.entry_date.bind("<KeyRelease>", lambda e: self.filter_appointments_by_date())

        btn_cal_date = tk.Button(date_frame, text="📅", font=('Arial', 8), bg="#17a2b8", fg="white", bd=1, cursor="hand2", command=lambda: self.open_calendar(self.entry_date))
        btn_cal_date.pack(side="left", padx=(2, 0))

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


        pat = tk.LabelFrame(middle_frame, text="Patient Details", font=("Arial", 10, "bold"))
        pat.pack(fill="both", pady=1)
        # Row 0: Patient ID & Reg No
        self.bill_patientid = tk.Entry(pat, justify="center", width=18)
        self.bill_patientid.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.bill_regno = tk.Entry(pat, justify="center", width=18)
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
        tk.Label(pat, text="Age:", font=("Arial", 8)).grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.bill_age = tk.Entry(pat, width=6)
        self.bill_age.grid(row=4, column=0, sticky="w", padx=5, pady=2)

        tk.Label(pat, text="Sex:", font=("Arial", 8)).grid(row=3, column=1, sticky="w", padx=5, pady=2)
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
                    raw_num = self.parse_patient_id(reg)
                    if raw_num.isdigit():
                        num = int(raw_num)
                        pid_search = num - 3000 if num > 3000 else num
                        cursor.execute("SELECT * FROM Appointments WHERE id=? OR id=?", (pid_search, num))
                        row = cursor.fetchone()
                    if not row:
                        cursor.execute("SELECT * FROM Appointments WHERE Contact=? OR Mobile_Number1=? OR Mobile_Number2=?", (reg, reg, reg))
                        row = cursor.fetchone()
                except Exception:
                    cursor.execute("SELECT * FROM Appointments WHERE Contact=? OR Mobile_Number1=? OR Mobile_Number2=?", (reg, reg, reg))
                    row = cursor.fetchone()
            
            if row:
                formatted_pid = self.format_patient_id(str(row[0]))
                formatted_regno = self.format_reg_no(str(row[0]))
                self.bill_patientid.delete(0, 'end')
                self.bill_patientid.insert(0, formatted_pid)
                self.bill_regno.delete(0, 'end')
                self.bill_regno.insert(0, formatted_regno)
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
                    "patientid": formatted_pid,
                    "regno": formatted_regno,
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
                self.load_patient_accounts(row[0])
                self.load_patient_treatments(row[0])
                comm_text = get_patient_comments(self.app, row[0], formatted_regno)
                self.patient_data["comments"] = comm_text
                if hasattr(self, 'doctor_committs') and self.doctor_committs:
                    self.doctor_committs.delete("1.0", "end")
                    if comm_text:
                        self.doctor_committs.insert("1.0", comm_text)
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
                self.entry_email.get()
            )
            
            # Retrieve last insert ID to populate patient_data
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(id) FROM Appointments")
                last_id = cursor.fetchone()[0]
                conn.close()
                pid_str = str(last_id) if last_id else "1"
                reg_str = self.format_reg_no(pid_str)
            except Exception:
                pid_str = "1"
                reg_str = "3001"

            formatted_pid = self.format_patient_id(pid_str)
            self.patient_data = {
                "patientid": formatted_pid,
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
            
            # Save treatments and comments from treatment_tree / doctor_committs if any
            doc_commit_text = self.doctor_committs.get("1.0", "end-1c").strip() if hasattr(self, 'doctor_committs') and self.doctor_committs else ""
            if hasattr(self, 'treatment_tree') and self.treatment_tree:
                trts = []
                for child in self.treatment_tree.get_children():
                    vals = self.treatment_tree.item(child)["values"]
                    if vals:
                        t_name = str(vals[1]) if len(vals) > 1 and vals[1] else ""
                        t_doc = str(vals[2]) if len(vals) > 2 and vals[2] else self.Doctor_combo.get().strip()
                        if t_name:
                            trts.append(("-", t_name, 0.0, t_doc))
                if trts or doc_commit_text:
                    try:
                        conn = get_db_connection(self.app)
                        cursor = conn.cursor()
                        b_date = datetime.now().strftime("%d-%m-%Y")
                        cursor.execute("SELECT id FROM Bills WHERE Patient_ID = ? OR Reg_No = ? ORDER BY id DESC LIMIT 1", (pid_str, reg_str))
                        bill_row = cursor.fetchone()
                        if bill_row:
                            bill_id = bill_row[0]
                            if doc_commit_text:
                                cursor.execute("UPDATE Bills SET Comments = ? WHERE id = ?", (doc_commit_text, bill_id))
                        else:
                            cursor.execute("INSERT INTO Bills (Patient_ID, Reg_No, Date, Total_Amount, Balance_Due, Comments) VALUES (?, ?, ?, ?, ?, ?)",
                                           (pid_str, reg_str, b_date, 0.0, 0.0, doc_commit_text))
                            bill_id = cursor.lastrowid
                        for tooth, trt, amt, doc in trts:
                            cursor.execute("INSERT INTO Bill_Treatments (Bill_ID, Tooth_No, Treatment, Amount, Doctor, Type) VALUES (?, ?, ?, ?, ?, ?)",
                                           (bill_id, tooth, trt, amt, doc, "Treatment"))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"Error saving appointment treatment/comments: {e}")
            
            # Pre-populate billing entry boxes
            self.bill_patientid.delete(0, 'end')
            self.bill_patientid.insert(0, self.patient_data["patientid"])
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
            today_str = datetime.now().strftime("%d-%m-%Y")
            selected_doc = self.Doctor_var.get().strip() if hasattr(self, 'Doctor_var') and self.Doctor_var else ""
            for child in patient_tree.get_children():
                patient_tree.delete(child)
            for row in get_all_appointments(self.app):
                app_date = row[9] if len(row) > 9 and row[9] else ""
                if app_date == today_str:
                    treatment, doc = get_patient_latest_treatment(self.app, row[0])
                    doc_name = doc if doc else selected_doc
                    patient_tree.insert("", "end", values=(self.format_patient_id(str(row[0])), row[1], row[5], treatment, doc_name))

            # Refresh history tree (full treeview)
            for child in history_tree.get_children():
                history_tree.delete(child)
            for row in get_all_appointments(self.app):
                history_tree.insert("", "end", values=(self.format_patient_id(str(row[0])), row[1], row[5]))

            # Refresh right side treatment & account treeviews and select patient
            self.load_patient_treatments(pid_str)
            self.load_patient_accounts(pid_str)
            self.select_patient_by_id(pid_str)

            messagebox.showinfo("Success", "Appointment saved successfully!")
            # Open bill view
            self.bill()

        # --- Save, Bill, Card, Doctor & Close buttons on row 7 ---
        btn_new = tk.Button(reg, text="Refresh", font=('Arial', 12, 'bold'), bg="#2196F3", fg="white", command=self.refresh_registration)
        btn_new.grid(row=7, column=0, pady=5, padx=5, sticky='ew')
        btn_save = tk.Button(reg, text="Save Appointment", font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", command=save)
        btn_save.grid(row=7, column=1, pady=5, padx=5, sticky='ew')
        btn_bill = tk.Button(reg, text="Bill", font=('Arial', 12, 'bold'), bg="#FF9800", fg="white", command=self.bill)
        btn_bill.grid(row=7, column=2, pady=5, padx=5, sticky='ew')
        btn_card = tk.Button(reg, text="ID Card", font=('Arial', 12, 'bold'), bg="#9C27B0", fg="white", command=self.idcard)
        btn_card.grid(row=7, column=3, padx=5, pady=5, sticky='ew')
        btn_close = tk.Button(reg, text="Close", font=('Arial', 12, 'bold'), bg="#F44336", fg="white", command=self.close)
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
        self.doctor_committs = tk.Text(notes, font=('Arial', 12), height=4, width=25)
        self.doctor_committs.pack(side="left",pady=10, padx=10, fill="both", expand=True)

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
        acc_input_frame = tk.Frame(acc)
        acc_input_frame.pack(fill="x", padx=2, pady=(2, 4))

        # tk.Label(acc_input_frame, text="Particulars:", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=2, pady=2, sticky="w")
        # self.acc_particulars_entry = tk.Entry(acc_input_frame, width=14)
        # self.acc_particulars_entry.grid(row=0, column=1, padx=2, pady=2)

        # tk.Label(acc_input_frame, text="Amount:", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=2, pady=2, sticky="w")
        # self.acc_amount_entry = tk.Entry(acc_input_frame, width=8)
        # self.acc_amount_entry.grid(row=0, column=3, padx=2, pady=2)

        # self.acc_type_var = tk.StringVar(value="Debit")
        # self.acc_type_combo = ttk.Combobox(acc_input_frame, textvariable=self.acc_type_var, values=["Debit", "Credit"], width=7, state="readonly")
        # self.acc_type_combo.grid(row=0, column=4, padx=2, pady=2)

        # btn_add_acc = tk.Button(acc_input_frame, text="+ Add Entry", font=("Arial", 8, "bold"), bg="#4CAF50", fg="white", command=self.add_manual_acc_item)
        # btn_add_acc.grid(row=0, column=5, padx=2, pady=2)

        # btn_del_acc = tk.Button(acc_input_frame, text="Delete Entry", font=("Arial", 8, "bold"), bg="#F44336", fg="white", command=self.delete_acc_row)
        # btn_del_acc.grid(row=0, column=6, padx=2, pady=2)

        acc_columns = ("Date", "Debit", "Credit", "Particulars", "Balance")
        self.acc_tree = ttk.Treeview(acc, columns=acc_columns, show="headings", height=4)
        self.acc_tree.pack(side="left", fill="both", expand=True)
        for col in acc_columns:
            self.acc_tree.heading(col, text=col)
            self.acc_tree.column(col, width=60)
        self.acc_tree.tag_configure("debit_row", foreground="#D32F2F")
        self.acc_tree.tag_configure("credit_row", foreground="#2E7D32")
        self.acc_tree.tag_configure("past_row", font=("Arial", 9))
        self.acc_tree.tag_configure("present_row", font=("Arial", 9, "bold"))
        
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

        today_str = datetime.now().strftime("%d-%m-%Y")
        selected_doc = self.Doctor_var.get().strip() if hasattr(self, 'Doctor_var') and self.Doctor_var else ""
        for row in get_all_appointments(self.app):
            app_date = row[9] if len(row) > 9 and row[9] else ""
            if app_date == today_str:
                treatment, doc = get_patient_latest_treatment(self.app, row[0])
                doc_name = doc if doc else selected_doc
                patient_tree.insert("", "end", values=(self.format_patient_id(str(row[0])), row[1], row[5], treatment, doc_name))

        history=tk.Frame(middle_frame)
        history.pack(fill="both",expand="True",pady=10)

        columns=["Patient id","Patient Name","Address"]
        history_tree=ttk.Treeview(history,columns=columns,show="headings",height=12)
        self.history_tree = history_tree

        v_scroll=ttk.Scrollbar(history,orient="vertical",command=history_tree.yview)
        v_scroll.pack(side="right",fill="y")

        history_tree.pack(side="left",fill="both",expand=True)
        history_tree.configure(yscrollcommand=v_scroll.set)

        for col in columns:
            history_tree.heading(col,text=col)
            history_tree.column(col,width=100)

        for row in get_all_appointments(self.app):
            history_tree.insert("","end",values=(self.format_patient_id(str(row[0])),row[1],row[5]))

        # History action buttons
        hist_btn_frame = tk.Frame(middle_frame)
        hist_btn_frame.pack(fill="x", pady=(2, 10))

        # Tree selection bind
        def on_patient_select(event):
            tree = event.widget
            selected_item = tree.focus()
            if not selected_item:
                return
            values = tree.item(selected_item)["values"]
            if not values:
                return
            patient_id = self.parse_patient_id(values[0])
            if not patient_id:
                patient_id = values[0]
            if len(values) > 4 and values[4] and hasattr(self, 'Doctor_var'):
                self.Doctor_var.set(str(values[4]))
            self._load_patient_data(patient_id)
        
        patient_tree.bind("<<TreeviewSelect>>", on_patient_select)
        history_tree.bind("<<TreeviewSelect>>", on_patient_select)
        patient_tree.bind("<Double-1>", lambda event: self.todayapp())

    def select_patient_by_id(self, patient_id):
        pid_num = self.parse_patient_id(patient_id)
        if not pid_num:
            pid_num = str(patient_id).strip()
        found_item = None
        target_tree = None

        if hasattr(self, 'patient_tree') and self.patient_tree:
            for child in self.patient_tree.get_children():
                vals = self.patient_tree.item(child)["values"]
                if vals and self.parse_patient_id(vals[0]) == pid_num:
                    found_item = child
                    target_tree = self.patient_tree
                    break

        if not found_item and hasattr(self, 'history_tree') and self.history_tree:
            for child in self.history_tree.get_children():
                vals = self.history_tree.item(child)["values"]
                if vals and self.parse_patient_id(vals[0]) == pid_num:
                    found_item = child
                    target_tree = self.history_tree
                    break

        if found_item and target_tree:
            target_tree.selection_set(found_item)
            target_tree.focus(found_item)
            target_tree.see(found_item)
            vals = target_tree.item(found_item)["values"]
            if len(vals) > 4 and vals[4] and hasattr(self, 'Doctor_var'):
                self.Doctor_var.set(str(vals[4]))

    def refresh_registration(self):
        """Clears current form inputs and reloads today's patient appointments and patient history trees from database."""
        self.clear_registration_form()

        # Reload Doctor dropdown if updated
        if hasattr(self, 'Doctor_combo'):
            doc_names = get_doctor_names_from_db(self.app)
            if doc_names:
                self.Doctor_combo['values'] = doc_names

        # Reload Today's Patient Appointments tree
        if hasattr(self, 'patient_tree') and self.patient_tree:
            for child in self.patient_tree.get_children():
                self.patient_tree.delete(child)
            today_str = datetime.now().strftime("%d-%m-%Y")
            selected_doc = self.Doctor_var.get().strip() if hasattr(self, 'Doctor_var') and self.Doctor_var else ""
            for row in get_all_appointments(self.app):
                app_date = row[9] if len(row) > 9 and row[9] else ""
                if app_date == today_str:
                    treatment, doc = get_patient_latest_treatment(self.app, row[0])
                    doc_name = doc if doc else selected_doc
                    self.patient_tree.insert("", "end", values=(self.format_patient_id(str(row[0])), row[1], row[5], treatment, doc_name))

        # Reload History tree
        if hasattr(self, 'history_tree') and self.history_tree:
            for child in self.history_tree.get_children():
                self.history_tree.delete(child)
            for row in get_all_appointments(self.app):
                self.history_tree.insert("", "end", values=(self.format_patient_id(str(row[0])), row[1], row[5]))

    def clear_registration_form(self):
        """Reset registration form entries, billing fields, and tree selections for a new patient registration."""
        self.manual_present_acc_items = []
        if hasattr(self, 'entry_name'): self.entry_name.delete(0, 'end')
        if hasattr(self, 'entry_age'): self.entry_age.delete(0, 'end')
        if hasattr(self, 'entry_email'): self.entry_email.delete(0, 'end')
        if hasattr(self, 'entry_address1'): self.entry_address1.delete(0, 'end')
        if hasattr(self, 'entry_address2'): self.entry_address2.delete(0, 'end')
        if hasattr(self, 'entry_mobile1'): self.entry_mobile1.delete(0, 'end')
        if hasattr(self, 'entry_mobile2'): self.entry_mobile2.delete(0, 'end')
        if hasattr(self, 'gender_var'): self.gender_var.set('')

        if hasattr(self, 'entry_date'):
            self.entry_date.delete(0, 'end')
            self.entry_date.insert(0, datetime.now().strftime("%d-%m-%Y"))
        if hasattr(self, 'entry_time'):
            self.entry_time.delete(0, 'end')
            self.entry_time.insert(0, datetime.now().strftime("%I:%M %p"))

        if hasattr(self, 'bill_patientid'): self.bill_patientid.delete(0, 'end')
        if hasattr(self, 'bill_regno'): self.bill_regno.delete(0, 'end')
        if hasattr(self, 'bill_patientname'): self.bill_patientname.delete(0, 'end')
        if hasattr(self, 'bill_address1'): self.bill_address1.delete(0, 'end')
        if hasattr(self, 'bill_address2'): self.bill_address2.delete(0, 'end')
        if hasattr(self, 'bill_age'): self.bill_age.delete(0, 'end')
        if hasattr(self, 'bill_gender'): self.bill_gender.set('')
        if hasattr(self, 'bill_office'): self.bill_office.delete(0, 'end')
        if hasattr(self, 'bill_residence'): self.bill_residence.delete(0, 'end')
        if hasattr(self, 'bill_email'): self.bill_email.delete(0, 'end')

        if hasattr(self, 'doctor_committs') and self.doctor_committs:
            self.doctor_committs.delete("1.0", "end")
        if hasattr(self, 'treatment_tree') and self.treatment_tree:
            for item in self.treatment_tree.get_children():
                self.treatment_tree.delete(item)
        if hasattr(self, 'acc_tree') and self.acc_tree:
            for item in self.acc_tree.get_children():
                self.acc_tree.delete(item)

        if hasattr(self, 'patient_tree') and self.patient_tree:
            for sel in self.patient_tree.selection():
                self.patient_tree.selection_remove(sel)
        if hasattr(self, 'history_tree') and self.history_tree:
            for sel in self.history_tree.selection():
                self.history_tree.selection_remove(sel)

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
            self.entry_name.focus_set()

    def _load_patient_data(self, patient_id):
        self.manual_present_acc_items = []
        conn = get_db_connection(self.app)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Appointments WHERE id=?", (patient_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            formatted_pid = self.format_patient_id(str(row[0]))
            formatted_regno = self.format_reg_no(str(row[0]))
            if hasattr(self, 'entry_name'):
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

            self.patient_data = {
                "patientid": formatted_pid,
                "regno": formatted_regno,
                "patientname": row[1] if row[1] else "",
                "address1": row[5] if row[5] else "",
                "address2": row[6] if row[6] else "",
                "age": row[2] if row[2] else "",
                "gender": row[3] if row[3] else "",
                "office": row[7] if row[7] else "",
                "residence": row[8] if row[8] else "",
                "email": row[11] if row[11] else ""
            }
            if hasattr(self, 'bill_patientid'):
                self.bill_patientid.delete(0, 'end')
                self.bill_patientid.insert(0, formatted_pid)
                self.bill_regno.delete(0, 'end')
                self.bill_regno.insert(0, formatted_regno)
                self.bill_patientname.delete(0, 'end')
                self.bill_patientname.insert(0, row[1] if row[1] else "")
                self.bill_address1.delete(0, 'end')
                self.bill_address1.insert(0, row[5] if row[5] else "")
                self.bill_address2.delete(0, 'end')
                self.bill_address2.insert(0, row[6] if row[6] else "")
                self.bill_age.delete(0, 'end')
                self.bill_age.insert(0, row[2] if row[2] else "")
                self.bill_gender.set(row[3] if row[3] else "")
                self.bill_office.delete(0, 'end')
                self.bill_office.insert(0, row[7] if row[7] else "")
                self.bill_residence.delete(0, 'end')
                self.bill_residence.insert(0, row[8] if row[8] else "")
                self.bill_email.delete(0, 'end')
                self.bill_email.insert(0, row[11] if row[11] else "")

            treatment_val, doc_val = get_patient_latest_treatment(self.app, row[0])
            if doc_val and hasattr(self, 'Doctor_var'):
                self.Doctor_var.set(doc_val)
            self.load_patient_accounts(row[0])
            self.load_patient_treatments(row[0])
            comm_text = get_patient_comments(self.app, row[0], formatted_regno)
            self.patient_data["comments"] = comm_text
            if hasattr(self, 'doctor_committs') and self.doctor_committs:
                self.doctor_committs.delete("1.0", "end")
                if comm_text:
                    self.doctor_committs.insert("1.0", comm_text)

            try:
                conn_d = get_db_connection(self.app)
                cursor_d = conn_d.cursor()
                cursor_d.execute("CREATE TABLE IF NOT EXISTS Patient_Diseases (id INTEGER PRIMARY KEY AUTOINCREMENT, Patient_ID TEXT, Reg_No TEXT, Disease TEXT, Date TEXT, Reading TEXT)")
                cursor_d.execute("SELECT Disease, Date, Reading FROM Patient_Diseases WHERE Patient_ID=? OR Reg_No=? ORDER BY id ASC", (str(row[0]), formatted_regno))
                db_diseases = cursor_d.fetchall()
                d_list = [list(dr) for dr in db_diseases]
                self.patient_data["diseases"] = d_list
                conn_d.close()
            except Exception:
                pass

    def add_manual_acc_item(self):
        if not hasattr(self, 'manual_present_acc_items'):
            self.manual_present_acc_items = []

        today_str = datetime.now().strftime("%d-%m-%Y")
        particulars_val = self.acc_particulars_entry.get().strip() if hasattr(self, 'acc_particulars_entry') else ""
        
        amt_str = self.acc_amount_entry.get().strip() if hasattr(self, 'acc_amount_entry') else ""
        try:
            amt_val = float(amt_str) if amt_str else 0.0
        except ValueError:
            amt_val = 0.0

        type_val = self.acc_type_var.get().strip() if hasattr(self, 'acc_type_var') and self.acc_type_var else "Debit"

        if type_val == "Credit":
            debit_val = 0.0
            credit_val = amt_val
        else:
            debit_val = amt_val
            credit_val = 0.0

        if not particulars_val and debit_val == 0.0 and credit_val == 0.0:
            messagebox.showwarning("Input Error", "Please enter Particulars and Amount.")
            return

        if not particulars_val:
            particulars_val = "Additional Charge" if debit_val > 0 else "Payment Received"

        self.manual_present_acc_items.append({
            "date": today_str,
            "debit": debit_val,
            "credit": credit_val,
            "particulars": particulars_val
        })

        if hasattr(self, 'acc_particulars_entry'): self.acc_particulars_entry.delete(0, 'end')
        if hasattr(self, 'acc_amount_entry'): self.acc_amount_entry.delete(0, 'end')

        patient_id = ""
        if hasattr(self, 'bill_patientid') and self.bill_patientid:
            patient_id = self.bill_patientid.get().strip()
        elif hasattr(self, 'patient_data') and self.patient_data:
            patient_id = self.patient_data.get("patientid", "")

        self.load_patient_accounts(patient_id)

    def delete_acc_row(self):
        if not hasattr(self, 'acc_tree') or not self.acc_tree:
            return
        selected = self.acc_tree.selection()
        if selected:
            for item in selected:
                vals = self.acc_tree.item(item)["values"]
                tags = self.acc_tree.item(item).get("tags", [])
                if "past_row" in tags:
                    messagebox.showwarning("Cannot Delete", "Past finalized accounts cannot be deleted.")
                    continue
                if hasattr(self, 'manual_present_acc_items') and vals:
                    self.manual_present_acc_items = [
                        m for m in self.manual_present_acc_items
                        if not (m["particulars"] == str(vals[3]) and float(m["debit"]) == float(vals[1] or 0) and float(m["credit"]) == float(vals[2] or 0))
                    ]
                self.acc_tree.delete(item)
            patient_id = ""
            if hasattr(self, 'bill_patientid') and self.bill_patientid:
                patient_id = self.bill_patientid.get().strip()
            elif hasattr(self, 'patient_data') and self.patient_data:
                patient_id = self.patient_data.get("patientid", "")
            self.load_patient_accounts(patient_id)
        else:
            messagebox.showwarning("No Selection", "Please select a present entry to delete.")

    def load_patient_accounts(self, patient_id):
        if not hasattr(self, 'acc_tree') or not self.acc_tree:
            return
        for item in self.acc_tree.get_children():
            self.acc_tree.delete(item)
        
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            pid_str = str(patient_id).strip() if patient_id else ""
            reg_str = f"REG-{int(pid_str):04d}" if pid_str.isdigit() else pid_str
            rows = []
            if pid_str:
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
            has_today_in_past = False
            today_str = datetime.now().strftime("%d-%m-%Y")

            for row in rows:
                date_val, debit_val, credit_val, part_val, bal_val = row
                d_num = float(debit_val) if debit_val else 0.0
                c_num = float(credit_val) if credit_val else 0.0
                balance += d_num - c_num
                if str(date_val).strip() == today_str:
                    has_today_in_past = True
                row_tag = ("past_row", "debit_row" if d_num > 0 or c_num == 0 else "credit_row")
                self.acc_tree.insert("", "end", values=(date_val, f"{d_num:.2f}", f"{c_num:.2f}", part_val, f"{balance:.2f}"), tags=row_tag)

            has_present_items = False
            if hasattr(self, 'manual_present_acc_items') and self.manual_present_acc_items:
                for item in self.manual_present_acc_items:
                    m_date = item.get("date", today_str)
                    m_deb = float(item.get("debit", 0.0))
                    m_crd = float(item.get("credit", 0.0))
                    m_part = item.get("particulars", "Entry")

                    if m_deb > 0 or m_crd == 0:
                        has_present_items = True
                        balance += m_deb
                        self.acc_tree.insert("", "end", values=(
                            m_date,
                            f"{m_deb:.2f}",
                            "0.00",
                            m_part,
                            f"{balance:.2f}"
                        ), tags=("present_row", "debit_row"))

                    if m_crd > 0:
                        has_present_items = True
                        balance -= m_crd
                        self.acc_tree.insert("", "end", values=(
                            m_date,
                            "0.00",
                            f"{m_crd:.2f}",
                            m_part,
                            f"{balance:.2f}"
                        ), tags=("present_row", "credit_row"))

            if rows and not has_today_in_past and not has_present_items:
                row_tag = ("past_row", "debit_row" if balance > 0 else "credit_row")
                self.acc_tree.insert("", "end", values=(today_str, "0.00", "0.00", "Balance B/F", f"{balance:.2f}"), tags=row_tag)

            if hasattr(self, 'balance_label'):
                lbl_color = "#D32F2F" if balance > 0 else "#2E7D32"
                self.balance_label.config(text=f"Balance: ₹{balance:.2f}", fg=lbl_color)
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

    def get_patient_id_format_setting(self):
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM Clinic_Settings WHERE key='patient_id_format'")
            row = cursor.fetchone()
            conn.close()
            if row and row[0]:
                return row[0].strip()
        except Exception:
            pass
        return ""

    def format_patient_id(self, patient_id):
        if not patient_id:
            return ""
        patient_id_str = str(patient_id).strip()
        parsed_num = self.parse_patient_id(patient_id_str)
        num_val = int(parsed_num) if parsed_num.isdigit() else 1

        if hasattr(self, 'only_four_digits') and self.only_four_digits.get():
            return f"{num_val:04d}"

        fmt_pattern = self.get_patient_id_format_setting()
        if not fmt_pattern:
            return f"{num_val:04d}"

        pattern = fmt_pattern

        import re
        match = re.search(r'0+\d*', pattern)
        if match:
            counter_token = match.group(0)
            zero_count = len(counter_token)
            padded_num = f"{num_val:0{zero_count}d}"
            pattern = pattern[:match.start()] + padded_num + pattern[match.end():]
        else:
            pattern = f"{pattern}-{num_val:03d}"

        now = datetime.now()
        pattern = pattern.replace("YYYY", now.strftime("%Y"))
        pattern = pattern.replace("MM", now.strftime("%m"))
        pattern = pattern.replace("DD", now.strftime("%d"))

        return pattern

    def parse_patient_id(self, patient_id):
        if not patient_id:
            return ""
        pid_str = str(patient_id).strip()
        import re
        if '-' in pid_str or '/' in pid_str:
            parts = re.split(r'[-/]', pid_str)
            last_part = parts[-1]
            digits = ''.join(filter(str.isdigit, last_part))
            if digits:
                return str(int(digits))
        digits = ''.join(filter(str.isdigit, pid_str))
        return str(int(digits)) if digits else pid_str

    def format_reg_no(self, patient_id):
        if not patient_id:
            return "3001"
        try:
            parsed = self.parse_patient_id(patient_id)
            num = int(parsed) if parsed.isdigit() else 1
            reg_num = 3000 + num
            return str(reg_num)
        except Exception:
            return str(patient_id)

    def update_patientid_display(self):
        current_id = self.bill_patientid.get().strip()
        parsed = self.parse_patient_id(current_id)
        self.bill_patientid.delete(0, 'end')
        self.bill_patientid.insert(0, self.format_patient_id(parsed))

    def bill(self):
        doc_commit_text = self.doctor_committs.get("1.0", "end-1c").strip() if hasattr(self, 'doctor_committs') and self.doctor_committs else ""
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
            "email": self.bill_email.get().strip(),
            "comments": doc_commit_text
        }
        if doc_commit_text:
            save_patient_comments(self.app, self.patient_data["patientid"], self.patient_data["regno"], doc_commit_text)
        b = Bill(self.app)
        b.patient_data = self.patient_data

        trts = []
        if hasattr(self, 'treatment_tree') and self.treatment_tree and self.treatment_tree.winfo_exists():
            try:
                for child in self.treatment_tree.get_children():
                    vals = self.treatment_tree.item(child)["values"]
                    if vals:
                        t_name = str(vals[1]) if len(vals) > 1 and vals[1] else ""
                        t_doc = str(vals[2]) if len(vals) > 2 and vals[2] else (self.Doctor_combo.get().strip() if hasattr(self, 'Doctor_combo') and self.Doctor_combo else "")
                        if t_name:
                            trts.append(("-", t_name, "0.00", "", t_doc))
            except Exception as e:
                print(f"Treatment tree access error: {e}")

        if hasattr(self, 'treatments_list') and self.treatments_list:
            b.treatments_list = self.treatments_list + [t for t in trts if t not in self.treatments_list]
        else:
            b.treatments_list = trts

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
def appointments(app, Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Appointments (Patient_Name,Age,Gender,Contact,Address1,Address2,Mobile_Number1,Mobile_Number2,Date,Time,Email_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', (Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id))
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
def update_appointments(app, id, Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Appointments SET Patient_Name=?,Age=?,Gender=?,Contact=?,Address1=?,Address2=?,Mobile_Number1=?,Mobile_Number2=?,Date=?,Time=?,Email_id=? WHERE id=?
    ''', (Patient_Name, Age, Gender, Contact, Address1, Address2, Mobile_Number1, Mobile_Number2, Date, Time, Email_id, id))
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
    return names

def get_patient_comments(app, pid_val, reg_val=""):
    if not pid_val and not reg_val:
        return ""
    try:
        conn = get_db_connection(app)
        cursor = conn.cursor()
        pid_str = str(pid_val).strip() if pid_val else ""
        reg_str = str(reg_val).strip() if reg_val else ""
        digits = ''.join(filter(str.isdigit, pid_str))
        pid_num = str(int(digits)) if digits else pid_str
        reg_num = str(int(digits) + 3000) if digits else reg_str
        reg_prefix = f"REG-{reg_num}"

        cursor.execute("""
            SELECT Comments FROM Bills
            WHERE (Patient_ID = ? OR Patient_ID = ? OR Reg_No = ? OR Reg_No = ? OR Reg_No = ?)
              AND Comments IS NOT NULL AND Comments != ''
            ORDER BY id DESC LIMIT 1
        """, (pid_num, pid_str, reg_num, reg_str, reg_prefix))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        print(f"Error fetching patient comments: {e}")
    return ""

def save_patient_comments(app, pid_val, reg_val, comments_text):
    if not pid_val and not reg_val:
        return
    try:
        conn = get_db_connection(app)
        cursor = conn.cursor()
        pid_str = str(pid_val).strip() if pid_val else ""
        reg_str = str(reg_val).strip() if reg_val else ""
        digits = ''.join(filter(str.isdigit, pid_str))
        pid_num = str(int(digits)) if digits else pid_str
        reg_num = str(int(digits) + 3000) if digits else reg_str
        reg_prefix = f"REG-{reg_num}"
        b_date = datetime.now().strftime("%d-%m-%Y")

        cursor.execute("""
            SELECT id FROM Bills
            WHERE Patient_ID = ? OR Patient_ID = ? OR Reg_No = ? OR Reg_No = ? OR Reg_No = ?
            ORDER BY id DESC LIMIT 1
        """, (pid_num, pid_str, reg_num, reg_str, reg_prefix))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE Bills SET Comments = ? WHERE id = ?", (comments_text, row[0]))
        else:
            cursor.execute("INSERT INTO Bills (Patient_ID, Reg_No, Date, Total_Amount, Balance_Due, Comments) VALUES (?, ?, ?, ?, ?, ?)",
                           (pid_num, reg_prefix, b_date, 0.0, 0.0, comments_text))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving patient comments: {e}")
