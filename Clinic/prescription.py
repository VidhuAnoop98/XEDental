import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

class Prescription:
    def __init__(self, app):
        self.app = app
        self.patient_data = getattr(app, "patient_data", {})
        self.ensure_tables_exist()
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

    def get_db_connection(self):
        if hasattr(self.app, 'get_db_connection'):
            return self.app.get_db_connection()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return sqlite3.connect(os.path.join(script_dir, "dental.db"))

    def ensure_tables_exist(self):
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS Medicines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Category TEXT,
                    Type TEXT,
                    Product_Name TEXT,
                    Brand_Name TEXT,
                    Strength TEXT,
                    Dosage TEXT,
                    Frequency TEXT,
                    Rate REAL,
                    Duration TEXT,
                    Ingredients TEXT,
                    Contra_Indications TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS Prescriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Date TEXT,
                    Patient_ID TEXT,
                    Doctor_Name TEXT,
                    Notes TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS Allergies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Allergic_Medicine TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS Doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    First_Name TEXT,
                    Last_Name TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS Treatment_Fees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Treatment TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS Diseases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Disease TEXT
                )
            """)
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error initializing database tables: {e}")

    def prescription(self):
        tk.Label(self.app.workspace, text="Prescription", font=("Arial", 10, "bold"), fg="navy").pack(pady=2)
        content_frame = tk.Frame(self.app.workspace)
        content_frame.pack(pady=5, fill="both", expand=True)

        left_frame = tk.LabelFrame(content_frame, width=20)
        left_frame.pack(side="left", fill="y", padx=(5, 10))

        right_frame = tk.LabelFrame(content_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        doctor_name = tk.Label(left_frame, text="Doctor Name:", font=("Arial", 8))
        doctor_name.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.doctor_var = tk.StringVar()
        self.doctor_combo = ttk.Combobox(
            left_frame,
            textvariable=self.doctor_var,
            state="readonly",
            font=("Arial", 8),
            width=15,
        )
        self.doctor_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.category_tree = ttk.Treeview(left_frame, columns=("Category",), show="headings", height=8)
        self.category_tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.category_tree.heading("Category", text="Category")
        self.category_tree.column("Category", width=300, anchor="center")
        self.category_tree.bind("<ButtonRelease-1>", self.on_category_select)

        btn_Medicine = tk.Button(left_frame, text="Edit Medicine List", font=("Arial", 10, "bold"), width=15, command=self.edit_medicine)
        btn_Medicine.grid(row=2, column=1, padx=5, pady=5)

        self.med_type = ttk.Treeview(left_frame, columns=("Type",), show="headings", height=5)
        self.med_type.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.med_type.heading("Type", text="Type")
        self.med_type.column("Type", width=300, anchor="center")
        self.med_type.bind("<ButtonRelease-1>", self.on_med_type_select)

        self.allergies = ttk.Treeview(left_frame, columns=("Allergic Medicine",), show="headings", height=2)
        self.allergies.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.allergies.heading("Allergic Medicine", text="Allergic Medicine")
        self.allergies.column("Allergic Medicine", width=200, anchor="center")

        column1 = ("Patient ID", "Patient Name", "Address 1", "Treatment", "Doctor Name")
        self.patient_tree = ttk.Treeview(right_frame, columns=column1, show="headings", height=1)
        self.patient_tree.pack(side="top", fill="x", expand=True, padx=5, pady=5)

        for col in column1:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=100)

        column2 = ("Product Name", "Brand Name", "Strength", "Dosage", "Frequency", "Rate", "Duration", "Ingredients")
        self.medicine_tree = ttk.Treeview(right_frame, columns=column2, show="headings", height=5)
        self.medicine_tree.pack(side="top", fill="x", expand=True, padx=5, pady=5)
        for col in column2:
            self.medicine_tree.heading(col, text=col)
            self.medicine_tree.column(col, width=100, anchor="center")
        self.medicine_tree.bind("<Double-1>", self.on_medicine_double_click)

        column3 = ("SortNo", "Medicine", "Sales Rate", "Nos", "Amount", "Remark")
        self.medicine_info = ttk.Treeview(right_frame, columns=column3, show="headings", height=10)
        self.medicine_info.pack(side="top", fill="x", expand=True, padx=5, pady=5)
        for col in column3:
            self.medicine_info.heading(col, text=col)
            if col == "SortNo":
                self.medicine_info.column(col, width=30, anchor="center")
            elif col == "Remark":
                self.medicine_info.column(col, width=250, anchor="center")
            else:
                self.medicine_info.column(col, width=100, anchor="center")

        middle_frame = tk.Frame(right_frame)
        middle_frame.pack(side="left", fill="both", expand=True, padx=5)

        middle2_frame = tk.Frame(middle_frame)
        middle2_frame.pack(side="left", fill="both", expand=True, padx=5)

        middle3_frame = tk.Frame(middle_frame)
        middle3_frame.pack(side="left", fill="both", expand=True, padx=5)

        btn_print = tk.Button(middle3_frame, text="Print", font=("Arial", 10, "bold"), width=15, command=self.print_prescription)
        btn_print.grid(row=0, column=3, padx=5, pady=5)
        btn_close = tk.Button(middle3_frame, text="Close", font=("Arial", 10, "bold"), width=15, command=self.close)
        btn_close.grid(row=0, column=4, padx=5, pady=5)

        self.disease = ttk.Treeview(middle2_frame, columns=("Disease",), show="headings", height=1)
        self.disease.grid(row=0,column=0, padx=5, pady=5)
        self.disease.heading("Disease", text="Disease")
        self.disease.column("Disease", width=300, anchor="center")

        self.ingredients = ttk.Treeview(middle3_frame, columns=("Ingredients",), show="headings", height=1)
        self.ingredients.grid(row=0,column=1, padx=5, pady=5)
        self.ingredients.heading("Ingredients", text="Ingredients")
        self.ingredients.column("Ingredients", width=300, anchor="center")

        self.load_data()

    def load_data(self):
        # Populate Patient Tree
        if self.patient_data:
            self.patient_tree.insert("", "end", values=(
                self.patient_data.get("patientid", ""),
                self.patient_data.get("patientname", ""),
                self.patient_data.get("address1", ""),
                "Consultation",
                self.doctor_var.get()
            ))

        try:
            conn = self.get_db_connection()
            c = conn.cursor()

            # Doctors
            c.execute("SELECT First_Name, Last_Name FROM Doctors")
            docs = c.fetchall()
            doc_list = []
            for d in docs:
                fname = (d[0] or "").strip()
                lname = (d[1] or "").strip()
                full_name = f"{fname} {lname}".strip()
                if full_name:
                    if not full_name.lower().startswith("dr.") and not full_name.lower().startswith("dr "):
                        full_name = f"Dr. {full_name}"
                    if full_name not in doc_list:
                        doc_list.append(full_name)
            if doc_list:
                self.doctor_combo['values'] = doc_list
                self.doctor_combo.current(0)
            
            # Categories (Medicines)
            c.execute("SELECT DISTINCT Category FROM Medicines WHERE Category IS NOT NULL AND Category != ''")
            categories = c.fetchall()
            for cat in categories:
                self.category_tree.insert("", "end", values=(cat[0],))

            # Types (Medicines)
            try:
                c.execute("SELECT DISTINCT Type FROM Medicines WHERE Type IS NOT NULL AND Type != ''")
                types = c.fetchall()
                for t in types:
                    self.med_type.insert("", "end", values=(t[0],))
            except sqlite3.Error:
                pass

            # Initial Medicine Tree Load (All Medicines)
            c.execute("SELECT Product_Name, Brand_Name, Strength, Dosage, Frequency, Rate, Duration, Ingredients FROM Medicines")
            all_meds = c.fetchall()
            for med in all_meds:
                self.medicine_tree.insert("", "end", values=med)

            # Allergies
            c.execute("SELECT Allergic_Medicine FROM Allergies")
            allergies_list = c.fetchall()
            for al in allergies_list:
                self.allergies.insert("", "end", values=(al[0],))

            # Diseases
            c.execute("SELECT Disease FROM Diseases")
            diseases = c.fetchall()
            for dis in diseases:
                self.disease.insert("", "end", values=(dis[0],))
            
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading data: {e}")

    def on_category_select(self, event):
        selected = self.category_tree.selection()
        if not selected:
            return
        category = self.category_tree.item(selected[0])['values'][0]
        
        # Clear existing medicine tree
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)

        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("SELECT Product_Name, Brand_Name, Strength, Dosage, Frequency, Rate, Duration, Ingredients FROM Medicines WHERE Category=?", (category,))
            meds = c.fetchall()
            for med in meds:
                self.medicine_tree.insert("", "end", values=med)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading medicines: {e}")

    def on_med_type_select(self, event):
        selected = self.med_type.selection()
        if not selected:
            return
        mtype = self.med_type.item(selected[0])['values'][0]
        
        # Clear existing medicine tree
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)

        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("SELECT Product_Name, Brand_Name, Strength, Dosage, Frequency, Rate, Duration, Ingredients FROM Medicines WHERE Type=?", (mtype,))
            meds = c.fetchall()
            for med in meds:
                self.medicine_tree.insert("", "end", values=med)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading medicines: {e}")

    def on_medicine_double_click(self, event):
        selected = self.medicine_tree.selection()
        if not selected:
            return
        med_values = self.medicine_tree.item(selected[0])['values']
        
        # ("SortNo", "Medicine", "Sales Rate", "Nos", "Amount", "Remark")
        sort_no = len(self.medicine_info.get_children()) + 1
        medicine_name = f"{med_values[0]} ({med_values[1]}) - {med_values[2]}"
        sales_rate = med_values[5]
        nos = 1 # Default 1
        amount = sales_rate * nos
        remark = f"{med_values[3]} {med_values[4]} for {med_values[6]}"

        self.medicine_info.insert("", "end", values=(sort_no, medicine_name, sales_rate, nos, amount, remark))

    def print_prescription(self):
        if not self.medicine_info.get_children():
            messagebox.showwarning("Warning", "No medicines added to the prescription.")
            return
            
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            
            patient_id = self.patient_data.get("patientid", "Unknown")
            doctor_name = self.doctor_var.get()
            
            # Simple notes string from medicines
            notes = ""
            for item in self.medicine_info.get_children():
                val = self.medicine_info.item(item)['values']
                notes += f"{val[1]} - {val[5]}; "
                
            c.execute("INSERT INTO Prescriptions (Date, Patient_ID, Doctor_Name, Notes) VALUES (date('now'), ?, ?, ?)",
                      (patient_id, doctor_name, notes))
            conn.commit()
            conn.close()
            
            # Generate Plain Prescription PDF directly (only PDF)
            from letter_paper import Letter_Paper
            lp = Letter_Paper(self.app)
            lp.patient_data = getattr(self, 'patient_data', {})
            pdf_path = lp.Plain_Priscription_PDF_only()
            
            messagebox.showinfo("Success", f"Prescription saved and PDF generated successfully:\n{pdf_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving/printing prescription: {e}")
    
    def load_medicine_edit_data(self):
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            
            # Ensure optional columns exist in Medicines table
            try:
                c.execute("ALTER TABLE Medicines ADD COLUMN Type TEXT")
            except sqlite3.Error:
                pass
            try:
                c.execute("ALTER TABLE Medicines ADD COLUMN Contra_Indications TEXT")
            except sqlite3.Error:
                pass
            conn.commit()

            for tree in [self.med_tree_cat, self.med_tree_type, self.med_tree_ing, self.med_tree_contra]:
                for item in tree.get_children():
                    tree.delete(item)
            if hasattr(self, 'product_tree'):
                for item in self.product_tree.get_children():
                    self.product_tree.delete(item)

            c.execute("SELECT DISTINCT Category FROM Medicines WHERE Category IS NOT NULL AND Category != ''")
            for cat in c.fetchall():
                self.med_tree_cat.insert("", "end", values=(cat[0],))
                
            c.execute("SELECT DISTINCT Ingredients FROM Medicines WHERE Ingredients IS NOT NULL AND Ingredients != ''")
            for ing in c.fetchall():
                self.med_tree_ing.insert("", "end", values=(ing[0],))

            c.execute("SELECT DISTINCT Type FROM Medicines WHERE Type IS NOT NULL AND Type != ''")
            for t in c.fetchall():
                self.med_tree_type.insert("", "end", values=(t[0],))

            c.execute("SELECT DISTINCT Contra_Indications FROM Medicines WHERE Contra_Indications IS NOT NULL AND Contra_Indications != ''")
            for ci in c.fetchall():
                self.med_tree_contra.insert("", "end", values=(ci[0],))

            if hasattr(self, 'product_tree'):
                try:
                    c.execute("SELECT Category, Type, Product_Name, Brand_Name, Strength, Dosage, Frequency, Rate, Duration, Ingredients, Contra_Indications FROM Medicines")
                    for row in c.fetchall():
                        self.product_tree.insert("", "end", values=row)
                except sqlite3.Error:
                    pass
                
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading edit lists: {e}")

    def filter_product_tree(self, col_idx, search_val):
        if not hasattr(self, 'product_tree'):
            return
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            for item in self.product_tree.get_children():
                self.product_tree.delete(item)
            
            c.execute("SELECT Category, Type, Product_Name, Brand_Name, Strength, Dosage, Frequency, Rate, Duration, Ingredients, Contra_Indications FROM Medicines")
            for row in c.fetchall():
                val_at_col = str(row[col_idx] if row[col_idx] is not None else "").strip()
                if search_val.lower() in val_at_col.lower():
                    self.product_tree.insert("", "end", values=row)
            conn.close()
        except sqlite3.Error:
            pass

    def on_edit_cat_select(self, event):
        selected = self.med_tree_cat.selection()
        if not selected:
            return
        cat_val = self.med_tree_cat.item(selected[0])['values'][0]
        self.cat_var.set(cat_val)
        self.filter_product_tree(0, str(cat_val))

    def on_edit_type_select(self, event):
        selected = self.med_tree_type.selection()
        if not selected:
            return
        type_val = self.med_tree_type.item(selected[0])['values'][0]
        self.type_var.set(type_val)
        self.filter_product_tree(1, str(type_val))

    def on_edit_ing_select(self, event):
        selected = self.med_tree_ing.selection()
        if not selected:
            return
        ing_val = self.med_tree_ing.item(selected[0])['values'][0]
        self.ing_var.set(ing_val)
        self.filter_product_tree(9, str(ing_val))

    def on_edit_contra_select(self, event):
        selected = self.med_tree_contra.selection()
        if not selected:
            return
        contra_val = self.med_tree_contra.item(selected[0])['values'][0]
        self.comment_var.set(contra_val)
        self.filter_product_tree(10, str(contra_val))

    def on_product_tree_select(self, event):
        selected = self.product_tree.selection()
        if not selected:
            return
        vals = self.product_tree.item(selected[0])['values']
        if len(vals) >= 1:
            self.cat_var.set(vals[0] if vals[0] is not None else "")
        if len(vals) >= 2:
            self.type_var.set(vals[1] if vals[1] is not None else "")
        if len(vals) >= 3:
            self.prod_var.set(vals[2] if vals[2] is not None else "")
        if len(vals) >= 4:
            self.brand_var.set(vals[3] if vals[3] is not None else "")
        if len(vals) >= 5:
            self.strength_var.set(vals[4] if vals[4] is not None else "")
        if len(vals) >= 6:
            self.dosage_var.set(vals[5] if vals[5] is not None else "")
        if len(vals) >= 8:
            self.rate_var.set(vals[7] if vals[7] is not None else "")
        if len(vals) >= 10:
            self.ing_var.set(vals[9] if vals[9] is not None else "")
        if len(vals) >= 11:
            self.comment_var.set(vals[10] if vals[10] is not None else "")

    def add_category(self):
        category = self.cat_var.get()
        prod = self.prod_var.get()
        brand = self.brand_var.get()
        strength = self.strength_var.get()
        dosage = self.dosage_var.get()
        rate = self.rate_var.get()
        ing = self.ing_var.get()
        mtype = self.type_var.get()
        comment = self.comment_var.get()
        
        if not category or not prod:
            messagebox.showwarning("Warning", "Category and Product Name are required!")
            return
            
        try:
            rate_val = float(rate) if rate else 0.0
            conn = self.get_db_connection()
            c = conn.cursor()

            # Ensure optional columns exist
            try:
                c.execute("ALTER TABLE Medicines ADD COLUMN Type TEXT")
            except sqlite3.Error:
                pass
            try:
                c.execute("ALTER TABLE Medicines ADD COLUMN Contra_Indications TEXT")
            except sqlite3.Error:
                pass
            conn.commit()

            c.execute("""
                INSERT INTO Medicines (Category, Type, Product_Name, Brand_Name, Strength, Dosage, Frequency, Rate, Duration, Ingredients, Contra_Indications)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (category, mtype, prod, brand, strength, dosage, "Daily", rate_val, "1 week", ing, comment))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Medicine added successfully!")
            
            # Clear form entries
            self.cat_var.set("")
            self.type_var.set("")
            self.prod_var.set("")
            self.brand_var.set("")
            self.strength_var.set("")
            self.dosage_var.set("")
            self.rate_var.set("")
            self.ing_var.set("")
            self.comment_var.set("")
            
            # Refresh all trees
            self.load_medicine_edit_data()
            
        except ValueError:
            messagebox.showerror("Error", "Rate must be a number.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving medicine: {e}")
            
    def edit_medicine(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        top_frame = tk.Frame(self.app.workspace)
        top_frame.pack(side="top", fill="x", padx=5, pady=5)

        left_frame = tk.Frame(top_frame)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)

        right_frame = tk.Frame(top_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        bottom_frame = tk.LabelFrame(self.app.workspace, text="Medicine Inventory List", font=("Arial", 10, "bold"))
        bottom_frame.pack(side="bottom", fill="both", expand=True, padx=5, pady=5)

        # Variables for form
        self.cat_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.prod_var = tk.StringVar()
        self.brand_var = tk.StringVar()
        self.strength_var = tk.StringVar()
        self.dosage_var = tk.StringVar()
        self.rate_var = tk.StringVar()
        self.ing_var = tk.StringVar()
        self.comment_var = tk.StringVar()

        tk.Label(left_frame,text="Category",font=("Arial", 10, "bold")).grid(row=0,column=0,padx=5,pady=5)
        tk.Entry(left_frame,textvariable=self.cat_var, width=20).grid(row=0,column=1,padx=5,pady=5)
        
        tk.Label(left_frame,text="Type",font=("Arial",10,"bold")).grid(row=1,column=0,padx=5,pady=5)
        tk.Entry(left_frame,textvariable=self.type_var, width=20).grid(row=1,column=1,padx=5,pady=5)
        
        tk.Label(left_frame,text="Product Name",font=("Arial",10,"bold")).grid(row=2,column=0,padx=5,pady=5)
        tk.Entry(left_frame,textvariable=self.prod_var, width=20).grid(row=2,column=1,padx=5,pady=5)
        
        tk.Label(left_frame,text="Brand Name",font=("Arial",10,"bold")).grid(row=3,column=0,padx=5,pady=5)
        tk.Entry(left_frame,textvariable=self.brand_var, width=20).grid(row=3,column=1,padx=5,pady=5)
        
        tk.Label(left_frame,text="Strength",font=("Arial",10,"bold")).grid(row=4,column=0,padx=5,pady=5)
        tk.Entry(left_frame,textvariable=self.strength_var, width=20).grid(row=4,column=1,padx=5,pady=5)
        
        tk.Label(left_frame,text="Dosage",font=("Arial",10,"bold")).grid(row=5,column=0,padx=5,pady=5)
        tk.Entry(left_frame,textvariable=self.dosage_var, width=20).grid(row=5,column=1,padx=5,pady=5)
        
        tk.Label(left_frame,text="Rate",font=("Arial",10,"bold")).grid(row=6,column=0,padx=5,pady=5)
        tk.Entry(left_frame,textvariable=self.rate_var, width=20).grid(row=6,column=1,padx=5,pady=5)
        
        tk.Label(left_frame,text="Ingredients",font=("Arial",10,"bold")).grid(row=7,column=0,padx=5,pady=5)
        tk.Entry(left_frame,textvariable=self.ing_var, width=20).grid(row=7,column=1,padx=5,pady=5)
        
        tk.Label(left_frame,text="Comments",font=("Arial",10,"bold")).grid(row=8,column=0,padx=5,pady=5)
        tk.Entry(left_frame,textvariable=self.comment_var, width=20).grid(row=8,column=1,padx=5,pady=5)

        btn_add = tk.Button(left_frame, text="Add Category", font=("Arial", 10, "bold"), width=15, command=self.add_category)
        btn_add.grid(row=9,column=0,padx=5,pady=5)

        btn_close = tk.Button(left_frame, text="Close", font=("Arial", 10, "bold"), width=15, command=self.close)
        btn_close.grid(row=9,column=1,padx=5,pady=5)

        self.med_tree_cat = ttk.Treeview(right_frame,columns=("Category",),show="headings", height=4)
        self.med_tree_cat.grid(row=0,column=0,padx=5,pady=5, sticky="ew")
        self.med_tree_cat.heading("Category", text="Category")

        self.med_tree_type = ttk.Treeview(right_frame, columns=("Type",), show="headings", height=4)
        self.med_tree_type.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.med_tree_type.heading("Type", text="Type")
        self.med_tree_type.column("Type", width=300, anchor="center")  

        self.med_tree_ing = ttk.Treeview(right_frame, columns=("Ingredients",), show="headings", height=4)
        self.med_tree_ing.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.med_tree_ing.heading("Ingredients", text="Ingredients")
        self.med_tree_ing.column("Ingredients", width=300, anchor="center") 

        self.med_tree_contra = ttk.Treeview(right_frame, columns=("Contra Indications",), show="headings", height=4)
        self.med_tree_contra.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.med_tree_contra.heading("Contra Indications", text="Contra Indications")
        self.med_tree_contra.column("Contra Indications", width=300, anchor="center")

        columns = ("Category", "Type", "Product Name", "Brand Name", "Strength", "Dosage", "Rate", "Duration", "Ingredients", "Contra Indications")
        self.product_tree = ttk.Treeview(bottom_frame, columns=columns, show="headings")
        
        prod_vsb = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.product_tree.yview)
        prod_hsb = ttk.Scrollbar(bottom_frame, orient="horizontal", command=self.product_tree.xview)
        self.product_tree.configure(yscrollcommand=prod_vsb.set, xscrollcommand=prod_hsb.set)

        prod_vsb.pack(side="right", fill="y")
        prod_hsb.pack(side="bottom", fill="x")
        self.product_tree.pack(side="left", fill="both", expand=True)

        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=110, anchor="center")

        self.med_tree_cat.bind("<<TreeviewSelect>>", self.on_edit_cat_select)
        self.med_tree_type.bind("<<TreeviewSelect>>", self.on_edit_type_select)
        self.med_tree_ing.bind("<<TreeviewSelect>>", self.on_edit_ing_select)
        self.med_tree_contra.bind("<<TreeviewSelect>>", self.on_edit_contra_select)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_tree_select)

        self.load_medicine_edit_data()

    def close(self):
        try:
            from bill import Bill
            b = Bill(self.app)
            b.patient_data = getattr(self, 'patient_data', {})
            b.bill()
        except Exception:
            if hasattr(self.app, 'registration'):
                self.app.registration()
            elif hasattr(self.app, 'clear_workspace'):
                self.app.clear_workspace()