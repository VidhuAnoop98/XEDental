from Clinic import card
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import sqlite3
import os

class Case_Details:
    def __init__(self, app):
        self.app = app
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        self.case_details()

    def close(self):
        self.app.files()

    def case_details(self):
        self.app.clear_workspace()
        self.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace = self.workspace
        self.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        tk.Label(self.app.workspace, text="Case " + chr(38) + " Collection Details",
                 font=("Arial", 14, "bold"), fg="navy").pack(pady=10)

        main = tk.Frame(self.app.workspace)
        main.pack()

        top_frame = tk.Frame(main)
        top_frame.pack()

        left   = tk.Frame(top_frame); left.pack(side="left")
        middle = tk.Frame(top_frame); middle.pack(side="left")
        right  = tk.Frame(top_frame); right.pack(side="right")

        bottom_frame = tk.Frame(main)
        bottom_frame.pack()

        bm_left  = tk.Frame(bottom_frame); bm_left.pack(side="left")
        bm_right = tk.Frame(bottom_frame); bm_right.pack(side="right")

        self.stock_cal = Calendar(right, selectmode="day", date_pattern="dd-mm-yyyy")
        self.stock_cal.pack(padx=20, pady=20)

        btn_data = [
            ("Treatment Report", 1, 0, self.Treatment_report),
            ("Treatment Key Word wise", 1, 1, self.Treatment_key_word),
            ("Treatment Register", 2, 0, self.Treatment_register),
            ("Daily Cash Transactions", 2, 1, self.Treatment_daily_cash),
            ("Not Paid List", 3, 0, self.Treatment_not_paid),
            ("Patient Balance", 3, 1, self.Treatment_patient_balance),
            ("Collection Chart", 4, 0, self.Treatment_collection_chart),
            ("Consultant Wise", 4, 1, self.Treatment_consultant_wise),
        ]
        for text, row, col, cmd in btn_data:
            tk.Button(left, text=text, font=("Arial", 12), command=cmd).grid(row=row, column=col, padx=10, pady=10)

        tk.Label(middle, text="Start Date",          font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.start_date = tk.Entry(middle)
        self.start_date.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(middle, text="End Date",            font=("Arial", 12)).grid(row=0, column=2, padx=10, pady=10)
        self.end_date = tk.Entry(middle)
        self.end_date.grid(row=0, column=3, padx=10, pady=10)

        tk.Label(middle, text="Find Treatment Code", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        self.Find_treatment = tk.Entry(middle)
        self.Find_treatment.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(middle, text="Treatment Code",      font=("Arial", 12)).grid(row=1, column=2, padx=10, pady=10)
        self.SID = tk.Entry(middle)
        self.SID.grid(row=1, column=3, padx=10, pady=10)

        tk.Label(middle, text="Treatment",           font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
        self.Invoice = tk.Entry(middle)
        self.Invoice.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(middle, text="ADD",    font=("Arial", 12), command=getattr(self, "add_stock",    lambda: None)).grid(row=4, column=0, padx=10, pady=10)
        tk.Button(middle, text="DELETE", font=("Arial", 12), command=getattr(self, "delete_stock", lambda: None)).grid(row=4, column=1, padx=10, pady=10)
        tk.Button(middle, text="Close",  font=("Arial", 12), command=self.close).grid(row=4, column=2, padx=10, pady=10)
        tk.Button(middle, text="View Consultants Ledger", font=("Arial", 12), bg="red",
                  command=getattr(self, "view", lambda: None)).grid(row=5, column=2, padx=10, pady=10)

        tc_columns = ("Treatment Code", "Treatment")
        tc_tree = ttk.Treeview(bm_left, columns=tc_columns, show="headings",height=5)
        tc_tree.pack(pady=20)
        for col in tc_columns:
            tc_tree.heading(col, text=col)
            tc_tree.column(col, width=100)

        tk.Label(bm_right, text="Refby", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Entry(bm_right).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        tk.Button(bm_right, text="Previous").grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ref_columns = ("Patient id", "Name", "Tooth", "Address", "Contact No", "Mobile No")
        ref_tree = ttk.Treeview(bm_right, columns=ref_columns, show="headings",height=10)
        ref_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        for col in ref_columns:
            ref_tree.heading(col, text=col)
            ref_tree.column(col, width=100)

    def on_stock_register_complete(self):
        try:
            selected_date = self.stock_cal.get_date()
        except Exception:
            selected_date = None
        start_val = ""
        end_val = ""
        try: start_val = self.start_date.get()
        except Exception: pass
        try: end_val = self.end_date.get()
        except Exception: pass
        info = selected_date or start_val or end_val or "no date or range provided"
        messagebox.showinfo("Stock Register", f"Stock register completed for: {info}")

    def Treatment_report(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(fill="both", expand=True, padx=10, pady=10)
        ws = self.app.workspace

        PAGE_W, PAGE_H = 595.0, 842.0 # A4 size in points

        # Try to check if reportlab is ok
        try:
            from reportlab.lib.pagesizes import A4
            reportlab_ok = True
        except ImportError:
            reportlab_ok = False

        AVAIL_H = 500
        AVAIL_W = 500
        self.preview_scale = min(AVAIL_H / PAGE_H, AVAIL_W / PAGE_W)
        
        CW      = int(PAGE_W * self.preview_scale)
        CH      = int(PAGE_H * self.preview_scale)

        outer = tk.Frame(ws, bg="#c0c0c0")
        outer.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        vsb = tk.Scrollbar(outer, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(outer, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        cv = tk.Canvas(outer, bg="#c0c0c0", width=CW+10, height=CH+1,
                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        cv.pack(fill="both", expand=True)
        vsb.config(command=cv.yview)
        hsb.config(command=cv.xview)

        canvas_width = CW + 950      # Same as the Canvas width logic in Letter_Pad
        OX = (canvas_width - CW) // 2
        OY = 10



        def zoom_in():
            if self.preview_scale < 2.0:
                self.preview_scale = round(min(2.0, self.preview_scale + 0.1), 1)
                draw_page_preview(state["current_page"])

        def zoom_out():
            if self.preview_scale > 0.25:
                self.preview_scale = round(max(0.25, self.preview_scale - 0.1), 1)
                draw_page_preview(state["current_page"])

        def on_mouse_wheel(event):
            if getattr(event, "delta", 0) > 0 or getattr(event, "num", 0) == 4:
                zoom_in()
            else:
                zoom_out()
            return "break"

        cv.bind("<MouseWheel>", on_mouse_wheel)
        cv.bind("<Button-4>", on_mouse_wheel)
        cv.bind("<Button-5>", on_mouse_wheel)

        def prev_page():
            if state["current_page"] > 0:
                draw_page_preview(state["current_page"] - 1)

        def next_page():
            if state["current_page"] < len(state["pages"]) - 1:
                draw_page_preview(state["current_page"] + 1)

        def draw_page_preview(page_idx):
            state["current_page"] = page_idx
            cv.delete("all")
            
            scale = self.preview_scale
            w_scaled = int(PAGE_W * scale)
            h_scaled = int(PAGE_H * scale)
            
            cv.config(scrollregion=(0, 0, w_scaled + 40, h_scaled + 40))
            
            local_ox = (canvas_width - w_scaled) // 2
            local_oy = 10
            
            # Draw paper shadow
            cv.create_rectangle(local_ox+4, local_oy+4, local_ox+w_scaled+4, local_oy+h_scaled+4, fill="#888888", outline="")
            # Draw paper background
            cv.create_rectangle(local_ox, local_oy, local_ox+w_scaled, local_oy+h_scaled, fill="white", outline="#aaaaaa", width=1)
            
            def ppx(pt):  return local_ox + int(pt * scale)
            def ppy(pt):  return local_oy + int((PAGE_H - pt) * scale)
            def pcx():    return local_ox + w_scaled // 2
            def spt(pt_val): return max(6, int(pt_val * scale))
            
            
            if not pages or page_idx >= len(pages):
                return
                
            page_txs = pages[page_idx]
            
            page_lbl.config(text=f"Page {page_idx + 1} of {len(pages)}")
            zoom_lbl.config(text=f"{int(scale / (min(600 / PAGE_H, 500 / PAGE_W)) * 100)}%")
            
            
            cv.create_text(pcx(), ppy(PAGE_H - 40), text="Patient Treatment Report",
                               font=("Helvetica", spt(16), "bold"), fill="black")
            # Render the page text lines from the state["pages"] content
            y_start = 40
            line_spacing = 14
            for i, line in enumerate(page_txs):
                y_offset = y_start + i * line_spacing
                cv.create_text(pcx(), ppy(PAGE_H - y_offset), text=line,
                               font=("Helvetica", spt(10)), fill="black")
            y_pt = PAGE_H - (y_start + len(page_txs) * line_spacing)
            

        # Preview Controls (Zoom & Navigation)
        ctrl_frame = tk.Frame(ws)
        ctrl_frame.pack(fill="x", pady=4)

        btn_prev = tk.Button(ctrl_frame, text=" ◀", font=("Arial", 9, "bold"), command=lambda: prev_page())
        btn_prev.pack(side="left", padx=5)

        page_lbl = tk.Label(ctrl_frame, text="Page 1 of 1", font=("Arial", 10, "bold"), bg="white")
        page_lbl.pack(side="left", padx=5)

        btn_next = tk.Button(ctrl_frame, text=" ▶", font=("Arial", 9, "bold"), command=lambda: next_page())
        btn_next.pack(side="left", padx=5)

        # tk.Label(ctrl_frame, text="   |   ", bg="white").pack(side="left")

        btn_zoom_out = tk.Button(ctrl_frame, text="-", font=("Arial", 9, "bold"), command=lambda: zoom_out())
        btn_zoom_out.pack(side="left", padx=5)

        zoom_lbl = tk.Label(ctrl_frame, text="100%", font=("Arial", 10), bg="white")
        zoom_lbl.pack(side="left", padx=5)

        btn_zoom_in = tk.Button(ctrl_frame, text="+", font=("Arial", 9, "bold"), command=lambda: zoom_in())
        btn_zoom_in.pack(side="left", padx=5)

        btn_bar = tk.Frame(ws)
        btn_bar.pack(pady=8)

        def generate_pdf(filepath, s_str, e_str):
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(filepath, pagesize=(PAGE_W, PAGE_H))
            # pages = state.get("pages", []) or [[]]

            left_margin = 72
            right_margin = 72
            top_margin = 72
            bottom_margin = 72
            line_height = 14

            for page in pages:
                y = PAGE_H - top_margin

            # -------------------- Report Header --------------------
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(PAGE_W / 2, y, "Patient Treatment Report")
            y -= 22

            # Top Line
            c.setLineWidth(1)
            c.line(left_margin, y, PAGE_W - right_margin, y)
            y -= 18

            # Column Headings
            c.setFont("Helvetica-Bold", 10)

            headers = [
                ("Patient ID", left_margin),
                ("Name", left_margin + 90),
                ("Address", left_margin + 240),
                ("Doctor", left_margin + 380),
                ("Purpose", left_margin + 470),
            ]

            for text, x in headers:
                c.drawString(x, y, text)

            y -= 10

            # Bottom Line
            c.line(left_margin, y, PAGE_W - right_margin, y)
            y -= 18

            c.setFont("Helvetica", 10)
            for line in page:
                for sub in str(line).splitlines():
                    if y < bottom_margin:
                        c.showPage()
                        y = PAGE_H - top_margin
                    c.drawString(left_margin, y, sub)
                    y -= line_height

            c.showPage()

            c.save()

        def _open_pdf(path):
            import subprocess
            import sys
            try:
                if hasattr(os, "startfile"):
                    os.startfile(path)
                elif sys.platform.startswith("linux"):
                    subprocess.Popen(["xdg-open", path])
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["cmd", "/c", "start", "", path])
            except Exception as exc:
                messagebox.showwarning("Open PDF", f"Could not open the PDF automatically.\n{exc}")

        def _generate_pdf():
            if not reportlab_ok:
                messagebox.showerror("Missing Library",
                    "ReportLab is required.\nRun:  pip install reportlab")
                return
            s_str = ""
            e_str = ""
            try: s_str = self.start_date.get().strip()
            except Exception: pass
            try: e_str = self.end_date.get().strip()
            except Exception: pass
            if not s_str or not e_str:
                messagebox.showerror("Error", "Please select start and end dates.")
                return
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf", initialfile=f"Daily_Transaction_{s_str}_to_{e_str}.pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Daily Transaction Report As")
            if not filepath: return
            try:
                generate_pdf(filepath, s_str, e_str)
                messagebox.showinfo("Done", f"Daily Transaction Report saved:\n{filepath}")
                _open_pdf(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"PDF generation failed:\n{exc}")

        def _print_now():
            if not reportlab_ok:
                messagebox.showerror("Missing Library",
                    "ReportLab is required.\nRun:  pip install reportlab")
                return
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tmp = os.path.join(script_dir, "_daily_transaction_temp.pdf")
            try:
                s_str = ""
                e_str = ""
                try: s_str = self.start_date.get().strip()
                except Exception: pass
                try: e_str = self.end_date.get().strip()
                except Exception: pass
                generate_pdf(tmp, s_str, e_str)
                _open_pdf(tmp)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not open PDF:\n{exc}")

        tk.Button(btn_bar, text="📄  Generate PDF", font=("Arial", 11), width=16,
                  bg="#1565C0", fg="white", command=_generate_pdf).pack(side="left", padx=8)
        tk.Button(btn_bar, text="🖨  Open / Print", font=("Arial", 11), width=16,
                  bg="#2E7D32", fg="white", command=_print_now).pack(side="left", padx=8)
        tk.Button(btn_bar, text="Close",bg="#ED350E",fg="white", font=("Arial", 11), width=10,
                  command=self.close).pack(side="left", padx=8)


    def Treatment_key_word(self):
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(fill="both", expand=True, padx=10, pady=10)
        ws = self.app.workspace

        PAGE_W, PAGE_H = 595.0, 842.0 # A4 size in points

        # Try to check if reportlab is ok
        try:
            from reportlab.lib.pagesizes import A4
            reportlab_ok = True
        except ImportError:
            reportlab_ok = False

        AVAIL_H = 500
        AVAIL_W = 500
        self.preview_scale = min(AVAIL_H / PAGE_H, AVAIL_W / PAGE_W)
        
        CW      = int(PAGE_W * self.preview_scale)
        CH      = int(PAGE_H * self.preview_scale)

        outer = tk.Frame(ws, bg="#c0c0c0")
        outer.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        vsb = tk.Scrollbar(outer, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(outer, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        cv = tk.Canvas(outer, bg="#c0c0c0", width=CW+10, height=CH+1,
                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        cv.pack(fill="both", expand=True)
        vsb.config(command=cv.yview)
        hsb.config(command=cv.xview)

        canvas_width = CW + 950      # Same as the Canvas width logic in Letter_Pad
        OX = (canvas_width - CW) // 2
        OY = 10

        def zoom_in():
            if self.preview_scale < 2.0:
                self.preview_scale = round(min(2.0, self.preview_scale + 0.1), 1)
                draw_page_preview(state["current_page"])

        def zoom_out():
            if self.preview_scale > 0.25:
                self.preview_scale = round(max(0.25, self.preview_scale - 0.1), 1)
                draw_page_preview(state["current_page"])

        def on_mouse_wheel(event):
            if getattr(event, "delta", 0) > 0 or getattr(event, "num", 0) == 4:
                zoom_in()
            else:
                zoom_out()
            return "break"

        cv.bind("<MouseWheel>", on_mouse_wheel)
        cv.bind("<Button-4>", on_mouse_wheel)
        cv.bind("<Button-5>", on_mouse_wheel)

        def prev_page():
            if state["current_page"] > 0:
                draw_page_preview(state["current_page"] - 1)

        def next_page():
            if state["current_page"] < len(state["pages"]) - 1:
                draw_page_preview(state["current_page"] + 1)

        def draw_page_preview(page_idx):
            state["current_page"] = page_idx
            cv.delete("all")
            
            scale = self.preview_scale
            w_scaled = int(PAGE_W * scale)
            h_scaled = int(PAGE_H * scale)
            
            cv.config(scrollregion=(0, 0, w_scaled + 40, h_scaled + 40))
            
            local_ox = (canvas_width - w_scaled) // 2
            local_oy = 10
            
            # Draw paper shadow
            cv.create_rectangle(local_ox+4, local_oy+4, local_ox+w_scaled+4, local_oy+h_scaled+4, fill="#888888", outline="")
            # Draw paper background
            cv.create_rectangle(local_ox, local_oy, local_ox+w_scaled, local_oy+h_scaled, fill="white", outline="#aaaaaa", width=1)
            
            def ppx(pt):  return local_ox + int(pt * scale)
            def ppy(pt):  return local_oy + int((PAGE_H - pt) * scale)
            def pcx():    return local_ox + w_scaled // 2
            def spt(pt_val): return max(6, int(pt_val * scale))
            
            pages = state["pages"]
            if not pages or page_idx >= len(pages):
                return
                
            page_txs = pages[page_idx]
            
            page_lbl.config(text=f"Page {page_idx + 1} of {len(pages)}")
            zoom_lbl.config(text=f"{int(scale / (min(600 / PAGE_H, 500 / PAGE_W)) * 100)}%")
                        
            if page_idx == 0:
                cv.create_text(pcx(), ppy(PAGE_H - 40), text="TreatmentRegisterKeyWordWise",
                               font=("Helvetica", spt(16), "bold"), fill="black")
                cv.create_text(pcx(), ppy(PAGE_H - 60), text=f"{s_str} to {e_str}",
                               font=("Helvetica", spt(12)), fill="black")
                y_pt = PAGE_H - 100
            else:
                y_pt = PAGE_H - 50
                
            # Table headers
            headers = ["Collection", "Payments"]
            x_pt_positions = [420, 500]
            
            cv.create_line(ppx(30), ppy(y_pt - 5), ppx(PAGE_W - 30), ppy(y_pt - 5), fill="black", width=1)
            y_pt -= 1
            
            # Paper Page Footer
            cv.create_text(pcx(), ppy(30), text=f"Page {page_idx + 1} of {len(pages)}", font=("Helvetica", spt(9)), fill="black")

            draw_page_preview(0)

        # Preview Controls (Zoom & Navigation)
        ctrl_frame = tk.Frame(ws)
        ctrl_frame.pack(fill="x", pady=4)

        btn_prev = tk.Button(ctrl_frame, text=" ◀", font=("Arial", 9, "bold"), command=lambda: prev_page())
        btn_prev.pack(side="left", padx=5)

        page_lbl = tk.Label(ctrl_frame, text="Page 1 of 1", font=("Arial", 10, "bold"), bg="white")
        page_lbl.pack(side="left", padx=5)

        btn_next = tk.Button(ctrl_frame, text=" ▶", font=("Arial", 9, "bold"), command=lambda: next_page())
        btn_next.pack(side="left", padx=5)

        # tk.Label(ctrl_frame, text="   |   ", bg="white").pack(side="left")

        btn_zoom_out = tk.Button(ctrl_frame, text="-", font=("Arial", 9, "bold"), command=lambda: zoom_out())
        btn_zoom_out.pack(side="left", padx=5)

        zoom_lbl = tk.Label(ctrl_frame, text="100%", font=("Arial", 10), bg="white")
        zoom_lbl.pack(side="left", padx=5)

        btn_zoom_in = tk.Button(ctrl_frame, text="+", font=("Arial", 9, "bold"), command=lambda: zoom_in())
        btn_zoom_in.pack(side="left", padx=5)

        btn_bar = tk.Frame(ws)
        btn_bar.pack(pady=8)

        def generate_pdf(filepath, s_str, e_str):
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors

             # Paginate exactly like preview
            pages = []
            current_page_txs = []
            y = 700
            for i, tx in enumerate(transactions):
                is_last = (i == len(transactions) - 1)
                required_space = 18
                if is_last:
                    required_space += 54
                
                if y - required_space < 50:
                    pages.append(current_page_txs)
                    current_page_txs = [tx]
                    y = 780
                else:
                    current_page_txs.append(tx)
                    y -= 18
            if current_page_txs:
                pages.append(current_page_txs)
            
            if not pages:
                pages = [[]]

            c = canvas.Canvas(filepath, pagesize=(PAGE_W, PAGE_H))
            width, height = PAGE_W, PAGE_H
            
            for page_idx, page_txs in enumerate(pages):
                # Draw white background
                c.setFillColor(colors.white)
                c.rect(0, 0, width, height, fill=1, stroke=0)

                # Reset to black for text
                c.setFillColor(colors.black)
                
                if page_idx == 0:
                    c.setFont("Helvetica-Bold", 16)
                    c.drawCentredString(width / 2.0, height - 50, "TreatmentRegisterKeyWordWise")                    
                    y = height - 100
                else:
                    y = height - 50
                
                # Table headers
                c.setFont("Helvetica-Bold", 10)
                headers = ["Receipts", "Payments"]
                x_positions = [ 420, 500]
                
                           
                # Page number footer
                c.setFont("Helvetica", 9)
                c.drawCentredString(width / 2.0, 30, f"Page {page_idx + 1} of {len(pages)}")
                
                c.showPage()
                
            c.save()

        def _open_pdf(path):
            import subprocess
            import sys
            try:
                if hasattr(os, "startfile"):
                    os.startfile(path)
                elif sys.platform.startswith("linux"):
                    subprocess.Popen(["xdg-open", path])
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["cmd", "/c", "start", "", path])
            except Exception as exc:
                messagebox.showwarning("Open PDF", f"Could not open the PDF automatically.\n{exc}")

        def _generate_pdf():
            if not reportlab_ok:
                messagebox.showerror("Missing Library",
                    "ReportLab is required.\nRun:  pip install reportlab")
                return
            s_str = start_date_entry.get().strip()
            e_str = end_date_entry.get().strip()
            if not s_str or not e_str:
                messagebox.showerror("Error", "Please select start and end dates.")
                return
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf", initialfile=f"Daily_Transaction_{s_str}_to_{e_str}.pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Daily Transaction Report As")
            if not filepath: return
            try:
                generate_pdf(filepath, s_str, e_str)
                messagebox.showinfo("Done", f"Daily Transaction Report saved:\n{filepath}")
                _open_pdf(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"PDF generation failed:\n{exc}")

        def _print_now():
            if not reportlab_ok:
                messagebox.showerror("Missing Library",
                    "ReportLab is required.\nRun:  pip install reportlab")
                return
            s_str = start_date_entry.get().strip()
            e_str = end_date_entry.get().strip()
            if not s_str or not e_str:
                messagebox.showerror("Error", "Please select start and end dates.")
                return
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tmp = os.path.join(script_dir, "_daily_transaction_temp.pdf")
            try:
                generate_pdf(tmp, s_str, e_str)
                _open_pdf(tmp)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not open PDF:\n{exc}")

        tk.Button(btn_bar, text="📄  Generate PDF", font=("Arial", 11), width=16,
                  bg="#1565C0", fg="white", command=_generate_pdf).pack(side="left", padx=8)
        tk.Button(btn_bar, text="🖨  Open / Print", font=("Arial", 11), width=16,
                  bg="#2E7D32", fg="white", command=_print_now).pack(side="left", padx=8)
        tk.Button(btn_bar, text="Close",bg="#ED350E",fg="white", font=("Arial", 11), width=10,
                  command=self.close).pack(side="left", padx=8)



    def Treatment_register(self):
        s_str = ""
        e_str = ""
        try: s_str = self.start_date.get().strip()
        except Exception: pass
        try: e_str = self.end_date.get().strip()
        except Exception: pass
        messagebox.showinfo("Treatment Register", f"Open Treatment Register from {s_str} to {e_str}")

    def Treatment_daily_cash(self):
        s_str = ""
        e_str = ""
        try: s_str = self.start_date.get().strip()
        except Exception: pass
        try: e_str = self.end_date.get().strip()
        except Exception: pass
        messagebox.showinfo("Daily Cash Transactions", f"Show daily cash transactions between {s_str} and {e_str}")

    def Treatment_not_paid(self):
        messagebox.showinfo("Not Paid List", "Show list of unpaid treatments (not implemented)")

    def Treatment_patient_balance(self):
        messagebox.showinfo("Patient Balance", "Show patient balances (not implemented)")

    def Treatment_collection_chart(self):
        messagebox.showinfo("Collection Chart", "Show collection chart (not implemented)")

    def Treatment_consultant_wise(self):
        messagebox.showinfo("Consultant Wise", "Show consultant-wise report (not implemented)")