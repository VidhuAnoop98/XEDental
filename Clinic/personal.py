from Clinic.card import Card
import warnings
import warnings
from PIL import ImageMode
from xml.etree import ElementTree
from PIL.Image import item
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from tkcalendar import Calendar
import sqlite3
import os
import subprocess
import sys
from letter_paper import Letter
from card import Card


class Personal:
    def __init__(self, app):
        self.app=app
        self.init_db()
        app.clear_workspace()
        app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        workspace = app.workspace

        col1_buttons = [
            ("Doctors Details",self.Doctors_Details), 
            ("Letter Pad",self.Letter_Pad),
            ("Plain Prescription",self.Plain_Priscription),
            ("ID Card",self.select_card),
            ("Change Telephone",self.Change_Telephone),
            ("Fees Details",self.Fees_Details),
            ("Add New Lab",self.Add_New_Lab),
            ("Shade Details",self.Shade_Details),
            ("Lab Payments",self.Lab_Payments),
            ("ID Formats",self.ID_Formats),
            ("Settings",self.Settings),
            ("Edit Medicine",self.Edit_Medicine),
            ("Edit Disease & Complaints",self.Edit_Disease_Complaints),
            ("Doctor's Leave",self.Doctors_Leave),
            ("Clinic Timing",self.Clinic_Timing)
        ]

        y_offset = 100
        for i, (text, command) in enumerate(col1_buttons):
            btn = tk.Button(workspace, text=text, font=('Arial', 11), width=20, command=command)
            btn.place(x=100, y=y_offset + i * 35)

    def get_db_connection(self):
        if hasattr(self.app, "get_db_connection"):
            return self.app.get_db_connection()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return sqlite3.connect(os.path.join(script_dir, "dental.db"))

    def init_db(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Reg_No TEXT,
                    First_Name TEXT,
                    Last_Name TEXT,
                    Sex TEXT,
                    Qualification TEXT,
                    Designation TEXT,
                    Address TEXT,
                    City TEXT,
                    Phone TEXT,
                    Mobile TEXT,
                    Email TEXT,
                    Is_Consultant INTEGER DEFAULT 0,
                    Is_Visiting INTEGER DEFAULT 0
                )
            ''')
            cursor.execute("PRAGMA table_info(Doctors)")
            columns = [col[1] for col in cursor.fetchall()]
            if "Is_Consultant" not in columns:
                cursor.execute("ALTER TABLE Doctors ADD COLUMN Is_Consultant INTEGER DEFAULT 0")
            if "Is_Visiting" not in columns:
                cursor.execute("ALTER TABLE Doctors ADD COLUMN Is_Visiting INTEGER DEFAULT 0")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Labs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Lab_Name TEXT UNIQUE NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Shades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Shade TEXT UNIQUE NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Works (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Work TEXT UNIQUE NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Lab_Payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Lab_Name TEXT NOT NULL,
                    Issue_Date TEXT,
                    Patient_ID TEXT,
                    Patient_Name TEXT,
                    Particular TEXT,
                    Dr TEXT,
                    Cr TEXT,
                    Receipt TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Treatment_Fees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Treatment TEXT UNIQUE NOT NULL,
                    Rate REAL NOT NULL DEFAULT 0,
                    Amount REAL NOT NULL DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Consultant_Rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Doctor_Name TEXT NOT NULL,
                    Treatment TEXT NOT NULL,
                    Rate REAL NOT NULL DEFAULT 0,
                    UNIQUE(Doctor_Name, Treatment)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Clinic_Settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Diseases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Disease TEXT UNIQUE NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Complaints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Complaint TEXT UNIQUE NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ContraIndications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Indication TEXT UNIQUE NOT NULL
                )
            ''')
            cursor.execute(
                "INSERT OR IGNORE INTO Clinic_Settings (key, value) VALUES (?, ?)",
                ("treatment_currency", "INR"),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO Clinic_Settings (key, value) VALUES (?, ?)",
                ("currency_symbol", "₹"),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO Clinic_Settings (key, value) VALUES (?, ?)",
                ("clinic_mobile", "9446046868"),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO Clinic_Settings (key, value) VALUES (?, ?)",
                ("clinic_telephone", ""),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO Clinic_Settings (key, value) VALUES (?, ?)",
                ("clinic_work", "216858"),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO Clinic_Settings (key, value) VALUES (?, ?)",
                ("clinic_open_time", "10:00 AM"),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO Clinic_Settings (key, value) VALUES (?, ?)",
                ("clinic_close_time", "07:00 PM"),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO Clinic_Settings (key, value) VALUES (?, ?)",
                ("clinic_holiday", "Tuesday Holiday"),
            )
            cursor.execute("SELECT COUNT(*) FROM Treatment_Fees")
            if cursor.fetchone()[0] == 0:
                defaults = [
                    ("Cleaning", 500, 500),
                    ("Extraction", 1000, 1000),
                    ("Filling", 750, 750),
                    ("Scaling", 600, 600),
                    ("RCT", 3500, 3500),
                    ("Crown", 4500, 4500),
                    ("Bridge", 8000, 8000),
                    ("Implant", 25000, 25000),
                    ("Denture", 12000, 12000),
                    ("X-Ray", 300, 300),
                    ("Consultation", 200, 200),
                ]
                cursor.executemany(
                    "INSERT INTO Treatment_Fees (Treatment, Rate, Amount) VALUES (?, ?, ?)",
                    defaults,
                )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing DB: {e}")

    def Doctors_Details(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        title = tk.Label(self.app.workspace, text="Doctor Details", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=(8, 4))

        # ── Form frame ────────────────────────────────────────────────────────────
        form_outer = tk.Frame(self.app.workspace, bd=2, relief="groove")
        form_outer.pack(padx=10, pady=4, fill="x")

        form = tk.Frame(form_outer)
        form.pack(padx=8, pady=6)

        fields = [
            # (label_text,  attr_name,    row, col_label, col_entry)
            ("Reg No",        "dd_reg_no",       0, 0, 1),
            ("First Name",    "dd_first_name",   0, 2, 3),
            ("Last Name",     "dd_last_name",    0, 4, 5),
            ("Sex",           "dd_sex",          0, 6, 7),
            ("Qualification", "dd_qualification",1, 0, 1),
            ("Designation",   "dd_designation",  1, 2, 3),
            ("Address",       "dd_address",      1, 4, 5),
            ("City",          "dd_city",         1, 6, 7),
            ("Phone",         "dd_phone",        2, 0, 1),
            ("Mobile",        "dd_mobile",       2, 2, 3),
            ("Email",         "dd_email",        2, 4, 5),
        ]

        for lbl_text, attr, row, col_lbl, col_ent in fields:
            tk.Label(form, text=lbl_text, font=("Arial", 9), anchor="e").grid(
                row=row, column=col_lbl, padx=(8, 2), pady=4, sticky="e")
            entry = tk.Entry(form, font=("Arial", 9), width=16)
            entry.grid(row=row, column=col_ent, padx=(0, 10), pady=4, sticky="w")
            setattr(self, attr, entry)

        self.dd_is_consultant = tk.BooleanVar()
        self.dd_is_visiting = tk.BooleanVar()

        # ── Treeview Container & Right Side Panel ──────────────────────────────────
        tree_outer = tk.Frame(self.app.workspace)
        tree_outer.pack(padx=10, pady=4, fill="both", expand=True)

        tree_frame = tk.Frame(tree_outer)
        tree_frame.pack(side="left", fill="both", expand=True)

        col_doctor = ("ID", "Reg No", "First Name", "Last Name", "Sex",
                      "Qualification", "Designation", "Address", "City",
                      "Phone", "Mobile", "Email", "Consultant", "Visiting")
        col_widths  = (40, 60, 90, 90, 50, 100, 100, 120, 80, 90, 90, 120, 75, 75)

        self.doctor_tree = ttk.Treeview(tree_frame, columns=col_doctor,
                                        show="headings", height=12)
        for col, w in zip(col_doctor, col_widths):
            self.doctor_tree.heading(col, text=col)
            self.doctor_tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.doctor_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                            command=self.doctor_tree.xview)
        self.doctor_tree.configure(yscrollcommand=vsb.set,
                                   xscrollcommand=hsb.set)
        self.doctor_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # ── Right Side Panel for Consultants / Visiting Checkboxes ───────────────
        right_panel = tk.LabelFrame(tree_outer, text="Doctor Type", font=("Arial", 10, "bold"), bd=2, relief="groove")
        right_panel.pack(side="right", fill="y", padx=(10, 0), pady=0, ipadx=10, ipady=10)

        self.sel_doc_label = tk.Label(right_panel, text="Select a doctor", font=("Arial", 9, "bold"), fg="#1565C0", wraplength=140)
        self.sel_doc_label.pack(pady=(10, 15))

        tk.Checkbutton(right_panel, text="Consultant Doctor", variable=self.dd_is_consultant,
                       font=("Arial", 9, "bold"), command=self._on_category_toggle).pack(anchor="w", pady=6, padx=5)
        tk.Checkbutton(right_panel, text="Visiting Doctor", variable=self.dd_is_visiting,
                       font=("Arial", 9, "bold"), command=self._on_category_toggle).pack(anchor="w", pady=6, padx=5)

        # Bind click → fill form for editing
        self.doctor_tree.bind("<<TreeviewSelect>>", self._on_doctor_select)

        # ── Buttons ───────────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self.app.workspace)
        btn_frame.pack(pady=6)

        tk.Button(btn_frame, text="Add",    font=('Arial', 10), width=10,
                  command=self._add_doctor).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Update", font=('Arial', 10), width=10,
                  command=self._update_doctor).grid(row=0, column=1, padx=6)
        tk.Button(btn_frame, text="Delete", font=('Arial', 10), width=10, fg="red",
                  command=self._delete_doctor).grid(row=0, column=2, padx=6)
        tk.Button(btn_frame, text="Clear",  font=('Arial', 10), width=10,
                  command=self._clear_doctor_form).grid(row=0, column=3, padx=6)
        tk.Button(btn_frame, text="Close",  font=('Arial', 10), width=10,
                  command=self.close).grid(row=0, column=4, padx=6)

        self._selected_doctor_id = None
        self._load_doctors()

    # ── Doctor helpers ────────────────────────────────────────────────────────────

    def _on_category_toggle(self):
        if not self._selected_doctor_id:
            return
        is_cons = 1 if self.dd_is_consultant.get() else 0
        is_vis = 1 if self.dd_is_visiting.get() else 0
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Doctors SET Is_Consultant=?, Is_Visiting=? WHERE id=?",
                (is_cons, is_vis, self._selected_doctor_id)
            )
            conn.commit()
            conn.close()
            sel = self.doctor_tree.selection()
            if sel:
                item_vals = list(self.doctor_tree.item(sel[0])["values"])
                if len(item_vals) >= 14:
                    item_vals[12] = "Yes" if is_cons else "No"
                    item_vals[13] = "Yes" if is_vis else "No"
                    self.doctor_tree.item(sel[0], values=item_vals)
        except Exception as e:
            print(f"Error updating doctor category: {e}")

    def _doctor_form_values(self):
        return (
            self.dd_reg_no.get().strip(),
            self.dd_first_name.get().strip(),
            self.dd_last_name.get().strip(),
            self.dd_sex.get().strip(),
            self.dd_qualification.get().strip(),
            self.dd_designation.get().strip(),
            self.dd_address.get().strip(),
            self.dd_city.get().strip(),
            self.dd_phone.get().strip(),
            self.dd_mobile.get().strip(),
            self.dd_email.get().strip(),
            1 if self.dd_is_consultant.get() else 0,
            1 if self.dd_is_visiting.get() else 0,
        )

    def _clear_doctor_form(self):
        for attr in ("dd_reg_no", "dd_first_name", "dd_last_name", "dd_sex",
                     "dd_qualification", "dd_designation", "dd_address",
                     "dd_city", "dd_phone", "dd_mobile", "dd_email"):
            getattr(self, attr).delete(0, tk.END)
        if hasattr(self, "dd_is_consultant"):
            self.dd_is_consultant.set(False)
        if hasattr(self, "dd_is_visiting"):
            self.dd_is_visiting.set(False)
        if hasattr(self, "sel_doc_label"):
            self.sel_doc_label.config(text="Select a doctor")
        self._selected_doctor_id = None
        if hasattr(self, "doctor_tree"):
            for sel in self.doctor_tree.selection():
                self.doctor_tree.selection_remove(sel)

    def _load_doctors(self):
        for item in self.doctor_tree.get_children():
            self.doctor_tree.delete(item)
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, Reg_No, First_Name, Last_Name, Sex, Qualification, "
                "Designation, Address, City, Phone, Mobile, Email, Is_Consultant, Is_Visiting FROM Doctors"
            )
            for row in cursor.fetchall():
                row_list = list(row)
                row_list[12] = "Yes" if row_list[12] else "No"
                row_list[13] = "Yes" if row_list[13] else "No"
                self.doctor_tree.insert("", "end", values=row_list)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load doctors: {e}")

    def _add_doctor(self):
        vals = self._doctor_form_values()
        if not vals[1]:  # First Name required
            messagebox.showwarning("Warning", "First Name is required.")
            return
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Doctors "
                "(Reg_No, First_Name, Last_Name, Sex, Qualification, "
                "Designation, Address, City, Phone, Mobile, Email, Is_Consultant, Is_Visiting) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                vals
            )
            conn.commit()
            conn.close()
            self._clear_doctor_form()
            self._load_doctors()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add doctor: {e}")

    def _update_doctor(self):
        if not self._selected_doctor_id:
            messagebox.showwarning("Warning", "Select a doctor row to update.")
            return
        vals = self._doctor_form_values()
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Doctors SET Reg_No=?, First_Name=?, Last_Name=?, Sex=?, "
                "Qualification=?, Designation=?, Address=?, City=?, Phone=?, "
                "Mobile=?, Email=?, Is_Consultant=?, Is_Visiting=? WHERE id=?",
                vals + (self._selected_doctor_id,)
            )
            conn.commit()
            conn.close()
            self._clear_doctor_form()
            self._load_doctors()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update doctor: {e}")

    def _delete_doctor(self):
        if not self._selected_doctor_id:
            messagebox.showwarning("Warning", "Select a doctor row to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected doctor?"):
            return
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Doctors WHERE id=?",
                           (self._selected_doctor_id,))
            conn.commit()
            conn.close()
            self._clear_doctor_form()
            self._load_doctors()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete doctor: {e}")

    def _on_doctor_select(self, event=None):
        sel = self.doctor_tree.selection()
        if not sel:
            return
        values = self.doctor_tree.item(sel[0])["values"]
        self._selected_doctor_id = values[0]
        attrs = ("dd_reg_no", "dd_first_name", "dd_last_name", "dd_sex",
                 "dd_qualification", "dd_designation", "dd_address",
                 "dd_city", "dd_phone", "dd_mobile", "dd_email")
        for attr, val in zip(attrs, values[1:12]):
            widget = getattr(self, attr)
            widget.delete(0, tk.END)
            widget.insert(0, str(val) if val else "")
        fname = values[2] if len(values) > 2 else ""
        lname = values[3] if len(values) > 3 else ""
        if hasattr(self, "sel_doc_label"):
            self.sel_doc_label.config(text=f"Dr. {fname} {lname}".strip())
        is_cons = values[12] if len(values) > 12 else "No"
        is_vis = values[13] if len(values) > 13 else "No"
        if hasattr(self, "dd_is_consultant"):
            self.dd_is_consultant.set(True if is_cons in (1, "1", "Yes") else False)
        if hasattr(self, "dd_is_visiting"):
            self.dd_is_visiting.set(True if is_vis in (1, "1", "Yes") else False)

    def Letter_Pad(self):
        Letter(self.app, mode="letter")

    def Plain_Priscription(self):
        Letter(self.app, mode="plain")

    def select_card(self):
        Card(self.app).select_card()

    def Change_Telephone(self):
        win = tk.Toplevel(self.app.root)
        win.title("Change Telephone")
        height = 170
        width = 400
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}") 
        
        lbl1 = tk.Label(win, text="Mobile No", font=("Arial", 11, "bold"), fg="#2C3E50")
        lbl1.grid(row=1, column=0, pady=6)
        txt1 = tk.Entry(win, width=30, justify="center")
        txt1.grid(row=1, column=1, pady=6)
        txt1.insert(0, self._get_clinic_setting("clinic_mobile", "9446046868"))

        lbl2 = tk.Label(win, text="Telephone No", font=("Arial", 11, "bold"), fg="#2C3E50")
        lbl2.grid(row=2, column=0, pady=6)
        txt2 = tk.Entry(win, width=30, justify="center")
        txt2.grid(row=2, column=1, pady=6)
        txt2.insert(0, self._get_clinic_setting("clinic_telephone", ""))

        lbl3 = tk.Label(win, text="Work No", font=("Arial", 11, "bold"), fg="#2C3E50")
        lbl3.grid(row=3, column=0, pady=6)
        txt3 = tk.Entry(win, width=30, justify="center")
        txt3.grid(row=3, column=1, pady=6)
        txt3.insert(0, self._get_clinic_setting("clinic_work", "216858"))

        btn_frame = tk.Frame(win)
        btn_frame.grid(row=5, column=1, pady=6)
        btn1 = tk.Button(btn_frame, text="Update", font=("Arial", 10), width=10, 
                         command=lambda: self._update_telephone(txt1.get().strip(), txt2.get().strip(), txt3.get().strip(), win))
        btn1.grid(row=5, column=0, padx=6)
        btn2 = tk.Button(btn_frame, text="Close", font=("Arial", 10), width=10, command=win.destroy)
        btn2.grid(row=5, column=1, padx=6)

    def _update_telephone(self, mobile_no, telephone_no, work_no, win):
        try:
            self._set_clinic_setting("clinic_mobile", mobile_no)
            self._set_clinic_setting("clinic_telephone", telephone_no)
            self._set_clinic_setting("clinic_work", work_no)
            messagebox.showinfo("Success", "Telephone/Mobile numbers updated successfully.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update telephone numbers: {e}")

    def _get_clinic_setting(self, key, default=""):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM Clinic_Settings WHERE key=?", (key,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else default
        except Exception:
            return default

    def _set_clinic_setting(self, key, value):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Clinic_Settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        conn.commit()
        conn.close()

    def _get_currency_symbol(self):
        return self._get_clinic_setting("currency_symbol", "₹")

    def _open_file(self, path):
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path], check=False)
            else:
                subprocess.run(["xdg-open", path], check=False)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def _load_treatment_fees(self):
        for item in self.fee_tree.get_children():
            self.fee_tree.delete(item)
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, Treatment, Rate, Amount FROM Treatment_Fees ORDER BY Treatment"
            )
            symbol = self._get_currency_symbol()
            for idx, row in enumerate(cursor.fetchall(), start=1):
                fee_id, treatment, rate, amount = row
                self.fee_tree.insert(
                    "",
                    "end",
                    iid=str(fee_id),
                    values=(idx, treatment, f"{symbol}{rate:.2f}", f"{symbol}{amount:.2f}"),
                )
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load treatment fees: {e}")

    def _clear_treatment_fee_form(self):
        self._selected_fee_id = None
        self.fee_treatment.delete(0, tk.END)
        self.fee_rate.delete(0, tk.END)
        self.fee_amount.delete(0, tk.END)
        for sel in self.fee_tree.selection():
            self.fee_tree.selection_remove(sel)
        self.fee_treatment.focus()

    def _on_treatment_fee_select(self, event=None):
        sel = self.fee_tree.selection()
        if not sel:
            return
        fee_id = sel[0]
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Treatment, Rate, Amount FROM Treatment_Fees WHERE id=?",
                (fee_id,),
            )
            row = cursor.fetchone()
            conn.close()
            if not row:
                return
            self._selected_fee_id = int(fee_id)
            self.fee_treatment.delete(0, tk.END)
            self.fee_rate.delete(0, tk.END)
            self.fee_amount.delete(0, tk.END)
            self.fee_treatment.insert(0, row[0])
            self.fee_rate.insert(0, str(row[1]))
            self.fee_amount.insert(0, str(row[2]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load treatment: {e}")

    def _parse_fee_value(self, value, field_name):
        text = str(value).strip()
        if not text:
            messagebox.showwarning("Warning", f"Enter {field_name}.")
            return None
        try:
            amount = float(text)
            if amount < 0:
                raise ValueError
            return amount
        except ValueError:
            messagebox.showwarning("Warning", f"Enter a valid {field_name}.")
            return None

    def _add_treatment_fee(self):
        treatment = self.fee_treatment.get().strip()
        if not treatment:
            messagebox.showwarning("Warning", "Enter Treatment name.")
            return
        rate = self._parse_fee_value(self.fee_rate.get(), "Rate")
        if rate is None:
            return
        amount_text = self.fee_amount.get().strip()
        amount = self._parse_fee_value(amount_text, "Amount") if amount_text else rate
        if amount is None:
            return
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Treatment_Fees (Treatment, Rate, Amount) VALUES (?, ?, ?)",
                (treatment, rate, amount),
            )
            conn.commit()
            conn.close()
            self._clear_treatment_fee_form()
            self._load_treatment_fees()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Warning", "Treatment already exists.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add treatment: {e}")

    def _update_treatment_fee(self):
        if not self._selected_fee_id:
            messagebox.showwarning("Warning", "Select a treatment to update.")
            return
        treatment = self.fee_treatment.get().strip()
        if not treatment:
            messagebox.showwarning("Warning", "Enter Treatment name.")
            return
        rate = self._parse_fee_value(self.fee_rate.get(), "Rate")
        if rate is None:
            return
        amount = self._parse_fee_value(self.fee_amount.get(), "Amount")
        if amount is None:
            return
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Treatment_Fees SET Treatment=?, Rate=?, Amount=? WHERE id=?",
                (treatment, rate, amount, self._selected_fee_id),
            )
            conn.commit()
            conn.close()
            self._clear_treatment_fee_form()
            self._load_treatment_fees()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Warning", "Another treatment with this name already exists.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update treatment: {e}")

    def _delete_treatment_fee(self):
        if not self._selected_fee_id:
            messagebox.showwarning("Warning", "Select a treatment to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected treatment?"):
            return
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Treatment FROM Treatment_Fees WHERE id=?",
                (self._selected_fee_id,),
            )
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "DELETE FROM Consultant_Rates WHERE Treatment=?",
                    (row[0],),
                )
            cursor.execute(
                "DELETE FROM Treatment_Fees WHERE id=?",
                (self._selected_fee_id,),
            )
            conn.commit()
            conn.close()
            self._clear_treatment_fee_form()
            self._load_treatment_fees()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete treatment: {e}")

    def _print_treatment_list(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.pdfgen import canvas
        except ImportError:
            messagebox.showerror(
                "Error",
                "ReportLab library is required. Install it using 'pip install reportlab'.",
            )
            return

        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Treatment, Rate, Amount FROM Treatment_Fees ORDER BY Treatment"
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("Print", "No treatment fees to print.")
            return

        symbol = self._get_currency_symbol()
        currency = self._get_clinic_setting("treatment_currency", "INR")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(
            script_dir, f"treatment_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        width, height = A4
        pdf = canvas.Canvas(output_path, pagesize=A4)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.setFillColor(colors.HexColor("#1A365D"))
        pdf.drawCentredString(width / 2.0, height - 50, "Treatment Fee List")

        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(colors.HexColor("#4A5568"))
        pdf.drawCentredString(
            width / 2.0,
            height - 68,
            f"Currency: {currency} ({symbol})   |   Date: {datetime.now().strftime('%d-%m-%Y')}",
        )

        y = height - 100
        pdf.setFillColor(colors.HexColor("#F7FAFC"))
        pdf.rect(40, y - 18, width - 80, 18, fill=True, stroke=False)
        pdf.setFillColor(colors.HexColor("#2D3748"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y - 13, "Sl.no.")
        pdf.drawString(100, y - 13, "Treatment")
        pdf.drawRightString(width - 170, y - 13, "Rate")
        pdf.drawRightString(width - 50, y - 13, "Amount")

        y -= 28
        pdf.setFont("Helvetica", 10)
        for idx, (treatment, rate, amount) in enumerate(rows, start=1):
            if y < 60:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)
            pdf.drawString(50, y, str(idx))
            pdf.drawString(100, y, treatment)
            pdf.drawRightString(width - 170, y, f"{symbol}{rate:.2f}")
            pdf.drawRightString(width - 50, y, f"{symbol}{amount:.2f}")
            y -= 18

        pdf.save()
        if messagebox.askyesno("Print", f"PDF saved.\nOpen file now?\n\n{output_path}"):
            self._open_file(output_path)

    def _treatment_currency(self):
        win = tk.Toplevel(self.app.root)
        win.title("Treatment Currency")
        win.geometry("320x180")
        win.transient(self.app.root)
        win.grab_set()

        options = {
            "INR (₹)": ("INR", "₹"),
            "USD ($)": ("USD", "$"),
            "EUR (€)": ("EUR", "€"),
            "GBP (£)": ("GBP", "£"),
            "AED (د.إ)": ("AED", "د.إ"),
        }
        current = self._get_clinic_setting("treatment_currency", "INR")
        current_symbol = self._get_currency_symbol()
        default_label = next(
            (label for label, (code, sym) in options.items() if code == current and sym == current_symbol),
            "INR (₹)",
        )

        tk.Label(win, text="Select Currency", font=("Arial", 11, "bold")).pack(pady=(15, 8))
        currency_var = tk.StringVar(value=default_label)
        currency_combo = ttk.Combobox(
            win,
            textvariable=currency_var,
            values=list(options.keys()),
            state="readonly",
            width=22,
            font=("Arial", 10),
        )
        currency_combo.pack(pady=5)

        def save_currency():
            selected = options.get(currency_var.get())
            if not selected:
                messagebox.showwarning("Warning", "Select a currency.")
                return
            code, symbol = selected
            self._set_clinic_setting("treatment_currency", code)
            self._set_clinic_setting("currency_symbol", symbol)
            self._load_treatment_fees()
            messagebox.showinfo("Saved", f"Currency set to {code} ({symbol}).")
            win.destroy()

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Save", width=10, command=save_currency).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Close", width=10, command=win.destroy).pack(side="left", padx=5)

    def _get_doctor_names(self):
        names = []
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT First_Name, Last_Name FROM Doctors ORDER BY First_Name, Last_Name"
            )
            for first, last in cursor.fetchall():
                name = f"Dr. {first or ''} {last or ''}".strip()
                if name != "Dr.":
                    names.append(name)
            conn.close()
        except Exception:
            pass
        if not names:
            names = ["Dr. Anoop", "Dr. Terry"]
        return names

    def _get_treatment_names(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Treatment FROM Treatment_Fees ORDER BY Treatment")
            names = [row[0] for row in cursor.fetchall()]
            conn.close()
            return names
        except Exception:
            return []

    def _consultant_wise_rates(self):
        win = tk.Toplevel(self.app.root)
        win.title("Consultants Wise Rates")
        win.geometry("620x420")
        win.transient(self.app.root)
        win.grab_set()

        form = tk.Frame(win)
        form.pack(fill="x", padx=10, pady=10)

        tk.Label(form, text="Doctor:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        doctor_combo = ttk.Combobox(
            form, values=self._get_doctor_names(), width=24, font=("Arial", 10)
        )
        doctor_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        if doctor_combo["values"]:
            doctor_combo.current(0)

        tk.Label(form, text="Treatment:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        treatment_combo = ttk.Combobox(
            form, values=self._get_treatment_names(), width=24, font=("Arial", 10)
        )
        treatment_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        if treatment_combo["values"]:
            treatment_combo.current(0)

        tk.Label(form, text="Rate:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        rate_entry = tk.Entry(form, width=26, font=("Arial", 10))
        rate_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tree_frame = tk.Frame(win)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        columns = ("Doctor", "Treatment", "Rate")
        rate_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        rate_tree.heading("Doctor", text="Doctor")
        rate_tree.heading("Treatment", text="Treatment")
        rate_tree.heading("Rate", text="Rate")
        rate_tree.column("Doctor", width=180, anchor="w")
        rate_tree.column("Treatment", width=220, anchor="w")
        rate_tree.column("Rate", width=100, anchor="e")
        rate_tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=rate_tree.yview)
        scroll.pack(side="right", fill="y")
        rate_tree.configure(yscrollcommand=scroll.set)

        selected_rate_id = {"value": None}
        symbol = self._get_currency_symbol()

        def load_consultant_rates():
            for item in rate_tree.get_children():
                rate_tree.delete(item)
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, Doctor_Name, Treatment, Rate FROM Consultant_Rates "
                    "ORDER BY Doctor_Name, Treatment"
                )
                for row in cursor.fetchall():
                    rate_id, doctor, treatment, rate = row
                    rate_tree.insert(
                        "",
                        "end",
                        iid=str(rate_id),
                        values=(doctor, treatment, f"{symbol}{rate:.2f}"),
                    )
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load consultant rates: {e}")

        def clear_rate_form():
            selected_rate_id["value"] = None
            rate_entry.delete(0, tk.END)
            for sel in rate_tree.selection():
                rate_tree.selection_remove(sel)

        def on_rate_select(event=None):
            sel = rate_tree.selection()
            if not sel:
                return
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT Doctor_Name, Treatment, Rate FROM Consultant_Rates WHERE id=?",
                    (sel[0],),
                )
                row = cursor.fetchone()
                conn.close()
                if not row:
                    return
                selected_rate_id["value"] = int(sel[0])
                doctor_combo.set(row[0])
                treatment_combo.set(row[1])
                rate_entry.delete(0, tk.END)
                rate_entry.insert(0, str(row[2]))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load rate: {e}")

        def add_consultant_rate():
            doctor = doctor_combo.get().strip()
            treatment = treatment_combo.get().strip()
            rate = self._parse_fee_value(rate_entry.get(), "Rate")
            if not doctor or not treatment or rate is None:
                if not doctor:
                    messagebox.showwarning("Warning", "Select Doctor.")
                elif not treatment:
                    messagebox.showwarning("Warning", "Select Treatment.")
                return
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Consultant_Rates (Doctor_Name, Treatment, Rate) VALUES (?, ?, ?)",
                    (doctor, treatment, rate),
                )
                conn.commit()
                conn.close()
                clear_rate_form()
                load_consultant_rates()
            except sqlite3.IntegrityError:
                messagebox.showwarning(
                    "Warning", "Rate for this doctor and treatment already exists."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add rate: {e}")

        def update_consultant_rate():
            if not selected_rate_id["value"]:
                messagebox.showwarning("Warning", "Select a rate to update.")
                return
            doctor = doctor_combo.get().strip()
            treatment = treatment_combo.get().strip()
            rate = self._parse_fee_value(rate_entry.get(), "Rate")
            if not doctor or not treatment or rate is None:
                return
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Consultant_Rates SET Doctor_Name=?, Treatment=?, Rate=? WHERE id=?",
                    (doctor, treatment, rate, selected_rate_id["value"]),
                )
                conn.commit()
                conn.close()
                clear_rate_form()
                load_consultant_rates()
            except sqlite3.IntegrityError:
                messagebox.showwarning(
                    "Warning", "Another rate for this doctor and treatment already exists."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update rate: {e}")

        def delete_consultant_rate():
            if not selected_rate_id["value"]:
                messagebox.showwarning("Warning", "Select a rate to delete.")
                return
            if not messagebox.askyesno("Confirm", "Delete selected consultant rate?"):
                return
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM Consultant_Rates WHERE id=?",
                    (selected_rate_id["value"],),
                )
                conn.commit()
                conn.close()
                clear_rate_form()
                load_consultant_rates()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete rate: {e}")

        rate_tree.bind("<<TreeviewSelect>>", on_rate_select)

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill="x", padx=10, pady=10)
        tk.Button(btn_frame, text="Add", width=10, command=add_consultant_rate).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Update", width=10, command=update_consultant_rate).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete", width=10, command=delete_consultant_rate).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Clear", width=10, command=clear_rate_form).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Close", width=10, command=win.destroy).pack(side="right", padx=4)

        load_consultant_rates()

    def Fees_Details(self):
        win = tk.Toplevel(self.app.root)
        win.title("Treatment")
        width = 800
        height = 600
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")
        win.configure(bg="white")
        win.transient(self.app.root)
        win.grab_set()

        tk.Label(
            win,
            text="Treatment Details",
            font=("Arial", 12, "bold"),
            bg="navy",
            fg="white",
        ).pack(fill="x", padx=5, pady=5)

        form = tk.Frame(win, bg="white")
        form.pack(fill="x", padx=10, pady=8)

        tk.Label(form, text="Treatment:", font=("Arial", 10), bg="white").grid(
            row=0, column=0, padx=5, pady=4, sticky="e"
        )
        self.fee_treatment = tk.Entry(form, font=("Arial", 10), width=28)
        self.fee_treatment.grid(row=0, column=1, padx=5, pady=4, sticky="w")

        tk.Label(form, text="Rate:", font=("Arial", 10), bg="white").grid(
            row=0, column=2, padx=5, pady=4, sticky="e"
        )
        self.fee_rate = tk.Entry(form, font=("Arial", 10), width=12)
        self.fee_rate.grid(row=0, column=3, padx=5, pady=4, sticky="w")

        tk.Label(form, text="Amount:", font=("Arial", 10), bg="white").grid(
            row=0, column=4, padx=5, pady=4, sticky="e"
        )
        self.fee_amount = tk.Entry(form, font=("Arial", 10), width=12)
        self.fee_amount.grid(row=0, column=5, padx=5, pady=4, sticky="w")

        action_frame = tk.Frame(win, bg="white")
        action_frame.pack(fill="x", padx=10, pady=(0, 8))
        tk.Button(action_frame, text="Add", width=10, command=self._add_treatment_fee).pack(
            side="left", padx=4
        )
        tk.Button(action_frame, text="Update", width=10, command=self._update_treatment_fee).pack(
            side="left", padx=4
        )
        tk.Button(action_frame, text="Delete", width=10, command=self._delete_treatment_fee).pack(
            side="left", padx=4
        )
        tk.Button(action_frame, text="Clear", width=10, command=self._clear_treatment_fee_form).pack(
            side="left", padx=4
        )

        content = tk.Frame(win, bg="white")
        content.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        columns = ("Sl.no.", "Treatment", "Rate", "Amount")
        self.fee_tree = ttk.Treeview(content, columns=columns, show="headings")
        self.fee_tree.heading("Sl.no.", text="Sl.no.")
        self.fee_tree.heading("Treatment", text="Treatment")
        self.fee_tree.heading("Rate", text="Rate")
        self.fee_tree.heading("Amount", text="Amount")
        self.fee_tree.column("Sl.no.", width=60, anchor="center")
        self.fee_tree.column("Treatment", width=320, anchor="w")
        self.fee_tree.column("Rate", width=120, anchor="e")
        self.fee_tree.column("Amount", width=120, anchor="e")
        self.fee_tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(content, orient="vertical", command=self.fee_tree.yview)
        scroll.pack(side="right", fill="y")
        self.fee_tree.configure(yscrollcommand=scroll.set)
        self.fee_tree.bind("<<TreeviewSelect>>", self._on_treatment_fee_select)

        btn_frame = tk.Frame(win, bg="white")
        btn_frame.pack(fill="x", padx=5, pady=(0, 10))

        btn_current = tk.Button(
            btn_frame,
            text="Treatment Currency",
            command=self._treatment_currency,
            width=18,
        )
        btn_current.pack(side="right", padx=5)
        btn_rates = tk.Button(
            btn_frame,
            text="Consultants wise rates",
            command=self._consultant_wise_rates,
            width=18,
        )
        btn_rates.pack(side="right", padx=5)
        btn_print = tk.Button(
            btn_frame,
            text="Print Treatment List",
            command=self._print_treatment_list,
            width=18,
        )
        btn_print.pack(side="right", padx=5)
        btn_close = tk.Button(btn_frame, text="Close", command=win.destroy, width=12)
        btn_close.pack(side="right", padx=5)

        self._selected_fee_id = None
        self._load_treatment_fees()
        self.fee_treatment.focus()

    def Add_New_Lab(self):
        win = tk.Toplevel(self.app.root)
        win.title("Lab Subform")
        width = 350
        height = 250
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(win, text="Lab Name :", font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.lab_name_entry = tk.Entry(win)
        self.lab_name_entry.grid(row=0, column=1, padx=5, pady=5)

        btn_add = tk.Button(win, text="Add", command=self.save_lab)
        btn_clear = tk.Button(win, text="Clear", command=self.clear_lab)
        btn_add.grid(row=1, column=1, padx=5, pady=10)
        btn_clear.grid(row=1, column=0, padx=5, pady=10)

        tree_frame = tk.Frame(win)
        tree_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        win.grid_rowconfigure(2, weight=1)
        win.grid_columnconfigure(0, weight=1)
        win.grid_columnconfigure(1, weight=1)

        columns = ('LabName',)
        self.lab_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=5)
        self.lab_tree.heading('LabName', text='Lab Name')
        self.lab_tree.column('LabName', width=250)
        self.lab_tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.lab_tree.yview)
        scroll.pack(side="right", fill="y")
        self.lab_tree.configure(yscrollcommand=scroll.set)

        self.lab_name_entry.focus()
        self.load_labs()

    def load_labs(self):
        for item in self.lab_tree.get_children():
            self.lab_tree.delete(item)
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Lab_Name FROM Labs")
            rows = cursor.fetchall()
            for row in rows:
                self.lab_tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load labs: {e}")

    def save_lab(self):
        lab = self.lab_name_entry.get().strip()
        if lab == "":
            messagebox.showwarning("Warning", "Enter Lab Name")
            return
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Labs (Lab_Name) VALUES (?)", (lab,))
            conn.commit()
            conn.close()
            self.load_labs()
            self.lab_name_entry.delete(0, tk.END)
            self.lab_name_entry.focus()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Warning", "Lab Name already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save lab: {e}")

    def clear_lab(self):
        self.lab_name_entry.delete(0, tk.END)
        self.lab_name_entry.focus()

    def Shade_Details(self):
        win = tk.Toplevel(self.app.root)
        win.title("Type of Shade and Work")
        width = 1000
        height = 500
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(
            win,
            text="Type of Shade and Work",
            font=("Arial", 14, "bold"),
            bg="#ADD8E6"
        ).pack(fill="x", pady=5)

        main = tk.Frame(win)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=1)

        # ================= Left =================
        left = tk.LabelFrame(main, text="Shade", font=("Arial", 11, "bold"))
        left.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        tk.Label(left, text="Shade").grid(row=0, column=0, padx=5, pady=5)
        self.shade_name_entry = tk.Entry(left, width=25)
        self.shade_name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.shade_tree = ttk.Treeview(left, columns=("Shade",), show="headings", height=12)
        self.shade_tree.heading("Shade", text="Shade")
        self.shade_tree.column("Shade", width=220)
        self.shade_tree.grid(row=1, column=0, columnspan=2, sticky="nsew")

        scroll1 = ttk.Scrollbar(left, orient="vertical", command=self.shade_tree.yview)
        scroll1.grid(row=1, column=2, sticky="ns")
        self.shade_tree.configure(yscrollcommand=scroll1.set)

        # ================= Middle =================
        middle = tk.LabelFrame(main, text="Lab Name", font=("Arial", 11, "bold"))
        middle.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.lab_tree_shade = ttk.Treeview(
            middle,
            columns=("LabName",),
            show="headings",
            height=12
        )
        self.lab_tree_shade.heading("LabName", text="Lab Name")
        self.lab_tree_shade.column("LabName", width=250)
        self.lab_tree_shade.grid(row=0, column=0, columnspan=3, sticky="nsew")

        scroll2 = ttk.Scrollbar(middle, orient="vertical", command=self.lab_tree_shade.yview)
        scroll2.grid(row=0, column=3, sticky="ns")
        self.lab_tree_shade.configure(yscrollcommand=scroll2.set)

        # ================= Right =================
        right = tk.LabelFrame(main, text="Work", font=("Arial", 11, "bold"))
        right.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        tk.Label(right, text="Work").grid(row=0, column=0, padx=5, pady=5)
        self.work_entry = tk.Entry(right, width=25)
        self.work_entry.grid(row=0, column=1, padx=5, pady=5)

        self.work_tree = ttk.Treeview(right, columns=("Works",), show="headings", height=12)
        self.work_tree.heading("Works", text="Works")
        self.work_tree.column("Works", width=220)
        self.work_tree.grid(row=1, column=0, columnspan=2, sticky="nsew")

        scroll3 = ttk.Scrollbar(right, orient="vertical", command=self.work_tree.yview)
        scroll3.grid(row=1, column=2, sticky="ns")
        self.work_tree.configure(yscrollcommand=scroll3.set)

        # Buttons Frame
        btn_frame = tk.Frame(win)
        btn_frame.pack(side="bottom", fill="x", pady=10)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

        tk.Button(btn_frame, text="Add", width=10, command=self.save_shade).grid(row=0, column=0, pady=5)
        tk.Button(btn_frame, text="Clear", width=10, command=self.clear_shade).grid(row=0, column=1, pady=5)
        tk.Button(btn_frame, text="Close", width=10, command=win.destroy).grid(row=0, column=2, pady=5)

        self.load_shades()
        self.load_labs_for_shade()
        self.load_works()

    def load_shades(self):
        for item in self.shade_tree.get_children():
            self.shade_tree.delete(item)
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Shade FROM Shades")
            rows = cursor.fetchall()
            for row in rows:
                self.shade_tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load shades: {e}")

    def load_labs_for_shade(self):
        for item in self.lab_tree_shade.get_children():
            self.lab_tree_shade.delete(item)
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Lab_Name FROM Labs")
            rows = cursor.fetchall()
            for row in rows:
                self.lab_tree_shade.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load labs: {e}")

    def load_works(self):
        for item in self.work_tree.get_children():
            self.work_tree.delete(item)
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Work FROM Works")
            rows = cursor.fetchall()
            for row in rows:
                self.work_tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load works: {e}")

    def save_shade(self):
        shade = self.shade_name_entry.get().strip()
        work = self.work_entry.get().strip()

        if shade == "" and work == "":
            messagebox.showwarning("Warning", "Enter Shade Name or Work Name")
            return

        conn = self.get_db_connection()
        cursor = conn.cursor()
        if shade != "":
            try:
                cursor.execute("INSERT INTO Shades (Shade) VALUES (?)", (shade,))
                conn.commit()
                self.shade_name_entry.delete(0, tk.END)
            except sqlite3.IntegrityError:
                messagebox.showwarning("Warning", "Shade already exists")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save shade: {e}")
        if work != "":
            try:
                cursor.execute("INSERT INTO Works (Work) VALUES (?)", (work,))
                conn.commit()
                self.work_entry.delete(0, tk.END)
            except sqlite3.IntegrityError:
                messagebox.showwarning("Warning", "Work already exists")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save work: {e}")
        conn.close()
        self.load_shades()
        self.load_works()

    def clear_shade(self):
        self.shade_name_entry.delete(0, tk.END)
        self.work_entry.delete(0, tk.END)
        self.shade_name_entry.focus()

    def Lab_Payments(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        title = tk.Label(self.app.workspace, text="Lab Payments", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=10)

        content_frame = tk.Frame(self.app.workspace)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_frame = tk.Frame(content_frame)
        left_frame.pack(side="left",fill="both",expand=True,padx=(0,10))

        right_frame = tk.Frame(content_frame)
        right_frame.pack(side="right",fill="both",expand=True,padx=(10,0))

        lab_frame = tk.Frame(left_frame)
        lab_frame.pack(side="top", fill="both", expand=True)

        form_frame = tk.Frame(left_frame)
        form_frame.pack(side="bottom", fill="both", expand=True, pady=(10, 0))

        self.lp_lab_tree = ttk.Treeview(lab_frame, columns=("Name"),show="headings",height=5)
        self.lp_lab_tree.pack(side="left",fill="both",expand=True)
        self.lp_lab_tree.heading("Name",text="Name")
        self.lp_lab_tree.column("Name",width=150)
        self.lp_lab_tree.bind("<<TreeviewSelect>>", self.on_lp_lab_select)

        scroll1 = ttk.Scrollbar(lab_frame, orient="vertical", command=self.lp_lab_tree.yview)
        scroll1.pack(side="left", fill="y")
        self.lp_lab_tree.configure(yscrollcommand=scroll1.set)

        column=("id", "Issue Date","Patientid","Patient Name","Particular","Dr","Cr")
        self.lp_pay_tree = ttk.Treeview(right_frame, columns=column,show="headings",height=5)
        self.lp_pay_tree.pack(side="left",fill="both",expand=True, padx=(10, 0))
        self.lp_pay_tree.heading("id",text="ID")
        self.lp_pay_tree.heading("Issue Date",text="Issue Date")
        self.lp_pay_tree.heading("Patientid",text="Patientid")
        self.lp_pay_tree.heading("Patient Name",text="Patient Name")
        self.lp_pay_tree.heading("Particular",text="Particular")
        self.lp_pay_tree.heading("Dr",text="Dr")
        self.lp_pay_tree.heading("Cr",text="Cr")
        self.lp_pay_tree.column("id",width=30, anchor="center")
        self.lp_pay_tree.column("Issue Date",width=80)
        self.lp_pay_tree.column("Patientid",width=80)
        self.lp_pay_tree.column("Patient Name",width=100)
        self.lp_pay_tree.column("Particular",width=100)
        self.lp_pay_tree.column("Dr",width=50)
        self.lp_pay_tree.column("Cr",width=50)

        scroll2 = ttk.Scrollbar(right_frame, orient="vertical", command=self.lp_pay_tree.yview)
        scroll2.pack(side="left", fill="y")
        self.lp_pay_tree.configure(yscrollcommand=scroll2.set)

        date_lbl=tk.Label(form_frame,text="Date",font=('Arial',8))
        date_lbl.grid(row=0,column=0,padx=(20,5),pady=10,sticky="e")
        self.lp_date = tk.Entry(form_frame,width=20)
        self.lp_date.grid(row=0,column=1,padx=(0,20),pady=10,sticky="w")
        self.lp_date.insert(0,datetime.now().strftime("%d-%m-%Y"))

        patientid_lbl = tk.Label(form_frame,text="Patient ID",font=('Arial',8))
        patientid_lbl.grid(row=1,column=0,padx=(20,5),pady=10,sticky="e")
        self.lp_patientid = tk.Entry(form_frame,width=20)
        self.lp_patientid.grid(row=1,column=1,padx=(0,20),pady=10,sticky="w")

        patientname_lbl = tk.Label(form_frame,text="Patient Name",font=('Arial',8))
        patientname_lbl.grid(row=2,column=0,padx=(20,5),pady=10,sticky="e")
        self.lp_patientname = tk.Entry(form_frame,width=20)
        self.lp_patientname.grid(row=2,column=1,padx=(0,20),pady=10,sticky="w")

        particular_lbl = tk.Label(form_frame,text="Particular",font=('Arial',8))
        particular_lbl.grid(row=3,column=0,padx=(20,5),pady=10,sticky="e")
        self.lp_particular = tk.Entry(form_frame,width=20)
        self.lp_particular.grid(row=3,column=1,padx=(0,20),pady=10,sticky="w")

        dr_lbl = tk.Label(form_frame,text="Dr (Amount)",font=('Arial',8))
        dr_lbl.grid(row=4,column=0,padx=(20,5),pady=10,sticky="e")
        self.lp_dr = tk.Entry(form_frame,width=20)
        self.lp_dr.grid(row=4,column=1,padx=(0,20),pady=10,sticky="w")
        
        cr_lbl = tk.Label(form_frame,text="Receipt",font=('Arial',8))
        cr_lbl.grid(row=5,column=0,padx=(20,5),pady=10,sticky="e")
        self.lp_cr = tk.Entry(form_frame,width=20)
        self.lp_cr.grid(row=5,column=1,padx=(0,20),pady=10,sticky="w")

        summarylbl = tk.Frame(form_frame)
        summarylbl.grid(row=6, column=0, columnspan=3, padx=5, pady=(10, 0), sticky="ew")
        tk.Label(summarylbl, text="Total Dr:", font=("Arial", 8, "bold")).pack(side="left", fill="x", padx=(4, 2))
        self.Total_Dr_lbl = tk.Entry(summarylbl, font=("Arial", 8, "bold"), fg="blue", width=10)
        self.Total_Dr_lbl.pack(side="left", fill="x", padx=(0, 8))
        tk.Label(summarylbl, text="Total Cr:", font=("Arial", 8, "bold")).pack(side="left", fill="x", padx=(4, 2))
        self.Total_Cr_lbl = tk.Entry(summarylbl, font=("Arial", 8, "bold"), fg="blue", width=10)
        self.Total_Cr_lbl.pack(side="left", fill="x", padx=(0, 8))
        tk.Label(summarylbl, text="Balance:", font=("Arial", 8, "bold")).pack(side="left", fill="x", padx=(4, 2))
        self.lp_balance_label = tk.Entry(summarylbl, font=("Arial", 8, "bold"), fg="blue", width=10)
        self.lp_balance_label.pack(side="left", fill="x")


        btn_add = tk.Button(form_frame,text="Add",font=('Arial',8), command=self.add_lp_payment)
        btn_add.grid(row=7,column=0,padx=10,pady=10)

        btn_delete = tk.Button(form_frame,text="Delete",font=('Arial',8), command=self.delete_lp_payment)
        btn_delete.grid(row=7,column=1,padx=10,pady=10)
        
        btn_close = tk.Button(form_frame,text="Close",font=('Arial',8),command=self.close)
        btn_close.grid(row=7,column=2,padx=10,pady=10)

        previews = tk.Button(form_frame,text="Preview Register",font=('Arial',8),command=self.previews)
        previews.grid(row=8,column=2,padx=10,pady=10)



        self.lp_selected_lab = None
        self.load_lp_labs()

    def load_lp_labs(self):
        for item in self.lp_lab_tree.get_children():
            self.lp_lab_tree.delete(item)
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Lab_Name FROM Labs")
            for row in cursor.fetchall():
                self.lp_lab_tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load labs: {e}")

    def on_lp_lab_select(self, event):
        selection = self.lp_lab_tree.selection()
        if selection:
            item = self.lp_lab_tree.item(selection[0])
            self.lp_selected_lab = item['values'][0]
            self.load_lp_payments()

    def load_lp_payments(self):
        if not self.lp_selected_lab: return
        for item in self.lp_pay_tree.get_children():
            self.lp_pay_tree.delete(item)
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, Issue_Date, Patient_ID, Patient_Name, Particular, Dr, Cr FROM Lab_Payments WHERE Lab_Name=?", (self.lp_selected_lab,))
            for row in cursor.fetchall():
                self.lp_pay_tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load payments: {e}")

    def add_lp_payment(self):
        if not self.lp_selected_lab:
            messagebox.showwarning("Warning", "Select a Lab first")
            return
            
        date = self.lp_date.get()
        pid = self.lp_patientid.get()
        pname = self.lp_patientname.get()
        part = self.lp_particular.get()
        dr = self.lp_dr.get()
        cr = self.lp_cr.get()
        rec = self.lp_receipt.get()
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Lab_Payments 
                              (Lab_Name, Issue_Date, Patient_ID, Patient_Name, Particular, Dr, Cr, Receipt) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (self.lp_selected_lab, date, pid, pname, part, dr, cr, rec))
            conn.commit()
            conn.close()
            
            self.lp_patientid.delete(0, tk.END)
            self.lp_patientname.delete(0, tk.END)
            self.lp_particular.delete(0, tk.END)
            self.lp_dr.delete(0, tk.END)
            self.lp_cr.delete(0, tk.END)
            self.lp_receipt.delete(0, tk.END)
            
            self.load_lp_payments()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add payment: {e}")

    def delete_lp_payment(self):
        selection = self.lp_pay_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a payment to delete")
            return
            
        item = self.lp_pay_tree.item(selection[0])
        payment_id = item['values'][0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this payment?"):
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Lab_Payments WHERE id=?", (payment_id,))
                conn.commit()
                conn.close()
                self.load_lp_payments()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete payment: {e}")

    def previews(self):
        messagebox.showinfo("Preview Register", "Preview feature coming soon.")

    def ID_Formats(self):
        win = tk.Toplevel(self.app.root)
        win.title("ID Formats")
        win.configure(bg="white")
        win.transient(self.app.root)
        win.grab_set()

        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = max(0, (screen_width - 520) // 3)
        y = max(0, (screen_height - 520) // 3)
        win.geometry(f"520x320+{x}+{y}")

        top_frame = tk.Frame(win, bg="white")
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(top_frame, text="Selected Pattern:", font=("Arial", 10), bg="white").pack(anchor="w")
        format1_entry = tk.Entry(top_frame, font=("Arial", 11), width=30)
        format1_entry.pack(fill="x", pady=(4, 8))

        format1 = ttk.Treeview(win, columns=("PIDF", "PatientID", "Increment Type", "Selection"), show="headings", height=7)
        format1.pack(padx=10, pady=5, fill="both", expand=True)

        format1.heading("PIDF", text="PIDF")
        format1.heading("PatientID", text="PatientID")
        format1.heading("Increment Type", text="Increment Type")
        format1.heading("Selection", text="Selection")

        format1.column("PIDF", width=60, anchor="center")
        format1.column("PatientID", width=180, anchor="center")
        format1.column("Increment Type", width=180, anchor="center")
        format1.column("Selection", width=90, anchor="center")

        def set_selected(item_id):
            for child in format1.get_children():
                values = list(format1.item(child, "values"))
                if values[3] == "☑":
                    values[3] = "☐"
                    format1.item(child, values=values)
            values = list(format1.item(item_id, "values"))
            values[3] = "☑"
            format1.item(item_id, values=values)
            format1_entry.delete(0, tk.END)
            format1_entry.insert(0, values[1])

        format1.insert("", "end", values=("1", "YYYYMMDD-001", "Daily", "☐"))
        format1.insert("", "end", values=("2", "MM-DD/001", "Financial Year", "☐"))
        format1.insert("", "end", values=("3", "MM/001", "Monthly", "☐"))
        format1.insert("", "end", values=("4", "YYYYMMDD/001", "Yearly", "☐"))

        def toggle_checkbox(event):
            item = format1.identify_row(event.y)
            column = format1.identify_column(event.x)
            if item and column == "#4":
                set_selected(item)

        def add_custom_format():
            pattern = format1_entry.get().strip()
            if not pattern:
                messagebox.showwarning("Warning", "Enter an ID format pattern first")
                return

            existing = [format1.item(child, "values")[1] for child in format1.get_children()]
            if pattern in existing:
                messagebox.showwarning("Warning", "This pattern already exists")
                return

            new_id = str(len(format1.get_children()) + 1)
            item_id = format1.insert("", "end", values=(new_id, pattern, "Custom", "☐"))
            set_selected(item_id)

        format1.bind("<Button-1>", toggle_checkbox)

        btn_frame = tk.Frame(win, bg="white")
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))
        tk.Button(btn_frame, text="Add", font=("Arial", 10), command=add_custom_format).pack(side="left", padx=(0, 8))
        tk.Button(btn_frame, text="Close", font=("Arial", 10), command=win.destroy, width=15).pack(side="right")

        

    def Settings(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        title = tk.Label(self.app.workspace, text="Settings", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=10)
        main = tk.Frame(self.app.workspace)
        main.pack(fill='both', expand=True, padx=40, pady=20)

        left = tk.LabelFrame(main, text="Appointment Type")
        left.pack(side="left", padx=5)

        middle = tk.LabelFrame(main, text="Member Type")
        middle.pack(side="left", padx=50)

        right = tk.LabelFrame(main, text="Salutation")
        right.pack(side="right", padx=5)
        
        columns=("AppointmentType",)

        tree1=ttk.Treeview(left,columns=columns,show="headings",height=15)

        tree1.heading("AppointmentType",text="Appointment Type")

        tree1.column("AppointmentType",width=220)

        tree1.pack(side="left")

        scroll=tk.Scrollbar(left,command=tree1.yview)
        scroll.pack(side="right",fill="y")

        tree1.configure(yscrollcommand=scroll.set)

        appointments=[
            "Appointed",
            "Casualty",
            "Late Come Appointment",
            "New as Casualty",
            "New with Appointment",
            "New without Appointment",
            "UN Appointed"
            ]

        for item in appointments:
            tree1.insert("",tk.END,values=(item,))

        columns = ("Name",)

        tree2 = ttk.Treeview(middle,columns=columns,show="headings",height=15)

        tree2.heading("Name", text="Member Type")
        tree2.column("Name", width=220)
        tree2.pack(side="left", fill="both", expand=True)

        scroll2 = tk.Scrollbar(middle, command=tree2.yview)
        scroll2.pack(side="right", fill="y")
        tree2.configure(yscrollcommand=scroll2.set)

        members=[
            "Friends",
            "Courier Service",
            "Relatives",
            "Dentists",
            "Skin Specialist",
            "Gynaecologist",
            "Paediatrician",
            "Neurologists",
            "Neuro Surgeon",
            "Dental Lab",
            "Medical Lab",
            "Dental Dealers",
            "Dental Mechanic",
            "Dental Faculty"
            ]
        
        for item in members:
            tree2.insert("",tk.END,value=(item,))

        tree3 = ttk.Treeview(right, columns=columns, show="headings", height=15)
        tree3.heading("Name", text="Salutation")
        tree3.column("Name", width=150)
        tree3.pack(side="left", fill="both", expand=True)

        scroll3 = tk.Scrollbar(right, command=tree3.yview)
        scroll3.pack(side="right", fill="y")
        tree3.configure(yscrollcommand=scroll3.set)

        titles=[
            "Adv.",
            "Baby",
            "Bro.",
            "Dr.",
            "Dr.Fr.",
            "Dr.Sr.",
            "Fr.",
            "Justice",
            "Kumari",
            "Lt.Col.",
            "Master",
            "Miss",
            "Mr.",
            "Mrs.",
            "Prof.",
            "Rev.Dr.",
            "Rev.Fr.",
            "Rev.Sr.",
            "Smt.",
            "Sri."
            ]

        for item in titles:
            tree3.insert("", tk.END, values=(item,))
            
       # Button Frame
        btn_close = tk.Button(self.app.workspace, text="Close", command=self.close)
        btn_close.pack(side="bottom", pady=10)


    def Edit_Medicine(self):
        pass

    def Edit_Disease_Complaints(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        title = tk.Label(self.app.workspace, text="Edit Disease & Complaints",
                         font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=(8, 4))

        # ── Three column content area ─────────────────────────────────────────
        content_frame = tk.Frame(self.app.workspace)
        content_frame.pack(fill="both", expand=True, padx=10, pady=4)

        # Column 1 – Disease List
        disease_lf = tk.LabelFrame(content_frame, text="Disease List",
                                   font=('Arial', 11, 'bold'), bd=2, relief="groove")
        disease_lf.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=4)

        # Column 2 – Complaints
        complaints_lf = tk.LabelFrame(content_frame, text="Complaints",
                                      font=('Arial', 11, 'bold'), bd=2, relief="groove")
        complaints_lf.pack(side="left", fill="both", expand=True, padx=5, pady=4)

        # Column 3 – Contra-indications / Ingredients
        contra_lf = tk.LabelFrame(content_frame, text="Contra-indications / Ingredients",
                                  font=('Arial', 11, 'bold'), bd=2, relief="groove")
        contra_lf.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=4)

        # ── Helper: build one panel (entry + Add/Delete + Treeview) ──────────
        def _make_panel(parent, table, col_name):
            """Returns the Treeview for *parent* panel backed by *table* (single TEXT col)."""

            # Entry + buttons row
            top = tk.Frame(parent)
            top.pack(fill="x", padx=8, pady=(8, 2))
            entry = tk.Entry(top, font=("Arial", 10), width=22)
            entry.pack(side="left", padx=(0, 4))

            def _load(tree):
                for ch in tree.get_children():
                    tree.delete(ch)
                try:
                    conn = self.get_db_connection()
                    cur = conn.cursor()
                    cur.execute(f"SELECT id, {col_name} FROM {table} ORDER BY {col_name}")
                    for row in cur.fetchall():
                        tree.insert("", "end", iid=str(row[0]), values=(row[1],))
                    conn.close()
                except Exception as exc:
                    messagebox.showerror("DB Error", str(exc))

            def _add(tree):
                val = entry.get().strip()
                if not val:
                    messagebox.showwarning("Input", "Please enter a value first.")
                    return
                try:
                    conn = self.get_db_connection()
                    cur = conn.cursor()
                    cur.execute(f"INSERT OR IGNORE INTO {table} ({col_name}) VALUES (?)", (val,))
                    conn.commit()
                    conn.close()
                    entry.delete(0, "end")
                    _load(tree)
                except Exception as exc:
                    messagebox.showerror("DB Error", str(exc))

            def _delete(tree):
                sel = tree.focus()
                if not sel:
                    messagebox.showwarning("Select", "Please select a row to delete.")
                    return
                if not messagebox.askyesno("Confirm", "Delete selected item?"):
                    return
                try:
                    conn = self.get_db_connection()
                    cur = conn.cursor()
                    cur.execute(f"DELETE FROM {table} WHERE id=?", (int(sel),))
                    conn.commit()
                    conn.close()
                    _load(tree)
                except Exception as exc:
                    messagebox.showerror("DB Error", str(exc))

            # Treeview
            tree = ttk.Treeview(parent, columns=(col_name,), show="headings", height=18)
            tree.heading(col_name, text=col_name.replace("_", " "))
            tree.column(col_name, width=180, anchor="w")

            # Click row → fill entry
            def _on_select(ev, t=tree, e=entry):
                sel = t.focus()
                if sel:
                    e.delete(0, "end")
                    e.insert(0, t.item(sel)["values"][0])
            tree.bind("<<TreeviewSelect>>", _on_select)

            btn_row = tk.Frame(parent)
            btn_row.pack(fill="x", padx=8, pady=2)

            # wire buttons now that tree exists
            tk.Button(top, text="ADD", font=("Arial", 9, "bold"), width=7,
                      bg="#27AE60", fg="white",
                      command=lambda t=tree: _add(t)).pack(side="left", padx=2)
            tk.Button(top, text="DELETE", font=("Arial", 9, "bold"), width=7,
                      bg="#C0392B", fg="white",
                      command=lambda t=tree: _delete(t)).pack(side="left", padx=2)

            # scrollbar
            vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)

            tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(2, 8))
            vsb.pack(side="left", fill="y", pady=(2, 8), padx=(0, 8))

            _load(tree)
            return tree

        # Build the three panels
        self.disease_tree   = _make_panel(disease_lf,    "Diseases",          "Disease")
        self.complaints_tree = _make_panel(complaints_lf, "Complaints",        "Complaint")
        self.contra_tree    = _make_panel(contra_lf,     "ContraIndications",  "Indication")

        # ── Bottom action bar ─────────────────────────────────────────────────
        bar = tk.Frame(self.app.workspace)
        bar.pack(side="bottom", fill="x", padx=10, pady=8)

        tk.Button(
            bar, text="Edit Medicine", font=("Arial", 11), width=14,
            command=self.Edit_Medicine
        ).pack(side="left", padx=8)

        tk.Button(
            bar, text="Close", font=("Arial", 11), width=10,
            command=self.close
        ).pack(side="right", padx=8)

    # ── Stub helpers kept for compatibility (no longer reference old widgets) ─
    def on_medicine_selected(self, event=None):
        pass

    def on_show_medicine(self):
        pass

    def on_clear_medicine(self):
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)

    

    def Doctors_Leave(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        title = tk.Label(self.app.workspace, text="Doctor Details", font=('Arial', 14, 'bold'), fg="navy")
        title.pack(pady=10)

        content_frame = tk.Frame(self.app.workspace)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_frame = tk.LabelFrame(content_frame, text="Doctor Schedule", font=('Arial', 11, 'bold'), bd=2, relief="groove")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        right_frame = tk.LabelFrame(content_frame, text="Appointments", font=('Arial', 11, 'bold'), bd=2, relief="groove")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=10)

        tk.Label(left_frame, text="Select Doctor:", font=('Arial', 11)).pack(anchor='w', padx=10, pady=(10, 2))
        self.doctor_combo = ttk.Combobox(left_frame, values=["Dr. Anoop", "Dr. Terry"], state="readonly", font=('Arial', 11), width=24)
        self.doctor_combo.current(0)
        self.doctor_combo.pack(anchor='w', padx=10, pady=(0, 10))

        tk.Label(left_frame, text="Selected Date:", font=('Arial', 11)).pack(anchor='w', padx=10, pady=(0, 2))
        self.selected_date_var = tk.StringVar(value="")
        self.selected_date_entry = tk.Entry(left_frame, textvariable=self.selected_date_var, font=('Arial', 11), width=18, state='readonly')
        self.selected_date_entry.pack(anchor='w', padx=10, pady=(0, 10))

        cal_frame = tk.Frame(right_frame)
        cal_frame.pack(fill='both', padx=10, pady=(0, 10))
        self.calendar = Calendar(cal_frame, selectmode='day', date_pattern='dd-mm-yyyy', font=('Arial', 12))
        self.calendar.pack(fill='both', expand=True)
        self.calendar.bind("<<CalendarSelected>>", self.on_doctor_date_selected)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        tk.Button(btn_frame, text="Show Appointments", font=('Arial', 11), bg="#4CAF50", fg="white", command=self.on_show_doctor_appointments).pack(side='left')
        tk.Button(btn_frame, text="Clear", font=('Arial', 11), command=self.on_clear_doctor_schedule).pack(side='right')

        self.doctor_tree = ttk.Treeview(left_frame, columns=("Doctorid", "Firstname", "Lastname", "Mobile1"), show="headings", height=14)
        self.doctor_tree.heading("Doctorid", text="Doctorid")
        self.doctor_tree.heading("Firstname", text="Firstname")
        self.doctor_tree.heading("Lastname", text="Lastname")
        self.doctor_tree.heading("Mobile1", text="Mobile1")
        self.doctor_tree.column("Doctorid", width=90, anchor='center')
        self.doctor_tree.column("Firstname", width=150, anchor='w')
        self.doctor_tree.column("Lastname", width=150, anchor='w')
        self.doctor_tree.column("Mobile1", width=100, anchor='center')
        self.doctor_tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.doctor_message = tk.Label(right_frame, text="Select a doctor and date, then click Show Appointments.", font=('Arial', 10), fg="gray")
        self.doctor_message.pack(padx=10, pady=(0, 10), anchor='w')

        btn_close = tk.Button(right_frame, text="Close", font=('Arial', 11), command=self.close)
        btn_close.pack(side='bottom')

    def on_doctor_date_selected(self, event=None):
        date = self.calendar.get_date()
        self.selected_date_var.set(date)

    def on_show_doctor_appointments(self):
        doctor = self.doctor_combo.get()
        date = self.selected_date_var.get() or self.calendar.get_date()
        self.selected_date_var.set(date)
        self.doctor_message.config(text=f"Appointments for {doctor} on {date}")

        for item in self.doctor_tree.get_children():
            self.doctor_tree.delete(item)

        sample_appointments = [
            ("001", "Jayesh K", "Sivan", "9588111065"),
            ("002", "Sreekala K", "Sivan", "9588111065"),
            ("003", "Seema K", "Sivan", "9588111065"),
            ("004", "Unnikrishnan K", "Sivan", "9588111065"),
        ]

        for doctor in sample_appointments:
            self.doctor_tree.insert("", "end", values=doctor)

    

    def on_clear_doctor_schedule(self):
        self.selected_date_var.set("")
        for item in self.doctor_tree.get_children():
            self.doctor_tree.delete(item)
        self.doctor_message.config(text="Select a doctor and date, then click Show Appointments.")

    def Clinic_Timing(self):
        win = tk.Toplevel(self.app.root)
        win.title("Clinic Timing & Holiday")
        width = 400
        height = 200
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}") 

        tk.Label(win, text="Opening Time:", font=('Arial', 11, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        open_entry = tk.Entry(win, font=('Arial', 11), width=20)
        open_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        open_entry.insert(0, self._get_clinic_setting("clinic_open_time", "10:00 AM"))

        tk.Label(win, text="Closing Time:", font=('Arial', 11, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        close_entry = tk.Entry(win, font=('Arial', 11), width=20)
        close_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        close_entry.insert(0, self._get_clinic_setting("clinic_close_time", "07:00 PM"))

        tk.Label(win, text="Holiday:", font=('Arial', 11, 'bold')).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        holiday_entry = tk.Entry(win, font=('Arial', 11), width=20)
        holiday_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        holiday_entry.insert(0, self._get_clinic_setting("clinic_holiday", "Tuesday Holiday"))

        btn_frame = tk.Frame(win)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)

        tk.Button(btn_frame, text="Ok", font=("Arial", 10, "bold"), width=10, bg="#27AE60", fg="white",
                  command=lambda: self._save_clinic_timing(open_entry.get().strip(), close_entry.get().strip(), holiday_entry.get().strip(), win)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Close", font=("Arial", 10), width=10,
                  command=win.destroy).pack(side="left", padx=10)

    def _save_clinic_timing(self, open_time, close_time, holiday, win):
        try:
            self._set_clinic_setting("clinic_open_time", open_time)
            self._set_clinic_setting("clinic_close_time", close_time)
            self._set_clinic_setting("clinic_holiday", holiday)
            messagebox.showinfo("Success", "Clinic timing and holiday updated successfully.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update clinic timing: {e}")

    
    
    def close(self):
        self.app.personal()
    
        
        

        



        
        


