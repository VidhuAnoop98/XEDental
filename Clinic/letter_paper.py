
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from tkcalendar import Calendar
import sqlite3
import os
import subprocess
import sys

class Letter:
    def __init__(self, app, mode="letter"):
        self.app = app
        self.init_db()
        if mode == "letter":
            self.Letter_Pad()
        elif mode == "plain":
            self.Plain_Priscription()
    
    def init_db(self):
        self.conn = sqlite3.connect("dental.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS letterpad (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, phone TEXT, email TEXT, website TEXT, logo TEXT)")
        self.conn.commit()
    

    def Letter_Pad(self):
        # ---- ReportLab import ----
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm as rl_mm
            from reportlab.pdfgen import canvas as rl_canvas
            from reportlab.lib.colors import HexColor
            from reportlab.lib.utils import ImageReader
            reportlab_ok = True
            PAGE_W, PAGE_H = A4          # points  (595 × 842)
        except ImportError:
            reportlab_ok = False
            PAGE_W, PAGE_H = 595.0, 842.0
            rl_mm = 2.8346
            HexColor = None
            ImageReader = None
            rl_canvas = None

        # ── Paths & clinic data ──────────────────────────────────────────
        SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
        LOGO_PATH      = os.path.join(SCRIPT_DIR, "Dental_logo.png")
        CLINIC_NAME    = "ANUPAM DENTAL CLINIC"
        CLINIC_ADDRESS = "West Gate Vaikom - 686141"
        CLINIC_PHONE   = "Clinic : 9446046868"
        CLINIC_RESI    = "Resi   : 216858"
        CLINIC_HOURS   = "Clinic Hours : 10:00 AM to 07:00 PM,  Tuesday Holiday"

        CONSULTANTS = [
            {"name": "Dr.ANOOP KUMAR. B D S", "role": "DENTAL SURGEON", "reg": "Reg.No. 1/32"},
        ]
        VISITING_DOCTORS = [
            {"name": "Dr.JUSTIN MATHEW. MDS",       "role": "Oral & Maxillo Facial Surgeon", "reg": "Reg.No. 5492"},
            {"name": "Dr.KRISHNA KUMAR. MDS",        "role": "Paedodontist",                  "reg": "Reg.No. 7729"},
            {"name": "Dr.JOSEPH J PULIKKOTTIL. MDS", "role": "Periodontist & Implantologist", "reg": "Reg.No. 2418"},
            {"name": "Dr.TERRY THOMAS. MDS",         "role": "Orthodontist",                  "reg": "Reg.No. 4807"},
            {"name": "Dr.SHIBHU SREEDHAR. MDS",      "role": "Endodontist",                   "reg": "Reg.No. 15619-A"},
            {"name": "Dr.RENJITH RAJ. MDS",          "role": "Endodontist",                   "reg": "Reg.No. 8171"},
            {"name": "Dr.SIJO P MATHEW. MDS",        "role": "Endodontist",                   "reg": "Reg.No. 8982"},
        ]

        # ==============================================================
        # PDF generation (ReportLab)
        # ==============================================================
        def draw_logo(c, cx: float, cy: float, r: float):
            if os.path.isfile(LOGO_PATH) and ImageReader:
                img = ImageReader(LOGO_PATH)
                iw, ih = img.getSize()
                box = 2 * r
                scale = min(box / iw, box / ih)
                w, h = iw * scale, ih * scale
                c.drawImage(img, cx - w / 2, cy - h / 2, width=w, height=h, mask="auto", preserveAspectRatio=True)
                return
            
            # Fallback
            c.saveState()
            c.setDash(1, 2)
            c.setLineWidth(1)
            c.circle(cx, cy, r, stroke=1, fill=0)
            c.circle(cx, cy, r - 2 * rl_mm, stroke=1, fill=0)
            c.restoreState()
            c.saveState()
            c.translate(cx, cy)
            c.rotate(90)
            c.setFont("Helvetica-Bold", 5.5)
            c.drawCentredString(0, r - 5 * rl_mm, "ANUPAM")
            c.restoreState()
            c.setFont("Helvetica", 4.5)
            c.drawCentredString(cx, cy - 1.5 * rl_mm, "DENTAL")
            c.drawCentredString(cx, cy - 4.5 * rl_mm, "CLINIC")

        def draw_letterhead(c):
            if HexColor:
                ink = HexColor("#1a1a1a")
                c.setFillColor(ink)
                c.setStrokeColor(ink)
            
            logo_cx, logo_cy, logo_r = 30 * rl_mm, PAGE_H - 20 * rl_mm, 15 * rl_mm
            draw_logo(c, logo_cx, logo_cy, logo_r)
            
            header_cx = PAGE_W / 2
            c.setFont("Times-Bold", 20)
            c.drawCentredString(header_cx, PAGE_H - 15 * rl_mm, CLINIC_NAME)
            c.setFont("Helvetica", 8.5)
            c.drawCentredString(header_cx, PAGE_H - 22 * rl_mm, CLINIC_ADDRESS)
            c.setFont("Helvetica", 9)
            c.drawCentredString(PAGE_W - 28 * rl_mm, PAGE_H - 30 * rl_mm, f"{CLINIC_PHONE}")
            c.drawCentredString(PAGE_W - 32 * rl_mm, PAGE_H - 37 * rl_mm, f"{CLINIC_RESI}")
            
            top_line_y = PAGE_H - 47 * rl_mm
            margin = 10 * rl_mm
            right_x = PAGE_W - 2 * rl_mm
            c.setLineWidth(0.8)
            c.line(margin, top_line_y, right_x, top_line_y)
            
            divider_x = margin + 70 * rl_mm
            bottom_line_y = 12 * rl_mm
            c.setLineWidth(0.8)
            c.line(divider_x, top_line_y, divider_x, bottom_line_y)
            c.line(divider_x, top_line_y, right_x, top_line_y)
            c.line(right_x, top_line_y, right_x, bottom_line_y)
            c.line(divider_x, bottom_line_y, right_x, bottom_line_y)
            
            left_x = margin + 1 * rl_mm
            y = top_line_y - 8 * rl_mm
            
            def section_label(text, size=9, gap=5.2):
                nonlocal y
                c.setFont("Helvetica-Bold", size)
                c.drawString(left_x, y, text)
                y -= gap * rl_mm
            
            def doctor_entry(doc, gap=4.6, size=7.8):
                nonlocal y
                c.setFont("Helvetica", size)
                for line in (doc["name"], doc["role"], doc["reg"]):
                    c.drawString(left_x, y, line)
                    y -= gap * rl_mm
                y -= 1.5 * rl_mm
            
            section_label("Consultants :")
            for doc in CONSULTANTS:
                doctor_entry(doc)
            
            y -= 6 * rl_mm
            section_label("Visiting :")
            for doc in VISITING_DOCTORS:
                doctor_entry(doc)
            
            c.setFont("Helvetica", 8.5)
            c.drawCentredString(header_cx, 6 * rl_mm, CLINIC_HOURS)

        def generate_pdf(filepath: str):
            if not rl_canvas: return
            c = rl_canvas.Canvas(filepath, pagesize=(PAGE_W, PAGE_H))
            draw_letterhead(c)
            c.showPage()
            c.save()

        # ==============================================================
        # Build Tkinter workspace
        # ==============================================================
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)
        ws = self.app.workspace

        AVAIL_H = 600
        AVAIL_W = 500
        SCALE   = min(AVAIL_H / PAGE_H, AVAIL_W / PAGE_W)
        CW      = int(PAGE_W * SCALE)
        CH      = int(PAGE_H * SCALE)
        mm_px   = SCALE * 2.8346

        outer = tk.Frame(ws, bg="#c0c0c0")
        outer.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        vsb = tk.Scrollbar(outer, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(outer, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        cv = tk.Canvas(outer, bg="#c0c0c0", width=CW+10, height=CH+1,
                       scrollregion=(0, 0, CW + 20, CH + 20),
                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        cv.pack(fill="both", expand=True)
        vsb.config(command=cv.yview)
        hsb.config(command=cv.xview)

        canvas_width = CW + 950      # Same as the Canvas width
        OX = (canvas_width - CW) // 2
        OY = 10
        cv.create_rectangle(OX+4, OY+4, OX+CW+4, OY+CH+4, fill="#888888", outline="")
        cv.create_rectangle(OX, OY, OX+CW, OY+CH, fill="white", outline="#aaaaaa", width=1)

        def ppx(pt):  return OX + int(pt * SCALE)
        def ppy(pt):  return OY + int((PAGE_H - pt) * SCALE)
        def pcx():    return OX + CW // 2
        def smm(v):   return int(v * mm_px)

        logo_cx = ppx(30*rl_mm)
        logo_cy = ppy(PAGE_H - 20*rl_mm)
        logo_r  = smm(15)
        if os.path.isfile(LOGO_PATH):
            try:
                from PIL import Image as _PI, ImageTk as _ITk
                _img = _PI.open(LOGO_PATH)
                _img.thumbnail((logo_r*2, logo_r*2))
                self._lp_logo = _ITk.PhotoImage(_img)
                cv.create_image(logo_cx, logo_cy, image=self._lp_logo)
            except Exception:
                cv.create_oval(logo_cx-logo_r, logo_cy-logo_r,
                               logo_cx+logo_r, logo_cy+logo_r, outline="#555")
        else:
            cv.create_oval(logo_cx-logo_r, logo_cy-logo_r,
                           logo_cx+logo_r, logo_cy+logo_r, outline="#555")

        cv.create_text(pcx(), ppy(PAGE_H - 15*rl_mm), text=CLINIC_NAME,
                       font=("Times New Roman", max(10, smm(6)), "bold"), fill="#1a1a1a")
        cv.create_text(pcx(), ppy(PAGE_H - 22*rl_mm), text=CLINIC_ADDRESS,
                       font=("Arial", max(8, smm(3))), fill="#333")
        cv.create_text(ppx(PAGE_W - 28*rl_mm), ppy(PAGE_H - 30*rl_mm),text=f"{CLINIC_PHONE}",
                       font=("Arial", max(8, smm(3))), fill="#333")
        cv.create_text(ppx(PAGE_W - 32*rl_mm), ppy(PAGE_H - 37*rl_mm),text=f"{CLINIC_RESI}",
                       font=("Arial", max(8, smm(3))), fill="#333")

        rule_y   = ppy(PAGE_H - 47*rl_mm)
        marg_px  = ppx(10*rl_mm)
        right_px = OX + CW - smm(2)
        cv.create_line(marg_px, rule_y, right_px, rule_y, fill="#333", width=1)

        div_x = marg_px + smm(70)
        bot_y = ppy(12*rl_mm)
        cv.create_line(div_x, rule_y, div_x, bot_y, fill="#555", width=1)
        cv.create_rectangle(div_x, rule_y, right_px, bot_y, outline="#555", width=1)

        lx  = marg_px + smm(1)
        ly  = rule_y + smm(8)
        lh  = smm(4.6)
        lhs = smm(5.2)

        cv.create_text(lx, ly, text="Consultants :",
                       font=("Arial", max(7, smm(3)), "bold"), fill="#1a1a1a", anchor="nw")
        ly += lhs
        for doc in CONSULTANTS:
            cv.create_text(lx+smm(3), ly, text=doc["name"],
                           font=("Arial", max(6, smm(2.5))), fill="#1a1a1a", anchor="nw"); ly += lh
            cv.create_text(lx+smm(3), ly, text=doc["role"],
                           font=("Arial", max(5, smm(2))), fill="#333",    anchor="nw"); ly += lh
            cv.create_text(lx+smm(3), ly, text=doc["reg"],
                           font=("Arial", max(5, smm(2))), fill="#555",    anchor="nw"); ly += lh + smm(1.5)

        ly += smm(6)
        cv.create_text(lx, ly, text="Visiting :",
                       font=("Arial", max(7, smm(3)), "bold"), fill="#1a1a1a", anchor="nw")
        ly += lhs
        for doc in VISITING_DOCTORS:
            cv.create_text(lx+smm(3), ly, text=doc["name"],
                           font=("Arial", max(6, smm(2.5))), fill="#1a1a1a", anchor="nw"); ly += lh
            cv.create_text(lx+smm(3), ly, text=doc["role"],
                           font=("Arial", max(5, smm(2))), fill="#333",    anchor="nw"); ly += lh
            cv.create_text(lx+smm(3), ly, text=doc["reg"],
                           font=("Arial", max(5, smm(2))), fill="#555",    anchor="nw"); ly += lh + smm(1.5)

        cv.create_text(pcx(), ppy(6*rl_mm), text=CLINIC_HOURS,
                       font=("Arial", max(6, smm(2.5))), fill="#555")

        btn_bar = tk.Frame(ws)
        btn_bar.pack(pady=8)

        def _open_pdf(path):
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
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf", initialfile="Anupam_Dental_Letterhead.pdf",
                initialdir=SCRIPT_DIR, filetypes=[("PDF files", "*.pdf")],
                title="Save Letterhead PDF As")
            if not filepath: return
            try:
                generate_pdf(filepath)
                messagebox.showinfo("Done", f"Letterhead saved:\n{filepath}")
                _open_pdf(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"PDF generation failed:\n{exc}")

        def _print_now():
            if not reportlab_ok:
                messagebox.showerror("Missing Library",
                    "ReportLab is required.\nRun:  pip install reportlab")
                return
            tmp = os.path.join(SCRIPT_DIR, "_letterhead_temp.pdf")
            try:
                generate_pdf(tmp)
                _open_pdf(tmp)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not open PDF:\n{exc}")

        tk.Button(btn_bar, text="📄  Generate PDF", font=("Arial", 11), width=16,
                  bg="#1565C0", fg="white", command=_generate_pdf).grid(row=0, column=0, padx=8)
        tk.Button(btn_bar, text="🖨  Open / Print", font=("Arial", 11), width=16,
                  bg="#2E7D32", fg="white", command=_print_now).grid(row=0, column=1, padx=8)
        tk.Button(btn_bar, text="Close",            font=("Arial", 11), width=10,
                  command=self.close).grid(row=0, column=2, padx=8)

    

    def close(self):
        self.app.personal()
    def close(self):
        self.app.personal()
    def close(self):
        self.app.personal()
    def close(self):
        self.app.personal()
