import os
import sqlite3
import sys  
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLINIC_DIR = os.path.join(SCRIPT_DIR, "Clinic")
if CLINIC_DIR not in sys.path:
    sys.path.insert(0, CLINIC_DIR)


from registration import Registration
from personal import Personal
from files import Files
from accounts import Accounts
from reports import Reports
from materials import Materials
    
class dental:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dr.Anoop's Dental Clinic")
        self.root.state("zoomed")

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.tkinter_dir = self.script_dir
        self.db_path = os.path.join(self.script_dir, "dental.db")
        self.current_file = None
        self.login_username = "admin"
        self.login_password = "admin"


        # Global TTK Style configuration for Treeview
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self.style.configure("Treeview",
                            background="#FFFFFF",
                            foreground="#000000",
                            rowheight=25,
                            fieldbackground="#FFFFFF",
                            font=("Arial", 10))
        self.style.configure("Treeview.Heading",
                            font=("Arial", 10, "bold"))
        self.style.map("Treeview",
                       background=[("selected", "#1976D2")],
                       foreground=[("selected", "#FFFFFF")])

        self.menu()
        self.create_nav()
        self.reports()
        self.root.mainloop()

    @staticmethod
    def setup_treeview_style(tree):
        if tree:
            tree.config(cursor="hand2")
            tree.tag_configure("evenrow", background="#E3F2FD", foreground="black")
            tree.tag_configure("oddrow", background="#F5F5F5", foreground="black")

    def menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Close")
        file_menu.add_separator()
        file_menu.add_command(label="Print Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="AutoDial")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Tools Menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Sqlite Database")
        tools_menu.add_command(label="Send to MS Access")
        tools_menu.add_command(label="Send to MS Word")
        tools_menu.add_command(label="Send to Ms Excel")
        menu_bar.add_cascade(label="Tools", menu=tools_menu)

        self.root.config(menu=menu_bar)

    def create_nav(self):
        buttonframe = tk.Frame(self.root)
        for col in range(12):
            buttonframe.columnconfigure(col, weight=1)

        nav_buttons = [
            ("Dental",self.dental),    
            ("Registration",self.registration),
            ("Files",self.files),
            ("Personal",self.personal),
            ("Materials",self.materials), 
            ("Accounts",self.accounts),
            ("Reports",self.reports),                                                                                                                              
            ("About us",self.aboutus),
        ]

        for idx, (text, command) in enumerate(nav_buttons):
            btn = tk.Button(buttonframe, text=text, font=("Arial", 14), command=command)
            btn.grid(row=0, column=idx + 1, sticky=tk.W + tk.E)

        tk.Button(buttonframe, text="Exit To Windows",font=("Arial", 14),fg="red",command=self.root.destroy,).grid(row=0, column=len(nav_buttons) + 1, sticky=tk.W + tk.E)

        tk.Button(buttonframe, text="Log off user", command=self.log, font=("Arial", 14)).grid(row=0, column=len(nav_buttons) + 2, sticky=tk.W + tk.E)

        buttonframe.pack(fill="x")

        status_bar = tk.Label(self.root, text="Ready  |  File > Open to load a document", bd=1, relief="sunken",anchor="w",).pack(side="bottom", fill="x")

    def clear_workspace(self):
        if hasattr(self, 'workspace') and self.workspace.winfo_exists():
            self.workspace.destroy()

    def dental(self):
        self.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        logo_path = os.path.join(self.tkinter_dir, "Clinic", "Dental_logo.png")
        if os.path.exists(logo_path):
            image = Image.open(logo_path).resize((200, 200))
            self.logo_photo = ImageTk.PhotoImage(image)
            tk.Label(self.workspace, image=self.logo_photo).place(relx=0.5, y=100, anchor='n')           
            
        tk.Label(self.workspace,text="Dr.Anoop's Anupam Dental Clinic",font=("Arial", 20,"bold")).place(x=500, y=400)
        tk.Label(self.workspace,text="West Gate, Vaikom",font=("Arial", 20,"bold")).place(x=560, y=435)
        tk.Label(self.workspace,text="Kottayam Dist",font=("Arial", 20,"bold")).place(x=575, y=470)
        tk.Label(self.workspace,text="Kerala - 686141",font=("Arial", 20,"bold")).place(x=570, y=505)

    def registration(self):
        Registration(self)  

    def personal(self):
        Personal(self)

    def files(self):
        Files(self)

    def accounts(self):
        Accounts(self)

    def reports(self):
        Reports(self)

    def materials(self):
        Materials(self)

    def aboutus(self):
        self.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        logo_path = os.path.join(self.tkinter_dir, "Clinic", "Dental_logo.png")
        if os.path.exists(logo_path):
            image = Image.open(logo_path).resize((200, 200))
            self.logo_photo = ImageTk.PhotoImage(image)
            tk.Label(self.workspace, image=self.logo_photo).place(relx=0.5, y=100, anchor='n')           
            
        tk.Label(self.workspace,text="Dr.Anoop's Anupam Dental Clinic",font=("Arial", 20,"bold")).place(x=500, y=400)
        tk.Label(self.workspace,text="West Gate, Vaikom",font=("Arial", 20,"bold")).place(x=560, y=435)
        tk.Label(self.workspace,text="Kottayam Dist",font=("Arial", 20,"bold")).place(x=575, y=470)
        tk.Label(self.workspace,text="Kerala - 686141",font=("Arial", 20,"bold")).place(x=570, y=505)

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def log(self):
        self.clear_workspace()
        self.workspace = tk.Frame(self.root, bd=3, relief="solid")
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)

        login_frame = tk.Frame(self.workspace, bd=2, relief="groove", padx=30, pady=30)
        login_frame.place(relx=0.5, rely=0.45, anchor="center")

        logo_path = os.path.join(self.tkinter_dir, "Clinic", "Dental_logo.png")
        if os.path.exists(logo_path):
            image = Image.open(logo_path).resize((100, 100))
            self.logo_photo = ImageTk.PhotoImage(image)
            tk.Label(login_frame, image=self.logo_photo).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        tk.Label(login_frame, text="Login", font=("Arial", 16, "bold")).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        tk.Label(login_frame, text="Username:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        username_entry = tk.Entry(login_frame, font=("Arial", 12), width=25)
        username_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(login_frame, text="Password:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        password_entry = tk.Entry(login_frame, font=("Arial", 12), width=25, show="*")
        password_entry.grid(row=3, column=1, padx=10, pady=10)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get()

            if username == self.login_username and password == self.login_password:
                self.root.unbind("<Return>")
                messagebox.showinfo("Success", "Login complete")
                self.dental()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
                password_entry.delete(0, tk.END)
                password_entry.focus_set()

        tk.Button(login_frame, text="Login", font=("Arial", 12), width=12, command=login).grid(row=4, column=0, columnspan=2, pady=(20, 0))

        username_entry.focus_set()
        self.root.bind("<Return>", lambda event: login())



if __name__ == "__main__": 
    app = dental()
