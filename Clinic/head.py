import os
import sqlite3
from accounts import get_db_connection
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

class Head:
    def __init__(self, accounts_view):
        self.accounts_view = accounts_view
        self.app = accounts_view.app
        self.root = self.app.root
        self.close = accounts_view.close
        
        self.head()
    
    def head(self):
        win = tk.Toplevel(self.root)
        win.title("General Ledger Heads")
        win.geometry("520x420")
        win.configure(bg="white")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="General Ledger Heads", font=("Arial", 16, "bold"), fg="navy", bg="white").pack(pady=10)

        table_frame = tk.Frame(win, bg="white")
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        form_frame = tk.Frame(table_frame, bg="white")
        form_frame.pack(fill="x", pady=5)

        tk.Label(form_frame, text="Head Name:", bg="white", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        head_entry = tk.Entry(form_frame, width=22, font=("Arial", 10))
        head_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Type:", bg="white", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        type_combo = ttk.Combobox(form_frame, values=["Income", "Expense", "Asset", "Liability"], state="readonly", width=14)
        type_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        type_combo.current(1)

        columns = ("HeadID", "Head Name", "Type")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=9)
        tree.heading("HeadID", text="Head ID")
        tree.heading("Head Name", text="Head Name")
        tree.heading("Type", text="Type")

        tree.column("HeadID", width=80, anchor="center")
        tree.column("Head Name", width=260)
        tree.column("Type", width=120, anchor="center")
        tree.pack(fill="both", expand=True, pady=5)

        def load_heads():
            for item in tree.get_children():
                tree.delete(item)
            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("SELECT id, head_name, head_type FROM Heads ORDER BY id ASC")
                for r in cursor.fetchall():
                    tree.insert("", "end", values=r)
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error loading heads: {e}")

        def add_head():
            head_val = head_entry.get().strip()
            head_type = type_combo.get()
            if not head_val:
                messagebox.showwarning("Validation Error", "Please enter Head Name.")
                return

            try:
                conn = get_db_connection(self.app)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Heads (head_name, head_type) VALUES (?, ?)", (head_val, head_type))
                conn.commit()
                conn.close()

                head_entry.delete(0, tk.END)
                load_heads()
                messagebox.showinfo("Success", f"A/c Head '{head_val}' added.")
            except sqlite3.IntegrityError:
                messagebox.showwarning("Duplicate Head", f"Head '{head_val}' already exists.")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to save head: {e}")

        def delete_head():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Select a head to delete.")
                return
            head_id, head_name, _ = tree.item(selected[0])['values']
            if messagebox.askyesno("Confirm", f"Delete account head '{head_name}'?"):
                try:
                    conn = get_db_connection(self.app)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Heads WHERE id=?", (head_id,))
                    conn.commit()
                    conn.close()
                    load_heads()
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Failed to delete head: {e}")

        button_frame = tk.Frame(table_frame, bg="white")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Head", font=("Arial", 10, "bold"), bg="green", fg="white", command=add_head, width=12).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Delete Selected", font=("Arial", 10), command=delete_head, width=14).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Close", font=("Arial", 10), command=win.destroy, width=10).grid(row=0, column=2, padx=5)

        load_heads()
