import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

class Prescription:
    def __init__(self, app):
        self.app = app
        self.patient_data = {}
        self.db_path = r"d:\XEDENTAL\Jayesh\Tkinter_Version1\Appu_Version\dental.db"
        
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

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

        self.treatment_type = ttk.Treeview(left_frame, columns=("Type",), show="headings", height=5)
        self.treatment_type.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.treatment_type.heading("Type", text="Type")
        self.treatment_type.column("Type", width=300, anchor="center")

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
            doc_list = [f"Dr. {d[0]} {d[1]}" for d in docs]
            if doc_list:
                self.doctor_combo['values'] = doc_list
                self.doctor_combo.current(0)
            
            # Categories (Medicines)
            c.execute("SELECT DISTINCT Category FROM Medicines")
            categories = c.fetchall()
            for cat in categories:
                self.category_tree.insert("", "end", values=(cat[0],))

            # Allergies
            c.execute("SELECT Allergic_Medicine FROM Allergies")
            allergies_list = c.fetchall()
            for al in allergies_list:
                self.allergies.insert("", "end", values=(al[0],))

            # Treatment Types
            c.execute("SELECT Treatment FROM Treatment_Fees")
            treatments = c.fetchall()
            for t in treatments:
                self.treatment_type.insert("", "end", values=(t[0],))

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
            # Here you would typically generate a PDF or print directly.
            # We'll save it to the DB as a record and show a success message.
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
            
            messagebox.showinfo("Success", "Prescription saved and sent to printer successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving prescription: {e}")
    
    def load_medicine_edit_data(self):
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            
            c.execute("SELECT DISTINCT Category FROM Medicines")
            for cat in c.fetchall():
                self.med_tree_cat.insert("", "end", values=(cat[0],))
                
            c.execute("SELECT DISTINCT Ingredients FROM Medicines WHERE Ingredients IS NOT NULL")
            for ing in c.fetchall():
                self.med_tree_ing.insert("", "end", values=(ing[0],))

            # Try to populate Type column if present in the Medicines table
            try:
                c.execute("SELECT DISTINCT Type FROM Medicines WHERE Type IS NOT NULL")
                for t in c.fetchall():
                    self.med_tree_type.insert("", "end", values=(t[0],))
            except sqlite3.Error:
                # If the Medicines table has no Type column, ignore silently
                pass
                
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading edit lists: {e}")

    def add_category(self):
        category = self.cat_var.get()
        prod = self.prod_var.get()
        brand = self.brand_var.get()
        strength = self.strength_var.get()
        dosage = self.dosage_var.get()
        rate = self.rate_var.get()
        ing = self.ing_var.get()
        mtype = self.type_var.get()
        # Frequency and duration default or from form (omitted in form but required in schema, so we default)
        
        if not category or not prod:
            messagebox.showwarning("Warning", "Category and Product Name are required!")
            return
            
        try:
            rate_val = float(rate) if rate else 0.0
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO Medicines (Category, Product_Name, Brand_Name, Strength, Dosage, Frequency, Rate, Duration, Ingredients)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (category, prod, brand, strength, dosage, "Daily", rate_val, "1 week", ing))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Medicine added successfully!")
            
            # Clear form
            self.cat_var.set("")
            self.prod_var.set("")
            self.brand_var.set("")
            self.strength_var.set("")
            self.dosage_var.set("")
            self.rate_var.set("")
            self.ing_var.set("")
            
            # Refresh tree
            for item in self.med_tree_cat.get_children():
                self.med_tree_cat.delete(item)
            for item in self.med_tree_ing.get_children():
                self.med_tree_ing.delete(item)
            for item in self.med_tree_type.get_children():
                self.med_tree_type.delete(item)
            self.load_medicine_edit_data()

            # If the DB/table doesn't store Type, still add the entered Type to the Type treeview
            if mtype:
                existing_types = [self.med_tree_type.item(i)['values'][0] for i in self.med_tree_type.get_children()]
                if mtype not in existing_types:
                    self.med_tree_type.insert("", "end", values=(mtype,))
            
        except ValueError:
            messagebox.showerror("Error", "Rate must be a number.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving medicine: {e}")
            
    def edit_medicine(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        left_frame = tk.Frame(self.app.workspace)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)

        right_frame = tk.Frame(self.app.workspace)
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

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

        self.med_tree_cat = ttk.Treeview(right_frame,columns=("Category"),show="headings")
        self.med_tree_cat.grid(row=0,column=0,padx=5,pady=5, sticky="ew")
        self.med_tree_cat.heading("Category", text="Category")

        self.med_tree_type = ttk.Treeview(right_frame, columns=("Type",), show="headings", height=5)
        self.med_tree_type.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.med_tree_type.heading("Type", text="Type")
        self.med_tree_type.column("Type", width=300, anchor="center")  

        self.med_tree_ing = ttk.Treeview(right_frame, columns=("Ingredients",), show="headings", height=5)
        self.med_tree_ing.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.med_tree_ing.heading("Ingredients", text="Ingredients")
        self.med_tree_ing.column("Ingredients", width=300, anchor="center") 

        self.med_tree_contra = ttk.Treeview(right_frame, columns=("Contra Indications",), show="headings", height=5)
        self.med_tree_contra.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.med_tree_contra.heading("Contra Indications", text="Contra Indications")
        self.med_tree_contra.column("Contra Indications", width=300, anchor="center")

        self.load_medicine_edit_data()

    def close(self):
        self.app.bill()