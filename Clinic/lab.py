import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk


def get_db_connection(app=None):
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))


def init_db(app=None):
    try:
        conn = get_db_connection(app)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Lab_Work (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patientid TEXT,
                regno TEXT,
                patientname TEXT,
                lab_name TEXT,
                work_type TEXT,
                tooth_no TEXT,
                shade TEXT,
                sent_date TEXT,
                expected_date TEXT,
                received_date TEXT,
                cost REAL DEFAULT 0,
                status TEXT DEFAULT 'Sent',
                doctor TEXT,
                notes TEXT
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Labs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Lab_Name TEXT UNIQUE NOT NULL
            )
        """
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Database init error:", e)


class Lab:

    def __init__(self, app):
        self.app = app
        init_db(app)
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
            "email": "",
        }
        self.tooth_vars = {}
        self.coping_var = tk.IntVar(value=0)
        self.pontic_var = tk.IntVar(value=0)
        self.margin_vars = {}

        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        self.lab()

    def lab(self):
        # tk.Label(self.app.workspace, text="Lab Work Order & Tracking", font=("Arial", 12, "bold")).pack(pady=2)

        content_frame = tk.Frame(self.app.workspace)
        content_frame.pack(pady=5, fill="both", expand=True)

        # Left Column Frame (Patient Details & Patient Work Register)
        self.patient = tk.LabelFrame(
            content_frame, text="Patient Details", font=("Arial", 10, "bold")
        )
        self.patient.pack(side="left", fill="y", padx=(5, 5))

        # Middle Column Frame (Work Items, Dates, Specifications)
        middle_frame = tk.Frame(content_frame)
        middle_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Right Column Frame (Tooth Chart, Coping, Pontic, Stains, Margins, Comments)
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # ---------------- PATIENT DETAILS FIELDS ----------------
        # Row 0: Patient ID & Reg No
        self.bill_patientid = tk.Entry(self.patient, justify="center", width=14)
        self.bill_patientid.grid(row=0, column=0, padx=5, pady=2)
        self.bill_patientid.bind("<Return>", lambda e: self.search_patient())

        self.bill_regno = tk.Entry(self.patient, justify="center", width=14)
        self.bill_regno.grid(row=0, column=1, padx=5, pady=2)

        # Row 1: Patient Name & Address 1
        self.bill_patientname = tk.Entry(self.patient, justify="center", width=14)
        self.bill_patientname.grid(row=1, column=0, padx=5, pady=2)

        self.bill_address1 = tk.Entry(self.patient, justify="center", width=14)
        self.bill_address1.grid(row=1, column=1, padx=5, pady=2)

        # Row 2: Address 2
        self.bill_address2 = tk.Entry(self.patient, width=30)
        self.bill_address2.grid(
            row=2, column=0, columnspan=2, padx=5, pady=2, sticky="we"
        )

        # Row 3-4: Age & Sex
        tk.Label(self.patient, text="Age:", font=("Arial", 9, "bold")).grid(
            row=3, column=0, sticky="w", padx=5
        )
        tk.Label(self.patient, text="Sex:", font=("Arial", 9, "bold")).grid(
            row=3, column=1, sticky="w", padx=2
        )

        self.bill_age = tk.Entry(self.patient, width=6)
        self.bill_age.grid(row=4, column=0, sticky="w", padx=5)

        self.bill_gender = ttk.Combobox(
            self.patient, values=["Male", "Female"], state="readonly", width=8
        )
        self.bill_gender.grid(row=4, column=1, sticky="w", padx=2)

        # Row 5: Phone Numbers
        self.bill_office = tk.Entry(self.patient, width=14)
        self.bill_office.grid(row=5, column=0, padx=5, pady=2, sticky="w")

        self.bill_residence = tk.Entry(self.patient, width=14)
        self.bill_residence.grid(row=5, column=1, padx=2, pady=2, sticky="w")

        # Row 6: Email
        self.bill_email = tk.Entry(self.patient, width=30)
        self.bill_email.grid(
            row=6, column=0, columnspan=2, padx=5, pady=2, sticky="we"
        )

        # Populate patient details fields
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

        # ---------------- Patient Work Register ----------------
        pat_list_lf = tk.LabelFrame(self.patient, text=" Patient Work Register ",)
        pat_list_lf.grid(row=8, column=0, columnspan=2, sticky="nsew", padx=4, pady=5)

        history_tree = ttk.Treeview(
            pat_list_lf, columns=["id", "name", "address"], show="headings", height=6
        )
        self.history_tree = history_tree
        self.pat_tree = history_tree
        history_tree.heading("id", text="Patient id")
        history_tree.heading("name", text="Patient Name")
        history_tree.heading("address", text="Address")
        history_tree.column("id", width=60)
        history_tree.column("name", width=140)
        history_tree.column("address", width=140)
        history_tree.pack(fill="both", expand=True, padx=2, pady=2) 
        history_tree.bind("<Double-1>", self.on_patient_work_select)
        history_tree.bind("<<TreeviewSelect>>", self.on_patient_work_select)

        comm_frame = tk.LabelFrame(self.patient, text=" Comments ")
        comm_frame.grid(row=9, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.txt_comments = tk.Text(comm_frame, width=18, height=10, font=("Tahoma", 8))
        self.txt_comments.pack(fill="both", expand=True, padx=2, pady=2)

        # ---------------- MIDDLE FRAME COMPONENTS ----------------
        # 1. Dates & Lab Name
        date_frame = tk.Frame(middle_frame)
        date_frame.pack(fill="x", padx=2, pady=2)

        tk.Label(date_frame, text="Despatch Date:").grid(row=0, column=0, sticky="w", padx=2)
        self.entry_despatch_date = tk.Entry(date_frame, width=12)
        self.entry_despatch_date.grid(row=0, column=1, padx=4, pady=2)
        self.entry_despatch_date.insert(
            0, datetime.today().strftime("%d-%m-%Y")
        )

        tk.Label(date_frame, text="Delivery Date:").grid(row=0, column=2, sticky="w", padx=4)
        self.entry_delivery_date = tk.Entry(date_frame, width=12)
        self.entry_delivery_date.grid(row=0, column=3, padx=4, pady=2)

        tk.Label(date_frame, text="Lab Name:").grid(row=1, column=0, sticky="w", padx=2)
        labs_list = self.get_dropdown_data("Labs", "Lab_Name") or [
            "Grace Dental Lab",
            "Anupam Lab",
        ]
        self.cb_lab_name = ttk.Combobox(
            date_frame, values=labs_list, width=14
        )
        self.cb_lab_name.grid(row=1, column=1, padx=4, pady=2)
        if labs_list:
            self.cb_lab_name.set(labs_list[0])

        tk.Label(date_frame, text="Find Name:").grid(row=1, column=2, sticky="w", padx=4)
        self.entry_find_name = tk.Entry(date_frame, width=12)
        self.entry_find_name.grid(row=1, column=3, padx=4, pady=2)

        tk.Button(
            date_frame,
            text="Find",
            width=8,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold"),
            command=self.find_lab,
        ).grid(row=1, column=4, padx=4, pady=2)

        # 2. Work Items Table
        work_lf = tk.LabelFrame(middle_frame, text=" Work Items ")
        work_lf.pack(fill="x", padx=2, pady=4)

        self.work_table = ttk.Treeview(
            work_lf,
            columns=("type", "tooth", "units"),
            show="headings",
            height=4,
        )
        self.work_table.heading("type", text="Type Of Work")
        self.work_table.heading("tooth", text="Tooth No")
        self.work_table.heading("units", text="Units")
        self.work_table.column("type", width=120)
        self.work_table.column("tooth", width=80)
        self.work_table.column("units", width=50, anchor="center")
        self.work_table.pack(fill="x", padx=2, pady=2)

        tk.Button(
            work_lf,
            text="Add New Work and Details",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            command=self.add_work_item,
        ).pack(pady=3)

        # 3. Specifications Frame
        specs_frame = tk.Frame(middle_frame)
        specs_frame.pack(fill="both", expand=True, padx=2, pady=2)

        row1 = tk.Frame(specs_frame)
        row1.pack(anchor="w", pady=2)
        tk.Label(row1, text="Tooth:").pack(side="left")
        self.entry_tooth_single = tk.Entry(row1, width=8)
        self.entry_tooth_single.pack(side="left", padx=2)
        tk.Label(row1, text="Rate:").pack(side="left", padx=4)
        self.entry_rate = tk.Entry(row1, width=8)
        self.entry_rate.pack(side="left")
        self.entry_rate.insert(0, "0.00")

        row2 = tk.Frame(specs_frame)
        row2.pack(anchor="w", pady=2)
        tk.Label(row2, text="MaterialType:").pack(side="left")
        self.cb_material_type = ttk.Combobox(
            row2,
            values=["PFM", "Zirconia", "Ceramic", "Acrylic", "Metal"],
            width=18,
        )
        self.cb_material_type.pack(side="left", padx=2)

        shade_box = tk.LabelFrame(specs_frame,text=" Work / Shade / Material Specifications ")
        shade_box.pack(anchor="w", fill="x", pady=4)

        self.shade_combos = {}
        labels = ["Cervical", "Middle", "Internal"]
        shades_data = self.get_dropdown_data("Shades", "Shade") or [
            "A1",
            "A2",
            "A3",
            "B1",
            "B2",
            "C1",
            "D2",
        ]
        for idx, lbl in enumerate(labels):
            r = tk.Frame(shade_box)
            r.pack(fill="x", pady=1)
            tk.Label(r, text=lbl, width=8, anchor="w").pack(side="left")
            c1 = ttk.Combobox(r, values=shades_data, width=8)
            c1.pack(side="left", padx=2)
            c2 = ttk.Combobox(r, values=shades_data, width=8)
            c2.pack(side="left", padx=2)
            c3 = ttk.Combobox(r, values=shades_data, width=8)
            c3.pack(side="left", padx=2)
            self.shade_combos[lbl] = (c1, c2, c3)

        # Extra Specs Sub-Rows
        extra_row1 = tk.Frame(specs_frame)
        extra_row1.pack(anchor="w", pady=2)

        tk.Label(extra_row1, text="Despatch Mode:").pack(side="left")
        self.cb_despatch_mode = ttk.Combobox(
            extra_row1, values=["Courier", "Hand Delivery", "Post"], width=10
        )
        self.cb_despatch_mode.pack(side="left", padx=(2, 6))

        tk.Label(extra_row1, text="Die:").pack(side="left")
        self.cb_die = ttk.Combobox(
            extra_row1, values=["Included", "NotIncluded"], width=10
        )
        self.cb_die.pack(side="left", padx=(2, 6))

        tk.Label(extra_row1, text="Cast:").pack(side="left")
        self.cb_cast = ttk.Combobox(
            extra_row1, values=["Included", "NotIncluded"], width=10
        )
        self.cb_cast.pack(side="left", padx=2)

        extra_row2 = tk.Frame(specs_frame)
        extra_row2.pack(anchor="w", pady=2)

        tk.Label(extra_row2, text="Individual / Splinted:", fg="#003366").pack(side="left")
        self.cb_splinted = ttk.Combobox(extra_row2, values=["Individual", "Splinted"], width=18)
        self.cb_splinted.pack(side="left", padx=4)

        extra_row3 = tk.Frame(specs_frame)
        extra_row3.pack(anchor="w", pady=2)

        tk.Label(extra_row3, text="Shade Enclosed:", fg="#003366").pack(side="left")
        self.cb_shade_enclosed = ttk.Combobox(extra_row3, values=["Yes", "No"], width=10)
        self.cb_shade_enclosed.pack(side="left", padx=(4, 10))

        tk.Label(extra_row3, text="If no occlusal clearance:", fg="#003366").pack(side="left")
        self.cb_occlusal = ttk.Combobox(extra_row3, values=["Reduce Opposing", "Reduce Preparation", "Make Metal Occlusal"], width=18)
        self.cb_occlusal.pack(side="left", padx=4)

        extra_row4 = tk.Frame(specs_frame)
        extra_row4.pack(anchor="w", pady=2)

        tk.Label(extra_row4, text="Total Amount:", fg="#003366", font=("Tahoma", 8, "bold")).pack(side="left")
        self.entry_total = tk.Entry(extra_row4, width=10, justify="right", font=("Tahoma", 8, "bold"))
        self.entry_total.insert(0, "0.00")
        self.entry_total.pack(side="left", padx=4)

        # ---------------- RIGHT FRAME COMPONENTS ----------------
        # 1. Tooth Chart Selection
        tooth_frame = tk.LabelFrame(
            right_frame,
            text=" Tooth Chart Selection ",
            font=("Tahoma", 8, "bold"),
        )
        tooth_frame.pack(fill="x", padx=2, pady=2)

        grid_container = tk.Frame(tooth_frame)
        grid_container.pack(pady=4)

        quad_1 = ["18", "17", "16", "15", "14", "13", "12", "11"]
        quad_2 = ["21", "22", "23", "24", "25", "26", "27", "28"]
        quad_4 = ["48", "47", "46", "45", "44", "43", "42", "41"]
        quad_3 = ["31", "32", "33", "34", "35", "36", "37", "38"]

        for idx, t in enumerate(quad_1 + quad_2):
            col = idx if idx < 8 else idx + 1
            lbl = tk.Label(grid_container,text=t,font=("Tahoma", 7, "bold"))
            lbl.grid(row=0, column=col, padx=1)
            var = tk.BooleanVar()
            self.tooth_vars[t] = var
            cb = tk.Checkbutton(grid_container, variable=var)
            cb.grid(row=1, column=col, padx=1)

        tk.Frame(grid_container, height=2, bg="gray").grid(
            row=2, column=0, columnspan=17, sticky="we", pady=2
        )

        for idx, t in enumerate(quad_4 + quad_3):
            col = idx if idx < 8 else idx + 1
            var = tk.BooleanVar()
            self.tooth_vars[t] = var
            cb = tk.Checkbutton(grid_container, variable=var)
            cb.grid(row=3, column=col, padx=1)
            lbl = tk.Label(grid_container,text=t,font=("Tahoma", 7, "bold"))
            lbl.grid(row=4, column=col, padx=1)

        # 2. Coping & Pontic Design
        right_design_frame = tk.Frame(right_frame)
        right_design_frame.pack(fill="x", padx=2, pady=2)

        coping_lf = tk.LabelFrame(right_design_frame, text=" Coping Design (Please tick one) ", font=("Tahoma", 8, "bold"))
        coping_lf.pack(fill="x", pady=2)

        coping_opts = [
            (self.draw_full_porcelain_molar, "Full\nPorcelain\nCoverage"),
            (self.draw_lingual_metal_collar, "Lingual\nMetal\nCollar"),
            (self.draw_full_metal_occlusal, "Full Metal\nOcclusal\n(Veneer / Facing)"),
            (self.draw_full_porcelain_ant, "Full\nPorcelain\nCoverage"),
            (self.draw_metal_coverage_lingual, "Full Metal\nCoverage\nLingual")
        ]
        for c_idx, (draw_func, text) in enumerate(coping_opts):
            box = tk.Frame(coping_lf)
            box.grid(row=0, column=c_idx, padx=4, pady=2)
            tk.Radiobutton(
                box, variable=self.coping_var, value=c_idx
            ).pack()
            c = tk.Canvas(
                box,
                width=32,
                height=22,
                bg="white",
                highlightbackground="#808080",
                highlightthickness=1,
            )
            c.pack()
            draw_func(c)
            tk.Label(box,text=text,font=("Tahoma", 6),justify="center").pack()

        pontic_lf = tk.LabelFrame(right_design_frame, text=" Pontic Design (Please tick one) ", font=("Tahoma", 8, "bold"))
        pontic_lf.pack(fill="x", pady=4)

        pontic_opts = ["Sanitary", "Full Ridge", "Modified", "Bullet", "Ovate"]
        for p_idx, text in enumerate(pontic_opts):
            box = tk.Frame(pontic_lf)
            box.grid(row=0, column=p_idx, padx=6, pady=2)
            tk.Radiobutton(box, variable=self.pontic_var, value=p_idx).pack()
            c = tk.Canvas(box,width=32,height=22,bg="white",highlightbackground="#808080",highlightthickness=1,)    
            c.pack()
            c.create_oval(5, 5, 27, 17, fill="#FFFFE0", outline="brown")
            tk.Label(box,text=text,font=("Tahoma", 6),justify="center",).pack()

        # 3. Lower Right Grid (Stains, Shade Map, Margins, Comments)
        lower_right_frame = tk.Frame(right_frame)
        lower_right_frame.pack(fill="both", expand=True, padx=2, pady=2)

        stains_frame = tk.Frame(lower_right_frame)
        stains_frame.pack(side="left", padx=5)

        self.stain_combos = {}
        stain_fields = [
            "Stains Internal:",
            "Stains External:",
            "Translucency:",
            "Glaze:",
            "Waxbite:",
            "Texture:",
        ]
        for idx, field in enumerate(stain_fields):
            f = tk.Frame(stains_frame)
            f.pack(anchor="w", pady=1)
            tk.Label(f, text=field, width=12, anchor="e").pack(side="left")
            cb = ttk.Combobox(f, width=10)
            cb.pack(side="left", padx=2)
            self.stain_combos[field] = cb

        tooth_diagram_frame = tk.Frame(lower_right_frame)
        tooth_diagram_frame.pack(side="left", padx=5)

        # ----------------------------------------------------
        # 4. MIDDLE-RIGHT: Shade Tooth Grid Diagram
        # ----------------------------------------------------
        shade_diag_frame = tk.Frame(lower_right_frame, bg="#D6D3CE")
        shade_diag_frame.pack(side="left", padx=6, pady=2)

        tk.Label(shade_diag_frame, text="Shade", fg="blue", bg="#D6D3CE", font=("Tahoma", 8, "bold")).pack()
        c_shade = tk.Canvas(shade_diag_frame, width=70, height=130, bg="white", highlightthickness=1, highlightbackground="#808080")
        c_shade.pack(pady=2)

        # Drawing top and bottom tooth shade segment grids
        c_shade.create_rectangle(5, 5, 65, 60, outline="#B0B0B0")
        c_shade.create_line(25, 5, 25, 60, fill="#B0B0B0")
        c_shade.create_line(45, 5, 45, 60, fill="#B0B0B0")
        c_shade.create_line(5, 32, 65, 32, fill="#B0B0B0")
        c_shade.create_oval(8, 12, 62, 50, outline="#004080", width=2)

        c_shade.create_rectangle(5, 68, 65, 125, outline="#B0B0B0")
        c_shade.create_line(25, 68, 25, 125, fill="#B0B0B0")
        c_shade.create_line(45, 68, 45, 125, fill="#B0B0B0")
        c_shade.create_line(5, 96, 65, 96, fill="#B0B0B0")
        c_shade.create_oval(8, 75, 62, 118, outline="#004080", width=2)

        tk.Label(shade_diag_frame, text="Lingual", fg="#003366", bg="#D6D3CE", font=("Tahoma", 7)).pack()

        # ----------------------------------------------------
        # 5. RIGHT: Mamelons Selection Box
        # ----------------------------------------------------
        mamelons_frame = tk.Frame(lower_right_frame, bg="#D6D3CE")
        mamelons_frame.pack(side="left", padx=6, pady=2)

        tk.Label(mamelons_frame, text="Mamelons", fg="blue", bg="#D6D3CE", font=("Tahoma", 8, "bold")).pack()
        
        mam_box = tk.Frame(mamelons_frame, bg="white", highlightthickness=1, highlightbackground="#808080", padx=4, pady=4)
        mam_box.pack(pady=2)

        for i in range(3):
            item_row = tk.Frame(mam_box, bg="white")
            item_row.pack(pady=3)
            
            cb = tk.Checkbutton(item_row, bg="white")
            cb.pack(side="left")
            
            c_mam = tk.Canvas(item_row, width=28, height=32, bg="white", highlightthickness=0)
            c_mam.pack(side="left")
            # Drawing tooth outline with mamelon patterns
            c_mam.create_polygon(4, 28, 4, 10, 10, 4, 18, 4, 24, 10, 24, 28, fill="#F0F4F8", outline="black", width=1)
            if i == 0:
                c_mam.create_arc(4, 22, 24, 28, start=0, extent=-180, outline="black")
            elif i == 1:
                c_mam.create_line(6, 24, 14, 22, 22, 25, fill="black")
            elif i == 2:
                c_mam.create_line(4, 26, 9, 20, 14, 26, 19, 20, 24, 26, fill="black")

        tk.Label(mamelons_frame, text="Distal", fg="#003366", bg="#D6D3CE", font=("Tahoma", 7)).pack()

        margin_frame = tk.Frame(lower_right_frame)
        margin_frame.pack(side="left", padx=5)

        tk.Label(margin_frame,text="Margins:",font=("Tahoma", 7, "bold")).pack(anchor="w")
        for m in ["Labial", "Mesial", "Lingual", "Distal"]:
            f = tk.Frame(margin_frame)
            f.pack(anchor="w")
            var = tk.BooleanVar()
            self.margin_vars[m] = var
            tk.Checkbutton(f, variable=var).pack(side="left")
            tk.Label(f, text=m, font=("Tahoma", 7)).pack(side="left")

        # ---------------- BOTTOM ACTION BUTTONS ----------------
        btn_frame = tk.Frame(self.app.workspace, bd=1, relief="raised")
        btn_frame.pack(fill="x", side="bottom", pady=4)

        inner_btn_frame = tk.Frame(btn_frame)
        inner_btn_frame.pack(expand=True)

        buttons = [
            ("Save", self.on_save, "#4CAF50", "white"),
            ("Preview", self.on_preview, "#2196F3", "white"),
            ("Close", self.close_workspace, "#f44336", "white"),
            ("Add New Record", self.clear_all, "#FF9800", "white"),
            ("Add New Lab", self.add_new_lab, "#9C27B0", "white"),
        ]

        for text, cmd, bg_col, fg_col in buttons:
            b = tk.Button(
                inner_btn_frame,
                text=text,
                width=14,
                font=("Arial", 9, "bold"),
                bg=bg_col,
                fg=fg_col,
                command=cmd,
            )
            b.pack(side="left", padx=6, pady=4)

        self.load_patient_work_register()

        left_btn_frame = tk.Frame(self.patient, bg="#D6D3CE") 
        left_btn_frame.grid(row=10, column=0, columnspan=2, sticky="ew", padx=4, pady=5)

        btn_work = tk.Button(left_btn_frame, text="Work", width=9, height=1, font=("Tahoma", 8, "bold"), bg="#4CAF50", fg="white", relief="raised")
        btn_work.pack(side="left", padx=2, pady=2)

        btn_shade = tk.Button(left_btn_frame, text="Shade", width=9, height=1, font=("Tahoma", 8, "bold"), bg="#2196F3", fg="white", relief="raised")
        btn_shade.pack(side="left", padx=2, pady=2)

        btn_update = tk.Button(left_btn_frame, text="Update", width=9, height=1, font=("Tahoma", 8, "bold"), bg="#FF9800", fg="white", relief="raised")
        btn_update.pack(side="left", padx=2, pady=2)

        lbl_all = tk.Label(left_btn_frame, text="All", fg="red", bg="#D6D3CE", font=("Tahoma", 8))
        lbl_all.pack(side="left", padx=(8, 2), pady=2)

        cb_all = ttk.Combobox(left_btn_frame, width=8)
        cb_all.pack(side="left", padx=2, pady=2)

    # ---------------- HELPER METHODS ----------------
    def refresh_labs(self):
        labs_list = self.get_dropdown_data("Labs", "Lab_Name") or [
            "Grace Dental Lab",
            "Anupam Lab",
        ]
        if hasattr(self, "cb_lab_name"):
            self.cb_lab_name["values"] = labs_list
            if labs_list and not self.cb_lab_name.get():
                self.cb_lab_name.set(labs_list[0])

    def add_new_lab(self):
        win = tk.Toplevel(self.app.root)
        win.title("Lab Subform")
        win.transient(self.app.root)
        win.grab_set()
        width = 380
        height = 280
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(win, text="Lab Name :", font=('Arial', 11, 'bold')).grid(row=0, column=0, padx=5, pady=8, sticky="e")
        lab_name_entry = tk.Entry(win, width=20, font=('Arial', 10))
        lab_name_entry.grid(row=0, column=1, padx=5, pady=8, sticky="w")

        tree_frame = tk.Frame(win)
        tree_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=5)
        win.grid_rowconfigure(2, weight=1)
        win.grid_columnconfigure(0, weight=1)
        win.grid_columnconfigure(1, weight=1)

        columns = ('LabName',)
        lab_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=5)
        lab_tree.heading('LabName', text='Lab Name')
        lab_tree.column('LabName', width=260)
        lab_tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=lab_tree.yview)
        scroll.pack(side="right", fill="y")
        lab_tree.configure(yscrollcommand=scroll.set)

        def load_labs():
            for item in lab_tree.get_children():
                lab_tree.delete(item)
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS Labs (id INTEGER PRIMARY KEY AUTOINCREMENT, Lab_Name TEXT UNIQUE NOT NULL)")
                cursor.execute("SELECT Lab_Name FROM Labs")
                rows = cursor.fetchall()
                for row in rows:
                    lab_tree.insert("", "end", values=row)
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load labs: {e}")

        def save_lab():
            lab = lab_name_entry.get().strip()
            if lab == "":
                messagebox.showwarning("Warning", "Enter Lab Name")
                return
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS Labs (id INTEGER PRIMARY KEY AUTOINCREMENT, Lab_Name TEXT UNIQUE NOT NULL)")
                cursor.execute("INSERT INTO Labs (Lab_Name) VALUES (?)", (lab,))
                conn.commit()
                conn.close()
                load_labs()
                lab_name_entry.delete(0, tk.END)
                lab_name_entry.focus()
                self.refresh_labs()
                self.cb_lab_name.set(lab)
            except sqlite3.IntegrityError:
                messagebox.showwarning("Warning", "Lab Name already exists")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save lab: {e}")

        def clear_lab():
            lab_name_entry.delete(0, tk.END)
            lab_name_entry.focus()

        def on_close():
            self.refresh_labs()
            win.destroy()

        btn_frame = tk.Frame(win)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(btn_frame, text="Add", width=8, bg="#4CAF50", fg="white", font=("Arial", 8, "bold"), command=save_lab).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Clear", width=8, bg="#FF9800", fg="white", font=("Arial", 8, "bold"), command=clear_lab).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Close", width=8, bg="#f44336", fg="white", font=("Arial", 8, "bold"), command=on_close).pack(side="left", padx=4)

        win.protocol("WM_DELETE_WINDOW", on_close)
        lab_name_entry.focus()
        load_labs()

    # ---------------- COPING DRAWING HELPERS ----------------
    def draw_full_porcelain_molar(self, canvas):
        canvas.create_rectangle(4, 4, 28, 18, fill="#FFFFF0", outline="#004080", width=1)
        canvas.create_rectangle(8, 7, 24, 15, fill="#E6F2FF", outline="#004080", dash=(2, 2))

    def draw_lingual_metal_collar(self, canvas):
        canvas.create_rectangle(4, 4, 28, 14, fill="#FFFFF0", outline="#004080", width=1)
        canvas.create_rectangle(4, 14, 28, 18, fill="#708090", outline="#004080", width=1)

    def draw_full_metal_occlusal(self, canvas):
        canvas.create_rectangle(4, 4, 28, 9, fill="#708090", outline="#004080", width=1)
        canvas.create_rectangle(4, 9, 28, 18, fill="#FFFFF0", outline="#004080", width=1)

    def draw_full_porcelain_ant(self, canvas):
        canvas.create_polygon(8, 18, 5, 8, 16, 4, 27, 8, 24, 18, fill="#FFFFF0", outline="#004080", width=1)
        canvas.create_polygon(10, 16, 8, 9, 16, 6, 24, 9, 22, 16, fill="#E6F2FF", outline="#004080", dash=(2, 2))

    def draw_metal_coverage_lingual(self, canvas):
        canvas.create_rectangle(4, 4, 16, 18, fill="#708090", outline="#004080", width=1)
        canvas.create_rectangle(16, 4, 28, 18, fill="#FFFFF0", outline="#004080", width=1)

    def get_dropdown_data(self, table_name, column_name):
        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT {column_name} FROM {table_name}")
            rows = cursor.fetchall()
            conn.close()
            return [row[0] for row in rows if row[0]]
        except Exception:
            return []

    def search_patient(self):
        pid = self.bill_patientid.get().strip()
        regno = self.bill_regno.get().strip()
        name = self.bill_patientname.get().strip()

        if not pid and not regno and not name:
            messagebox.showwarning(
                "Warning", "Enter Patient ID, Reg No, or Name to search."
            )
            return

        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            row = None

            if pid:
                cursor.execute(
                    "SELECT * FROM Appointments WHERE id=? OR pid=?", (pid, pid)
                )
                row = cursor.fetchone()
            if not row and regno:
                cursor.execute(
                    "SELECT * FROM Appointments WHERE regno=?", (regno,)
                )
                row = cursor.fetchone()
            if not row and name:
                cursor.execute(
                    "SELECT * FROM Appointments WHERE name LIKE ?",
                    (f"%{name}%",),
                )
                row = cursor.fetchone()

            if not row:
                if pid:
                    cursor.execute(
                        "SELECT * FROM registration WHERE id=? OR pid=?",
                        (pid, pid),
                    )
                    row = cursor.fetchone()
                if not row and name:
                    cursor.execute(
                        "SELECT * FROM registration WHERE name LIKE ?",
                        (f"%{name}%",),
                    )
                    row = cursor.fetchone()

            conn.close()

            if row:
                self.clear_patient_fields()
                self.bill_patientid.insert(0, str(row[0]))
                if len(row) > 1 and row[1]:
                    self.bill_regno.insert(0, str(row[1]))
                if len(row) > 3 and row[3]:
                    self.bill_patientname.insert(0, str(row[3]))
                if len(row) > 4 and row[4]:
                    self.bill_age.insert(0, str(row[4]))
                if len(row) > 5 and row[5]:
                    self.bill_gender.set(str(row[5]))
                if len(row) > 6 and row[6]:
                    self.bill_office.insert(0, str(row[6]))
                if len(row) > 7 and row[7]:
                    self.bill_address1.insert(0, str(row[7]))
            else:
                messagebox.showinfo("Not Found", "No matching patient found.")
        except Exception as e:
            messagebox.showerror("Error", f"Patient search error: {str(e)}")

    def clear_patient_fields(self):
        self.bill_patientid.delete(0, tk.END)
        self.bill_regno.delete(0, tk.END)
        self.bill_patientname.delete(0, tk.END)
        self.bill_address1.delete(0, tk.END)
        self.bill_address2.delete(0, tk.END)
        self.bill_age.delete(0, tk.END)
        self.bill_gender.set("")
        self.bill_office.delete(0, tk.END)
        self.bill_residence.delete(0, tk.END)
        self.bill_email.delete(0, tk.END)

    def load_patient_work_register(self):
        tree = getattr(self, 'history_tree', getattr(self, 'pat_tree', None))
        if not tree:
            return
        for item in tree.get_children():
            tree.delete(item)

        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Appointments ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()

            from registration import Registration
            r_obj = Registration.__new__(Registration)
            r_obj.app = self.app

            for row in rows:
                pid = str(row[0])
                formatted_id = r_obj.format_patient_id(pid)
                pname = str(row[1]) if len(row) > 1 and row[1] else ""
                addr = str(row[5]) if len(row) > 5 and row[5] else (str(row[6]) if len(row) > 6 and row[6] else "")
                tree.insert("", "end", values=(formatted_id, pname, addr))
        except Exception as e:
            print("Error loading work register:", e)

    def on_patient_work_select(self, event=None):
        tree = getattr(self, 'history_tree', getattr(self, 'pat_tree', None))
        if not tree:
            return
        selected = tree.selection()
        if not selected:
            return
        vals = tree.item(selected[0], "values")
        if not vals:
            return

        formatted_id = str(vals[0]).strip()
        
        from registration import Registration
        r_obj = Registration.__new__(Registration)
        r_obj.app = self.app
        pid_num = r_obj.parse_patient_id(formatted_id)
        if not pid_num:
            pid_num = formatted_id

        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Appointments WHERE id = ?", (pid_num,))
            row = cursor.fetchone()
            conn.close()

            if row:
                self.clear_patient_fields()
                formatted_pid = r_obj.format_patient_id(str(row[0]))
                reg_no = r_obj.format_reg_no(str(row[0]))

                if hasattr(self, 'bill_patientid') and self.bill_patientid:
                    self.bill_patientid.delete(0, tk.END)
                    self.bill_patientid.insert(0, formatted_pid)

                if hasattr(self, 'bill_regno') and self.bill_regno:
                    self.bill_regno.delete(0, tk.END)
                    self.bill_regno.insert(0, reg_no)

                if hasattr(self, 'bill_patientname') and self.bill_patientname and len(row) > 1 and row[1]:
                    self.bill_patientname.delete(0, tk.END)
                    self.bill_patientname.insert(0, str(row[1]))

                if hasattr(self, 'bill_age') and self.bill_age and len(row) > 2 and row[2]:
                    self.bill_age.delete(0, tk.END)
                    self.bill_age.insert(0, str(row[2]))

                if hasattr(self, 'bill_gender') and self.bill_gender and len(row) > 3 and row[3]:
                    self.bill_gender.set(str(row[3]))

                if hasattr(self, 'bill_address1') and self.bill_address1 and len(row) > 5 and row[5]:
                    self.bill_address1.delete(0, tk.END)
                    self.bill_address1.insert(0, str(row[5]))

                if hasattr(self, 'bill_address2') and self.bill_address2 and len(row) > 6 and row[6]:
                    self.bill_address2.delete(0, tk.END)
                    self.bill_address2.insert(0, str(row[6]))

                if hasattr(self, 'bill_office') and self.bill_office and len(row) > 7 and row[7]:
                    self.bill_office.delete(0, tk.END)
                    self.bill_office.insert(0, str(row[7]))

                if hasattr(self, 'bill_residence') and self.bill_residence and len(row) > 8 and row[8]:
                    self.bill_residence.delete(0, tk.END)
                    self.bill_residence.insert(0, str(row[8]))

                if hasattr(self, 'bill_email') and self.bill_email and len(row) > 11 and row[11]:
                    self.bill_email.delete(0, tk.END)
                    self.bill_email.insert(0, str(row[11]))

        except Exception as e:
            print("Error selecting patient work:", e)

    def add_work_item(self):
        work_type = self.cb_material_type.get().strip() or "Standard Work"
        tooth = self.entry_tooth_single.get().strip() or ",".join(
            [t for t, v in self.tooth_vars.items() if v.get()]
        )
        rate = self.entry_rate.get().strip() or "0.00"
        self.work_table.insert("", "end", values=(work_type, tooth, "1"))

    def find_lab(self):
        search_term = self.entry_find_name.get().strip()
        if not search_term:
            messagebox.showinfo("Search", "Please enter a name to search.")
            return

        tree = getattr(self, 'history_tree', getattr(self, 'pat_tree', None))
        if not tree:
            return

        for item in tree.get_children():
            vals = tree.item(item, "values")
            if len(vals) > 1 and search_term.lower() in str(vals[1]).lower():
                tree.selection_set(item)
                tree.see(item)
                self.on_patient_work_select(None)
                return
        messagebox.showinfo("Search", f"No record found for '{search_term}'.")

    def on_save(self):
        pid = self.bill_patientid.get().strip()
        regno = self.bill_regno.get().strip()
        pname = self.bill_patientname.get().strip()
        lab_name = self.cb_lab_name.get().strip()
        work_type = self.cb_material_type.get().strip() or "Dental Work"
        selected_teeth = [t for t, v in self.tooth_vars.items() if v.get()]
        tooth_no = (
            self.entry_tooth_single.get().strip()
            or ",".join(selected_teeth)
            or "N/A"
        )
        despatch_date = self.entry_despatch_date.get().strip()
        delivery_date = self.entry_delivery_date.get().strip()
        cost = self.entry_rate.get().strip() or "0"
        comments = self.txt_comments.get("1.0", tk.END).strip()

        if not pname:
            messagebox.showwarning("Warning", "Patient Name is required.")
            return

        try:
            conn = get_db_connection(self.app)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Lab_Work (
                    patientid, regno, patientname, lab_name, work_type, tooth_no,
                    sent_date, expected_date, cost, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    pid,
                    regno,
                    pname,
                    lab_name,
                    work_type,
                    tooth_no,
                    despatch_date,
                    delivery_date,
                    cost,
                    comments,
                ),
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Lab work record saved successfully.")
            self.load_patient_work_register()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save record: {str(e)}")

    def on_preview(self):
        messagebox.showinfo("Preview", "Lab order preview is ready.")

    def clear_all(self):
        self.clear_patient_fields()
        self.entry_tooth_single.delete(0, tk.END)
        self.entry_rate.delete(0, tk.END)
        self.entry_rate.insert(0, "0.00")
        self.cb_material_type.set("")
        self.txt_comments.delete("1.0", tk.END)
        for v in self.tooth_vars.values():
            v.set(False)
        for item in self.work_table.get_children():
            self.work_table.delete(item)

    def add_new_lab(self):
        win = tk.Toplevel(self.app.root)
        win.title("Add New Lab")
        win.geometry("300x150")
        tk.Label(win, text="Enter Lab Name:", font=("Arial", 10)).pack(pady=10)
        e = tk.Entry(win, width=25)
        e.pack(pady=5)

        def save_lab():
            lab_name = e.get().strip()
            if lab_name:
                try:
                    conn = get_db_connection(self.app)
                    c = conn.cursor()
                    c.execute(
                        "INSERT OR IGNORE INTO Labs (Lab_Name) VALUES (?)",
                        (lab_name,),
                    )
                    conn.commit()
                    conn.close()
                    messagebox.showinfo(
                        "Success", f"Lab '{lab_name}' added successfully."
                    )
                    self.cb_lab_name["values"] = self.get_dropdown_data(
                        "Labs", "Lab_Name"
                    )
                    self.cb_lab_name.set(lab_name)
                    win.destroy()
                except Exception as err:
                    messagebox.showerror("Error", str(err))

        tk.Button(win, text="Save Lab", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), command=save_lab).pack(pady=10)

    def close_workspace(self):
        pid = self.patient_data.get("patientid", "") if hasattr(self, 'patient_data') and self.patient_data else ""
        if not pid and hasattr(self, 'bill_patientid') and self.bill_patientid:
            pid = self.bill_patientid.get().strip()

        if hasattr(self.app, "registration"):
            self.app.registration(patient_id=pid if pid else None)
        else:
            from registration import Registration
            r = Registration(self.app)
            r.registration_workspace()
            if pid:
                try:
                    r.select_patient_by_id(pid)
                except Exception:
                    pass
