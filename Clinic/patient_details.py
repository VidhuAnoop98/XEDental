import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import sqlite3
import os
from files import get_db_connection

class Patient_Details:
    def __init__(self, app):
        self.app = app
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        self.patient_details()

    def patient_details(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        # Title bar
        title_bar = tk.Frame(self.workspace)
        title_bar.pack(fill="x", side="top")
        tk.Label(
            title_bar, text="Patient Details", font=("Arial", 12, "bold")).pack(padx=10, pady=6)

        # Main area
        main_frame = tk.Frame(self.workspace)
        main_frame.pack(fill="both", expand=True, padx=6, pady=6)

        left_frame = tk.Frame(main_frame, bd=1, relief="groove")
        left_frame.pack(side="left", fill="y", padx=(0, 4))

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        # ── Patient Details Form ──────────────────────
        form_lf = tk.LabelFrame(
            left_frame, text="Patient Record",
            font=("Arial", 10, "bold"), padx=8, pady=6
        )
        form_lf.pack(fill="x", padx=6, pady=(6, 2))

        self.f_patientid = tk.Entry(form_lf, width=12, justify="center")
        self.f_patientid.grid(row=0, column=1, padx=4, pady=2, sticky="w")

        self.f_regno = tk.Entry(form_lf, width=12, justify="center")
        self.f_regno.grid(row=0, column=2, padx=4, pady=2, sticky="w")

        self.f_patientname = tk.Entry(form_lf, width=18)
        self.f_patientname.grid(row=1, column=1, padx=4, pady=2, sticky="we")

        self.f_address1 = tk.Entry(form_lf, width=18)
        self.f_address1.grid(row=1, column=2,padx=4, pady=2, sticky="we")

        self.f_address2 = tk.Entry(form_lf, width=28)
        self.f_address2.grid(row=2, column=1, columnspan=2, padx=4, pady=2, sticky="we")

        age=tk.Label(form_lf,text="Age")
        age.grid(row=3,column=1,padx=4,pady=2,sticky="w")
        self.f_age = tk.Entry(form_lf, width=6)
        self.f_age.grid(row=4, column=1, padx=4, pady=2, sticky="w")

        gender=tk.Label(form_lf,text="Gender")
        gender.grid(row=3,column=2,padx=4,pady=2,sticky="w")
        self.f_gender = ttk.Combobox(
            form_lf, values=["Male", "Female"], state="readonly", width=10
        )
        self.f_gender.grid(row=4, column=2, padx=4, pady=2, sticky="w")

        self.f_mobile1 = tk.Entry(form_lf, width=14)
        self.f_mobile1.grid(row=5, column=1, padx=4, pady=2, sticky="w")

        self.f_mobile2 = tk.Entry(form_lf, width=14)
        self.f_mobile2.grid(row=5, column=2, padx=4, pady=2, sticky="w")

        self.f_email = tk.Entry(form_lf, width=18)
        self.f_email.grid(row=6, column=1, columnspan=2, padx=4, pady=2, sticky="we")

        # ── Action Buttons ────────────────────────────
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill="x", padx=6, pady=4)

        btn_cfg = dict(font=("Arial", 9, "bold"), width=9, relief="raised", bd=2)
        tk.Button(btn_frame, text="UPDATE", bg="#8E44AD", fg="white", command=self._form_update, **btn_cfg).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(btn_frame, text="DELETE", bg="#C0392B", fg="white", command=self._form_delete, **btn_cfg).grid(row=0, column=2, padx=3, pady=3)
        tk.Button(btn_frame, text="CLOSE",  bg="#7F8C8D", fg="white", command=self.close,        **btn_cfg).grid(row=0, column=3, padx=3, pady=3)

        # ── Search / Filter Panel ─────────────────────
        find_lf = tk.LabelFrame(
            left_frame, text="Search / Filter",
            font=("Arial", 10, "bold"), padx=8, pady=6
        )
        find_lf.pack(fill="x", padx=6, pady=(4, 6))

        search_fields = [
            ("Find by Name:", "s_name"),
            ("House Name:",   "s_house"),
            ("Place:",        "s_place"),
            ("Referred By:",  "s_refby"),
            ("Phone (O):",    "s_phoneo"),
            ("Phone (R):",    "s_phoner"),
        ]
        self._search_vars = {}
        for i, (label_text, attr) in enumerate(search_fields):
            tk.Label(find_lf, text=label_text, font=("Arial", 8)).grid(
                row=i, column=0, sticky="e", padx=(0, 4), pady=2
            )
            var = tk.StringVar()
            e = tk.Entry(find_lf, textvariable=var, width=20)
            e.grid(row=i, column=1, padx=2, pady=2, sticky="w")
            e.bind("<KeyRelease>", lambda ev: self._search_patients())
            self._search_vars[attr] = var

        tk.Button(
            find_lf, text="Search", font=("Arial", 9, "bold"),
            bg="#2980B9", fg="white", command=self._search_patients
        ).grid(row=len(search_fields), column=0, columnspan=2, pady=4)

        # ── Patient List Table ────────────────────────
        table_top = tk.Frame(right_frame)
        table_top.pack(fill="x", pady=(0, 4))

        tk.Button(table_top, text="Refresh", font=("Arial", 9), command=self._load_patient_table).pack(side="right", padx=6)

        columns = (
            "Patient ID", "Reg No", "Patient Name",
            "Age", "Gender", "Address 1", "Address 2",
            "Mobile 1", "Mobile 2", "Email"
        )
        col_widths = (70, 75, 150, 40, 60, 130, 130, 100, 100, 150)

        tree_frame = tk.Frame(right_frame)
        tree_frame.pack(fill="both", expand=True)

        self.patient_table = ttk.Treeview(tree_frame, columns=columns, show="headings", height=30)
        for col, w in zip(columns, col_widths):
            self.patient_table.heading(col, text=col)
            self.patient_table.column(col, width=w, anchor="w")

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.patient_table.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.patient_table.xview)
        self.patient_table.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.patient_table.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.patient_table.bind("<<TreeviewSelect>>", self._on_table_select)
        self.f_patientid.bind("<Return>", self._search_by_id)
        self.f_regno.bind("<Return>", self._search_by_id)

        # ── Keyword Panel ─────────────────────────────
        key_lf = tk.LabelFrame(left_frame)
        key_lf.pack(fill="x", padx=6, pady=(4, 10))

        key_columns = ("Keyword",)
        self.key_tree = ttk.Treeview(key_lf, columns=key_columns, show="headings", height=10)
        self.key_tree.heading("Keyword", text="Keyword")
        self.key_tree.column("Keyword", width=180)
        self.key_tree.pack(fill="both", expand=True)

        self._load_patient_table()


    # ── Load / refresh patient table ─────────────
    def _load_patient_table(self, rows=None):
        for child in self.patient_table.get_children():
            self.patient_table.delete(child)

        if rows is None:
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, Patient_Name, Age, Gender, Address1, Address2, "
                    "Mobile_Number1, Mobile_Number2, Email_id, Notes "
                    "FROM Appointments ORDER BY id"
                )
                rows = cursor.fetchall()
                conn.close()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
                return

        for r in rows:
            pid   = r[0]
            reg   = f"REG-{pid:04d}"
            name  = r[1] or ""
            age   = r[2] or ""
            gen   = r[3] or ""
            ad1   = r[4] or ""
            ad2   = r[5] or ""
            mob1  = r[6] or ""
            mob2  = r[7] or ""
            email = r[8] or ""
            self.patient_table.insert("", "end",
                values=(pid, reg, name, age, gen, ad1, ad2, mob1, mob2, email))

    # ── Populate form from a DB row ───────────────
    def _populate_form(self, row):
        def _set(entry, val):
            entry.delete(0, "end")
            if val:
                entry.insert(0, str(val))

        pid = row[0]
        _set(self.f_patientid, str(pid))
        _set(self.f_regno, f"REG-{pid:04d}")
        _set(self.f_patientname, row[1])
        _set(self.f_age, row[2])
        self.f_gender.set(row[3] if row[3] else "")
        _set(self.f_address1, row[5])
        _set(self.f_address2, row[6])
        _set(self.f_mobile1, row[7])
        _set(self.f_mobile2, row[8])
        _set(self.f_email,   row[11] if len(row) > 11 else "")
        _set(self.f_notes,   row[12] if len(row) > 12 else "")

    # ── Table row click ───────────────────────────
    def _on_table_select(self, event=None):
        selected = self.patient_table.focus()
        if not selected:
            return
        values = self.patient_table.item(selected)["values"]
        if not values:
            return
        pid = values[0]
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Appointments WHERE id=?", (pid,))
            row = cursor.fetchone()
            conn.close()
            if row:
                self._populate_form(row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    # ── Search by Patient ID or Reg No ───────────
    def _search_by_id(self, event=None):
        pid_val = self.f_patientid.get().strip()
        reg_val = self.f_regno.get().strip()
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            row = None
            if pid_val:
                try:
                    cursor.execute("SELECT * FROM Appointments WHERE id=?", (int(pid_val),))
                    row = cursor.fetchone()
                except ValueError:
                    pass
            if not row and reg_val:
                try:
                    num = int(reg_val.replace("REG-", ""))
                    cursor.execute("SELECT * FROM Appointments WHERE id=?", (num,))
                    row = cursor.fetchone()
                except ValueError:
                    cursor.execute(
                        "SELECT * FROM Appointments WHERE Mobile_Number1=? OR Mobile_Number2=?",
                        (reg_val, reg_val)
                    )
                    row = cursor.fetchone()
            conn.close()
            if row:
                self._populate_form(row)
            else:
                messagebox.showinfo("Not Found", "No patient record found.")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    # ── Live search / filter ──────────────────────
    def _search_patients(self, event=None):
        name   = self._search_vars["s_name"].get().strip().lower()
        house  = self._search_vars["s_house"].get().strip().lower()
        place  = self._search_vars["s_place"].get().strip().lower()
        refby  = self._search_vars["s_refby"].get().strip().lower()
        phoneo = self._search_vars["s_phoneo"].get().strip()
        phoner = self._search_vars["s_phoner"].get().strip()

        if not any([name, house, place, refby, phoneo, phoner]):
            self._load_patient_table()
            return

        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, Patient_Name, Age, Gender, Address1, Address2, "
                "Mobile_Number1, Mobile_Number2, Email_id, Notes FROM Appointments"
            )
            all_rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return

        filtered = []
        for r in all_rows:
            pid, pname, age, gen, ad1, ad2, mob1, mob2, email, notes = r
            if name   and name   not in (pname or "").lower(): continue
            if house  and house  not in (ad1   or "").lower(): continue
            if place  and place  not in (ad2   or "").lower(): continue
            if phoneo and phoneo not in (mob1  or ""):         continue
            if phoner and phoner not in (mob2  or ""):         continue
            filtered.append(r)

        self._load_patient_table(rows=filtered)

    # ── NEW ──────────────────────────────────────
    def _form_new(self):
        for widget in (
            self.f_patientid, self.f_regno, self.f_patientname,
            self.f_address1, self.f_address2, self.f_age,
            self.f_mobile1, self.f_mobile2, self.f_email, self.f_notes
        ):
            widget.delete(0, "end")
        self.f_gender.set("")
        self.f_patientname.focus()

    # ── SAVE ─────────────────────────────────────
    def _form_save(self):
        name = self.f_patientname.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Patient Name is required.")
            return
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Appointments "
                "(Patient_Name, Age, Gender, Address1, Address2, "
                "Mobile_Number1, Mobile_Number2, Email_id, Notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    name,
                    self.f_age.get().strip(),
                    self.f_gender.get(),
                    self.f_address1.get().strip(),
                    self.f_address2.get().strip(),
                    self.f_mobile1.get().strip(),
                    self.f_mobile2.get().strip(),
                    self.f_email.get().strip(),
                    self.f_notes.get().strip(),
                )
            )
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            self.f_patientid.delete(0, "end"); self.f_patientid.insert(0, str(last_id))
            self.f_regno.delete(0, "end");     self.f_regno.insert(0, f"REG-{last_id:04d}")
            messagebox.showinfo("Saved", f"Patient saved with ID {last_id}.")
            self._load_patient_table()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    # ── UPDATE ───────────────────────────────────
    def _form_update(self):
        pid_str = self.f_patientid.get().strip()
        if not pid_str:
            messagebox.showwarning("Validation", "Select or enter a Patient ID to update.")
            return
        name = self.f_patientname.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Patient Name is required.")
            return
        try:
            pid = int(pid_str)
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Appointments SET "
                "Patient_Name=?, Age=?, Gender=?, Address1=?, Address2=?, "
                "Mobile_Number1=?, Mobile_Number2=?, Email_id=?, Notes=? "
                "WHERE id=?",
                (
                    name,
                    self.f_age.get().strip(),
                    self.f_gender.get(),
                    self.f_address1.get().strip(),
                    self.f_address2.get().strip(),
                    self.f_mobile1.get().strip(),
                    self.f_mobile2.get().strip(),
                    self.f_email.get().strip(),
                    self.f_notes.get().strip(),
                    pid,
                )
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Updated", f"Patient ID {pid} updated successfully.")
            self._load_patient_table()
        except ValueError:
            messagebox.showerror("Error", "Invalid Patient ID.")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    # ── DELETE ───────────────────────────────────
    def _form_delete(self):
        pid_str = self.f_patientid.get().strip()
        if not pid_str:
            messagebox.showwarning("Validation", "Select or enter a Patient ID to delete.")
            return
        name = self.f_patientname.get().strip() or f"ID {pid_str}"
        if not messagebox.askyesno("Confirm Delete",
                f"Delete patient '{name}'? This cannot be undone."):
            return
        try:
            pid = int(pid_str)
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Appointments WHERE id=?", (pid,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", f"Patient ID {pid} deleted.")
            self._form_new()
            self._load_patient_table()
        except ValueError:
            messagebox.showerror("Error", "Invalid Patient ID.")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def close(self):
        self.app.files()
