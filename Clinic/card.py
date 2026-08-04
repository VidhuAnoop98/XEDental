from Clinic import case_details
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime 
import sqlite3
import os

def get_db_connection(app=None):
    if app and hasattr(app, "get_db_connection"):
        return app.get_db_connection()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return sqlite3.connect(os.path.join(script_dir, "dental.db"))

def init_db(app=None):
    conn = get_db_connection(app)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pid TEXT NOT NULL,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            age TEXT NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            doctor TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

class Card:
    def __init__(self, app):
        self.app = app
        init_db(app)
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(app.root, bd=3, relief="solid")
        self.app.workspace.pack(padx=10, pady=10, fill="both", expand=True)

    def idcard(self):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor
        from reportlab.lib.utils import ImageReader
        
        PAGE_W, PAGE_H = A4
        
        # ----------------------------------------------------------------------
        # Logo image - place "Dental_logo.png" next to this script (or point
        # LOGO_PATH elsewhere). A drawn placeholder is used if it's missing.
        # ----------------------------------------------------------------------
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        LOGO_PATH = os.path.join(SCRIPT_DIR, "Dental_logo.png")
        
        # ----------------------------------------------------------------------
        # Editable clinic data
        # ----------------------------------------------------------------------
        CLINIC_NAME = "ANUPAM DENTAL CLINIC"
        CLINIC_LINE = "West Gate Vaikom - 686141, Ph : 216878 Res : 216858"
        CLINIC_HOURS = "Clinic Hours :10:00 AM to 07:00 PM, Tuesday Holiday"
        FIELD_LABELS = ["Reg.No.", "PID", "Date", "Age", "Name", "Address"]
        
        # Reference aspect ratio taken from the original printed card (w / h)
        CARD_ASPECT = 716 / 492
        
        INK = HexColor("#1a1a1a")
        
        
        # ----------------------------------------------------------------------
        # Logo drawing (image with graceful fallback)
        # ----------------------------------------------------------------------
        def draw_logo(c: canvas.Canvas, cx: float, cy: float, box_w: float, box_h: float):
            """Draws the clinic logo centred at (cx, cy), fitted inside box_w x box_h."""
            if os.path.isfile(LOGO_PATH):
                img = ImageReader(LOGO_PATH)
                iw, ih = img.getSize()
                scale = min(box_w / iw, box_h / ih)
                w, h = iw * scale, ih * scale
                c.drawImage(
                    img,
                    cx - w / 2,
                    cy - h / 2,
                    width=w,
                    height=h,
                    mask="auto",
                    preserveAspectRatio=True,
                )
                return
        
            # ---- Fallback placeholder if the PNG can't be found ----
            r = min(box_w, box_h) / 2
            c.saveState()
            c.setStrokeColor(INK)
            c.setDash(1, 2)
            c.setLineWidth(0.7)
            c.circle(cx, cy, r, stroke=1, fill=0)
            c.circle(cx, cy, r - 1.5 * mm, stroke=1, fill=0)
            c.restoreState()
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", r * 0.22)
            c.drawCentredString(cx, cy + r * 0.15, "ANUPAM")
            c.setFont("Helvetica", r * 0.16)
            c.drawCentredString(cx, cy - r * 0.35, "DENTAL")
            c.drawCentredString(cx, cy - r * 0.60, "CLINIC")
        
        
        # ----------------------------------------------------------------------
        # Card drawing - all sizes are proportional to the card's own w / h.
        # ----------------------------------------------------------------------
        def draw_card(c: canvas.Canvas, x0: float, y0: float, w: float, h: float):
            """Draws one registration card inside the rectangle (x0, y0, w, h)."""
            c.setFillColor(INK)
            c.setStrokeColor(INK)
        
            def top_y(frac):
                """Convert a fraction-from-top (0=top edge, 1=bottom edge) to an
                absolute canvas y coordinate."""
                return y0 + h * (1 - frac)
        
            # ---------- outer card border ----------
            c.setLineWidth(0.4)
            c.roundRect(x0, y0, w, h, 2 * mm, stroke=1, fill=0)
        
            # ---------- title box ----------
            title_top = top_y(0.06)
            title_bottom = top_y(0.20)
            box_margin = w * 0.035
            c.setLineWidth(0.9)
            c.rect(x0 + box_margin, title_bottom, w - 2 * box_margin, title_top - title_bottom, stroke=1, fill=0)
            c.setFont("Times-Bold", h * 0.095)
            c.drawCentredString(x0 + w / 2, (title_top + title_bottom) / 2 - h * 0.028, CLINIC_NAME)
        
            # ---------- logo (top-right, alongside the field labels) ----------
            logo_cx = x0 + w * 0.685
            logo_cy = top_y(0.44)
            draw_logo(c, logo_cx, logo_cy, w * 0.30, h * 0.42)
        
            # ---------- field labels (left column) ----------
            field_x = x0 + w * 0.045
            field_fracs_top = 0.30
            field_fracs_bottom = 0.70
            n = len(FIELD_LABELS)
            step = (field_fracs_bottom - field_fracs_top) / (n - 1)
            c.setFont("Times-Roman", h * 0.062)
            
            field_values = ["", "", "", "", "", ""]
            if hasattr(self, "patient_data") and self.patient_data:
                pd = self.patient_data
                field_values = [
                    str(pd.get("regno", "")),
                    str(pd.get("patientid", "")),
                    datetime.now().strftime("%d-%m-%Y"),
                    str(pd.get("age", "")),
                    str(pd.get("patientname", "")),
                    f"{pd.get('address1', '')} {pd.get('address2', '')}".strip()
                ]
                
            for i, label in enumerate(FIELD_LABELS):
                frac = field_fracs_top + step * i
                c.drawString(field_x, top_y(frac), f"{label} : {field_values[i]}")
        
            # ---------- horizontal rule ----------
            rule_y = top_y(0.755)
            c.setLineWidth(0.8)
            c.line(x0 + w * 0.045, rule_y, x0 + w * 0.955, rule_y)
        
            # ---------- address / phone line ----------
            c.setFont("Times-Roman", h * 0.052)
            c.drawCentredString(x0 + w / 2, top_y(0.815), CLINIC_LINE)
        
            # ---------- footer box: clinic hours ----------
            footer_top = top_y(0.865)
            footer_bottom = top_y(0.955)
            c.setLineWidth(0.9)
            c.rect(x0 + box_margin, footer_bottom, w - 2 * box_margin, footer_top - footer_bottom, stroke=1, fill=0)
            c.setFont("Times-Roman", h * 0.052)
            c.drawCentredString(x0 + w / 2, (footer_top + footer_bottom) / 2 - h * 0.017, CLINIC_HOURS)
        
        
        def generate_pdf(filepath: str):
            """Creates the 1-page single-card PDF at the given filepath."""
            c = canvas.Canvas(filepath, pagesize=A4)
        
            card_w = 100 * mm      # 10 cm
            card_h = 80 * mm       # 8 cm

            # Top-right position
            # Center card on page
            x0 = (PAGE_W - card_w) / 2
            y0 = (PAGE_H - card_h) / 2
        
            draw_card(c, x0, y0, card_w, card_h)
            c.showPage()
            c.save()

        # Tkinter UI (Canvas Preview)
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

        canvas_width = CW + 950      
        OX = (canvas_width - CW) // 2
        OY = 10
        cv.create_rectangle(OX+4, OY+4, OX+CW+4, OY+CH+4, fill="#888888", outline="")
        cv.create_rectangle(OX, OY, OX+CW, OY+CH, fill="white", outline="#aaaaaa", width=1)

        def ppx(pt):  return OX + int(pt * SCALE)
        def ppy(pt):  return OY + int((PAGE_H - pt) * SCALE)

        # Calculate card dimensions (matching user updates)
        card_w = 100 * mm
        card_h = 80 * mm
                # Center card on PDF page
        c_x0 = (PAGE_W - card_w) / 2
        c_y0 = (PAGE_H - card_h) / 2
        
        # In Tkinter, ppy(c_y0 + card_h) is the top edge in Tkinter space
        tk_x0 = ppx(c_x0)
        tk_w  = int(card_w * SCALE)
        tk_h  = int(card_h * SCALE)
        tk_y0 = ppy(c_y0 + card_h)
        
        # Helper to map fraction to tk y
        def tk_top_y(frac):
            return tk_y0 + int(tk_h * frac)

        # Draw outer card border
        cv.create_rectangle(tk_x0, tk_y0, tk_x0+tk_w, tk_y0+tk_h, outline="#1a1a1a", width=1)

        # title box
        title_top = tk_top_y(0.06)
        title_bottom = tk_top_y(0.20)
        box_margin = int(tk_w * 0.035)
        cv.create_rectangle(tk_x0 + box_margin, title_top, tk_x0 + tk_w - box_margin, title_bottom, outline="#1a1a1a", width=1)
        
        cv.create_text(tk_x0 + tk_w // 2, (title_top + title_bottom) // 2, text=CLINIC_NAME,
                       font=("Times New Roman", max(10, int(tk_h * 0.08)), "bold"), fill="#1a1a1a")

        # logo
        logo_cx = tk_x0 + int(tk_w * 0.685)
        logo_cy = tk_top_y(0.44)
        box_w = int(tk_w * 0.30)
        box_h = int(tk_h * 0.42)
        logo_r = min(box_w, box_h) // 2
        
        if os.path.isfile(LOGO_PATH):
            try:
                from PIL import Image as _PI, ImageTk as _ITk
                _img = _PI.open(LOGO_PATH)
                _img.thumbnail((logo_r*2, logo_r*2))
                self._card_logo = _ITk.PhotoImage(_img)
                cv.create_image(logo_cx, logo_cy, image=self._card_logo)
            except Exception:
                cv.create_oval(logo_cx-logo_r, logo_cy-logo_r, logo_cx+logo_r, logo_cy+logo_r, outline="#1a1a1a")
        else:
            cv.create_oval(logo_cx-logo_r, logo_cy-logo_r, logo_cx+logo_r, logo_cy+logo_r, outline="#1a1a1a")
            cv.create_text(logo_cx, logo_cy, text="LOGO", font=("Helvetica", max(8, int(logo_r*0.4))), fill="#1a1a1a")

        # field labels
        field_x = tk_x0 + int(tk_w * 0.045)
        field_fracs_top = 0.30
        field_fracs_bottom = 0.70
        n = len(FIELD_LABELS)
        step = (field_fracs_bottom - field_fracs_top) / (n - 1)
        
        field_values = ["", "", "", "", "", ""]
        if hasattr(self, "patient_data") and self.patient_data:
            pd = self.patient_data
            field_values = [
                str(pd.get("regno", "")),
                str(pd.get("patientid", "")),
                datetime.now().strftime("%d-%m-%Y"),
                str(pd.get("age", "")),
                str(pd.get("patientname", "")),
                f"{pd.get('address1', '')} {pd.get('address2', '')}".strip()
            ]
            
        for i, label in enumerate(FIELD_LABELS):
            frac = field_fracs_top + step * i
            cv.create_text(field_x, tk_top_y(frac), text=f"{label} : {field_values[i]}", font=("Times New Roman", max(8, int(tk_h * 0.05))), anchor="nw", fill="#1a1a1a")

        # horizontal rule
        rule_y = tk_top_y(0.755)
        cv.create_line(tk_x0 + int(tk_w * 0.045), rule_y, tk_x0 + int(tk_w * 0.955), rule_y, fill="#1a1a1a", width=1)

        # address / phone line
        cv.create_text(tk_x0 + tk_w // 2, tk_top_y(0.815), text=CLINIC_LINE, font=("Times New Roman", max(7, int(tk_h * 0.045))), fill="#1a1a1a")

        # footer box
        footer_top = tk_top_y(0.865)
        footer_bottom = tk_top_y(0.955)
        cv.create_rectangle(tk_x0 + box_margin, footer_top, tk_x0 + tk_w - box_margin, footer_bottom, outline="#1a1a1a", width=1)
        cv.create_text(tk_x0 + tk_w // 2, (footer_top + footer_bottom) // 2, text=CLINIC_HOURS, font=("Times New Roman", max(7, int(tk_h * 0.045))), fill="#1a1a1a")

        # Buttons
        btn_bar = tk.Frame(ws)
        btn_bar.pack(pady=8)

        def _open_pdf(path):
            try:
                import subprocess
                import sys
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
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf", initialfile="Registration_ID_Card.pdf",
                initialdir=SCRIPT_DIR, filetypes=[("PDF files", "*.pdf")],
                title="Save Card PDF As")
            if not filepath: return
            try:
                generate_pdf(filepath)
                messagebox.showinfo("Done", f"Card saved:\n{filepath}")
                _open_pdf(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"PDF generation failed:\n{exc}")

        def _print_now():
            tmp = os.path.join(SCRIPT_DIR, "_card_temp.pdf")
            try:
                generate_pdf(tmp)
                _open_pdf(tmp)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not open PDF:\n{exc}")

        def close():
            self.app.registration()

        tk.Button(btn_bar, text="📄  Generate PDF", font=("Arial", 11), width=16,
                  bg="#1565C0", fg="white", command=_generate_pdf).grid(row=0, column=0, padx=8)
        tk.Button(btn_bar, text="🖨  Open / Print", font=("Arial", 11), width=16,
                  bg="#2E7D32", fg="white", command=_print_now).grid(row=0, column=1, padx=8)
        tk.Button(btn_bar, text="Close",            font=("Arial", 11), width=10,
                  command=close).grid(row=0, column=2, padx=8)
    
    def select_card(self):
        """Opens the 8‑up card sheet generator inside the main workspace.
        Clears the current workspace, builds the UI as a Frame, and uses the
        existing generate_pdf logic to create the PDF. Also adds a canvas preview
        of the 8‑up layout similar to the single‑card preview in `idcard`.
        """
        import os
        import tkinter as tk
        from tkinter import filedialog, messagebox
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.colors import HexColor
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas

        # Clear current workspace and set up a new frame
        self.app.clear_workspace()
        ws = tk.Frame(self.app.root, bd=3, relief="solid")
        ws.pack(padx=10, pady=10, fill="both", expand=True)
        self.app.workspace = ws

        # UI header
        tk.Label(ws, text="Anupam Dental Clinic", font=("Helvetica", 16, "bold")).pack(pady=(20, 5))
        tk.Label(
            ws,
            text="Generate an A4 sheet with 8 registration cards\n(2 columns x 4 rows) ready to print & cut.",
            font=("Helvetica", 10),
            justify="center",
        ).pack(pady=(0, 20))
        status_var = tk.StringVar(value="")

        # Button bar
        btn_bar = tk.Frame(ws)
        btn_bar.pack(pady=8)
        def on_generate():
            default_name = "Anupam_Dental_Clinic_8up_Cards.pdf"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=default_name,
                filetypes=[("PDF files", "*.pdf")],
                title="Save 8-Up Sheet PDF As",
            )
            if not filepath:
                return
            try:
                generate_pdf(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not generate PDF:\n{exc}")
                return
            status_var.set(f"Saved: {os.path.basename(filepath)}")
            messagebox.showinfo("Done", f"8‑up card sheet PDF saved to:\n{filepath}")
        tk.Button(
            btn_bar,
            text="Generate 8‑Up Sheet PDF",
            font=("Helvetica", 11, "bold"),
            bg="#2c5f8a",
            fg="white",
            padx=12,
            pady=8,
            command=on_generate,
        ).pack()
        tk.Label(ws, textvariable=status_var, fg="#2c5f8a").pack(pady=15)

        # ------------------------------------------------------------------
        # Canvas preview of the 8‑up layout (mirrors the PDF generation logic)
        # ------------------------------------------------------------------
        PAGE_W, PAGE_H = A4
        AVAIL_H = 600
        AVAIL_W = 500
        SCALE = min(AVAIL_H / PAGE_H, AVAIL_W / PAGE_W)
        CW = int(PAGE_W * SCALE)
        CH = int(PAGE_H * SCALE)
        outer = tk.Frame(ws, bg="#c0c0c0")
        outer.pack(fill="both", expand=True, padx=10, pady=(6, 0))
        vsb = tk.Scrollbar(outer, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(outer, orient="horizontal")
        hsb.pack(side="bottom", fill="x")
        cv = tk.Canvas(
            outer,
            bg="#c0c0c0",
            width=CW + 10,
            height=CH + 1,
            scrollregion=(0, 0, CW + 20, CH + 20),
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )
        cv.pack(fill="both", expand=True)
        vsb.config(command=cv.yview)
        hsb.config(command=cv.xview)

        canvas_width = CW + 950
        OX = (canvas_width - CW) // 2
        OY = 10
        cv.create_rectangle(OX + 4, OY + 4, OX + CW + 4, OY + CH + 4, fill="#888888", outline="")
        cv.create_rectangle(OX, OY, OX + CW, OY + CH, fill="white", outline="#aaaaaa", width=1)

        def ppx(pt):
            return OX + int(pt * SCALE)

        def ppy(pt):
            return OY + int((PAGE_H - pt) * SCALE)

        # Helper to map fraction to Tk y coordinate (top‑down)
        def tk_top_y(frac):
            return ppy(0) - int(frac * CH)  # ppy(0) is top edge in Tk coords

        # Draw the 8 cards using the same geometry as the PDF generation
        margin = 5 * mm
        col_gap = 5 * mm
        row_gap = 5 * mm
        cols, rows = 2, 4
        card_w = (PAGE_W - 2 * margin - col_gap) / cols
        card_h = card_w / CARD_ASPECT
        for r in range(rows):
            for c in range(cols):
                # Calculate PDF‑space position
                x0 = margin + c * (card_w + col_gap)
                y_top = PAGE_H - margin - r * (card_h + row_gap)
                y0 = y_top - card_h
                # Convert to Tk coordinates
                tk_x0 = ppx(x0)
                tk_y0 = ppy(y_top)
                tk_w = int(card_w * SCALE)
                tk_h = int(card_h * SCALE)
                # Draw card rectangle
                cv.create_rectangle(tk_x0, tk_y0 - tk_h, tk_x0 + tk_w, tk_y0, outline="#1a1a1a", width=1)
                # Title box
                title_top = tk_y0 - int(0.06 * tk_h)
                title_bottom = tk_y0 - int(0.20 * tk_h)
                box_margin = int(tk_w * 0.035)
                cv.create_rectangle(tk_x0 + box_margin, title_bottom, tk_x0 + tk_w - box_margin, title_top, outline="#1a1a1a", width=1)
                cv.create_text(tk_x0 + tk_w // 2, (title_top + title_bottom) // 2, text=CLINIC_NAME,
                               font=("Times New Roman", max(10, int(tk_h * 0.08)), "bold"), fill="#1a1a1a")
                # Logo placeholder (same as idcard preview)
                logo_cx = tk_x0 + int(tk_w * 0.685)
                logo_cy = tk_top_y(0.44)
                box_w = int(tk_w * 0.30)
                box_h = int(tk_h * 0.42)
                logo_r = min(box_w, box_h) // 2
                if os.path.isfile(LOGO_PATH):
                    try:
                        from PIL import Image as _PI, ImageTk as _ITk
                        _img = _PI.open(LOGO_PATH)
                        _img.thumbnail((logo_r * 2, logo_r * 2))
                        self._card_logo = _ITk.PhotoImage(_img)
                        cv.create_image(logo_cx, logo_cy, image=self._card_logo)
                    except Exception:
                        cv.create_oval(logo_cx - logo_r, logo_cy - logo_r, logo_cx + logo_r, logo_cy + logo_r, outline="#1a1a1a")
                else:
                    cv.create_oval(logo_cx - logo_r, logo_cy - logo_r, logo_cx + logo_r, logo_cy + logo_r, outline="#1a1a1a")
                    cv.create_text(logo_cx, logo_cy, text="LOGO", font=("Helvetica", max(8, int(logo_r * 0.4)), "bold"), fill="#1a1a1a")
                # Field labels (reuse the same logic as idcard preview)
                field_x = tk_x0 + int(tk_w * 0.045)
                field_fracs_top = 0.30
                field_fracs_bottom = 0.70
                n = len(FIELD_LABELS)
                step = (field_fracs_bottom - field_fracs_top) / (n - 1)
                field_values = ["", "", "", "", "", ""]
                if hasattr(self, "patient_data") and self.patient_data:
                    pd = self.patient_data
                    field_values = [
                        str(pd.get("regno", "")),
                        str(pd.get("patientid", "")),
                        datetime.now().strftime("%d-%m-%Y"),
                        str(pd.get("age", "")),
                        str(pd.get("patientname", "")),
                        f"{pd.get('address1', '')} {pd.get('address2', '')}".strip(),
                    ]
                for i, label in enumerate(FIELD_LABELS):
                    frac = field_fracs_top + step * i
                    cv.create_text(field_x, tk_top_y(frac), text=f"{label} : {field_values[i]}",
                                   font=("Times New Roman", max(8, int(tk_h * 0.05))), anchor="nw", fill="#1a1a1a")
                # Horizontal rule
                rule_y = tk_top_y(0.755)
                cv.create_line(tk_x0 + int(tk_w * 0.045), rule_y, tk_x0 + int(tk_w * 0.955), rule_y, fill="#1a1a1a", width=1)
                # Address / phone line
                cv.create_text(tk_x0 + tk_w // 2, tk_top_y(0.815), text=CLINIC_LINE,
                               font=("Times New Roman", max(7, int(tk_h * 0.045))), fill="#1a1a1a")
                # Footer box
                footer_top = tk_top_y(0.865)
                footer_bottom = tk_top_y(0.955)
                cv.create_rectangle(tk_x0 + box_margin, footer_bottom, tk_x0 + tk_w - box_margin, footer_top,
                                    outline="#1a1a1a", width=1)
                cv.create_text(tk_x0 + tk_w // 2, (footer_top + footer_bottom) // 2, text=CLINIC_HOURS,
                               font=("Times New Roman", max(7, int(tk_h * 0.045))), fill="#1a1a1a")
        # End of preview canvas
        # ------------------------------------------------------------------
        # End of select_card implementation
        
        PAGE_W, PAGE_H = A4
        
        # ----------------------------------------------------------------------
        # Logo image - place "Dental_logo.png" next to this script (or point
        # LOGO_PATH elsewhere). A drawn placeholder is used if it's missing.
        # ----------------------------------------------------------------------
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        LOGO_PATH = os.path.join(SCRIPT_DIR, "Dental_logo.png")
        
        # ----------------------------------------------------------------------
        # Editable clinic data
        # ----------------------------------------------------------------------
        CLINIC_NAME = "ANUPAM DENTAL CLINIC"
        CLINIC_LINE = "West Gate Vaikom - 686141, Ph : 216878 Res : 216858"
        CLINIC_HOURS = "Clinic Hours :10:00 AM to 07:00 PM, Tuesday Holiday"
        FIELD_LABELS = ["Reg.No.", "PID", "Date", "Age", "Name", "Address"]
        
        # Reference aspect ratio taken from the original printed card (w / h)
        CARD_ASPECT = 716 / 492
        
        INK = HexColor("#1a1a1a")
        
        
        # ----------------------------------------------------------------------
        # Logo drawing (image with graceful fallback)
        # ----------------------------------------------------------------------
        def draw_logo(c: canvas.Canvas, cx: float, cy: float, box_w: float, box_h: float):
            """Draws the clinic logo centred at (cx, cy), fitted inside box_w x box_h."""
            if os.path.isfile(LOGO_PATH):
                img = ImageReader(LOGO_PATH)
                iw, ih = img.getSize()
                scale = min(box_w / iw, box_h / ih)
                w, h = iw * scale, ih * scale
                c.drawImage(
                    img,
                    cx - w / 2,
                    cy - h / 2,
                    width=w,
                    height=h,
                    mask="auto",
                    preserveAspectRatio=True,
                )
                return
        
            # ---- Fallback placeholder if the PNG can't be found ----
            r = min(box_w, box_h) / 2
            c.saveState()
            c.setStrokeColor(INK)
            c.setDash(1, 2)
            c.setLineWidth(0.7)
            c.circle(cx, cy, r, stroke=1, fill=0)
            c.circle(cx, cy, r - 1.5 * mm, stroke=1, fill=0)
            c.restoreState()
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", r * 0.22)
            c.drawCentredString(cx, cy + r * 0.15, "ANUPAM")
            c.setFont("Helvetica", r * 0.16)
            c.drawCentredString(cx, cy - r * 0.35, "DENTAL")
            c.drawCentredString(cx, cy - r * 0.60, "CLINIC")
        
        
        # ----------------------------------------------------------------------
        # Card drawing - all sizes are proportional to the card's own w / h.
        # ----------------------------------------------------------------------
        def draw_card(c: canvas.Canvas, x0: float, y0: float, w: float, h: float):
            """Draws one registration card inside the rectangle (x0, y0, w, h)."""
            c.setFillColor(INK)
            c.setStrokeColor(INK)
        
            def top_y(frac):
                """Convert a fraction-from-top (0=top edge, 1=bottom edge) to an
                absolute canvas y coordinate."""
                return y0 + h * (1 - frac)
        
            # ---------- outer card border (cut guide) ----------
            c.setLineWidth(0.4)
            c.roundRect(x0, y0, w, h, 2 * mm, stroke=1, fill=0)
        
            # ---------- title box ----------
            title_top = top_y(0.06)
            title_bottom = top_y(0.20)
            box_margin = w * 0.035
            c.setLineWidth(0.9)
            c.rect(x0 + box_margin, title_bottom, w - 2 * box_margin, title_top - title_bottom, stroke=1, fill=0)
            c.setFont("Times-Bold", h * 0.095)
            c.drawCentredString(x0 + w / 2, (title_top + title_bottom) / 2 - h * 0.028, CLINIC_NAME)
        
            # ---------- logo (top-right, alongside the field labels) ----------
            logo_cx = x0 + w * 0.685
            logo_cy = top_y(0.44)
            draw_logo(c, logo_cx, logo_cy, w * 0.30, h * 0.42)
        
            # ---------- field labels (left column) ----------
            field_x = x0 + w * 0.045
            field_fracs_top = 0.30
            field_fracs_bottom = 0.70
            n = len(FIELD_LABELS)
            step = (field_fracs_bottom - field_fracs_top) / (n - 1)
            c.setFont("Times-Roman", h * 0.062)
            for i, label in enumerate(FIELD_LABELS):
                frac = field_fracs_top + step * i
                c.drawString(field_x, top_y(frac), label)
        
            # ---------- horizontal rule ----------
            rule_y = top_y(0.755)
            c.setLineWidth(0.8)
            c.line(x0 + w * 0.045, rule_y, x0 + w * 0.955, rule_y)
        
            # ---------- address / phone line ----------
            c.setFont("Times-Roman", h * 0.052)
            c.drawCentredString(x0 + w / 2, top_y(0.815), CLINIC_LINE)
        
            # ---------- footer box: clinic hours ----------
            footer_top = top_y(0.865)
            footer_bottom = top_y(0.955)
            c.setLineWidth(0.9)
            c.rect(x0 + box_margin, footer_bottom, w - 2 * box_margin, footer_top - footer_bottom, stroke=1, fill=0)
            c.setFont("Times-Roman", h * 0.052)
            c.drawCentredString(x0 + w / 2, (footer_top + footer_bottom) / 2 - h * 0.017, CLINIC_HOURS)
        
        
        def generate_pdf(filepath: str):
            """Creates the 1-page 8-up card sheet PDF at the given filepath."""
            c = canvas.Canvas(filepath, pagesize=A4)
        
            margin = 5 * mm
            col_gap = 5 * mm
            row_gap = 5 * mm
            cols, rows = 2, 4
        
            card_w = (PAGE_W - 2 * margin - col_gap) / cols
            card_h = card_w / CARD_ASPECT
        
            grid_h = rows * card_h + (rows - 1) * row_gap
            top_margin = margin + (PAGE_H - 2 * margin - grid_h) / 2  # vertically centre the grid
        
            for r in range(rows):
                for col in range(cols):
                    x0 = margin + col * (card_w + col_gap)
                    y_top = PAGE_H - top_margin - r * (card_h + row_gap)
                    y0 = y_top - card_h
                    draw_card(c, x0, y0, card_w, card_h)
        
            c.showPage()
            c.save()
        
        
        # ----------------------------------------------------------------------
        # Tkinter GUI
        # ----------------------------------------------------------------------
        class EightCardApp(tk.Tk):
            def __init__(self):
                super().__init__()
                self.title("Anupam Dental Clinic - 8-Up Card Sheet Generator")
                self.geometry("420x220")
                self.resizable(False, False)
        
                tk.Label(
                    self,
                    text="Anupam Dental Clinic",
                    font=("Helvetica", 16, "bold"),
                ).pack(pady=(20, 5))
        
                tk.Label(
                    self,
                    text="Generate an A4 sheet with 8 registration cards\n(2 columns x 4 rows) ready to print & cut.",
                    font=("Helvetica", 10),
                    justify="center",
                ).pack(pady=(0, 20))
        
                tk.Button(
                    self,
                    text="Generate 8-Up Sheet PDF",
                    font=("Helvetica", 11, "bold"),
                    bg="#2c5f8a",
                    fg="white",
                    padx=12,
                    pady=8,
                    command=self.on_generate,
                ).pack()
        
                self.status_var = tk.StringVar(value="")
                tk.Label(self, textvariable=self.status_var, fg="#2c5f8a").pack(pady=15)
        
            def on_generate(self):
                default_name = "Anupam_Dental_Clinic_8up_Cards.pdf"
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    initialfile=default_name,
                    filetypes=[("PDF files", "*.pdf")],
                    title="Save 8-Up Sheet PDF As",
                )
                if not filepath:
                    return  # user cancelled
        
                try:
                    generate_pdf(filepath)
                except Exception as exc:
                    messagebox.showerror("Error", f"Could not generate PDF:\n{exc}")
                    return
        
                self.status_var.set(f"Saved: {os.path.basename(filepath)}")
                messagebox.showinfo("Done", f"8-up card sheet PDF saved to:\n{filepath}")