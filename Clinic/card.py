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

def get_clinic_card_info(app=None):
    try:
        conn = get_db_connection(app)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM Clinic_Settings")
        settings = dict(cursor.fetchall())
        conn.close()
    except Exception:
        settings = {}

    clinic_name = settings.get("clinic_name", "ANUPAM DENTAL CLINIC").strip()
    if not clinic_name:
        clinic_name = "ANUPAM DENTAL CLINIC"

    mobile = settings.get("clinic_mobile", "9446046868").strip()
    if not mobile:
        mobile = "9446046868"

    clinic_line = f"West Gate Vaikom - 686141, Ph : {mobile}"

    open_time = settings.get("clinic_open_time", "10:00 AM").strip()
    close_time = settings.get("clinic_close_time", "07:00 PM").strip()
    holiday = settings.get("clinic_holiday", "Tuesday Holiday").strip()

    if holiday:
        clinic_hours = f"Clinic Hours :{open_time} to {close_time}, {holiday}"
    else:
        clinic_hours = f"Clinic Hours :{open_time} to {close_time}"

    return clinic_name, clinic_line, clinic_hours

def convert_pdf_to_docx(pdf_path, docx_path=None):
    """Converts a generated PDF card file into an editable MS Word (.docx) document."""
    if not docx_path:
        docx_path = os.path.splitext(pdf_path)[0] + ".docx"

    target_path = docx_path
    counter = 1
    while True:
        try:
            if os.path.exists(target_path):
                with open(target_path, "a"):
                    pass
            break
        except (PermissionError, IOError):
            base, ext = os.path.splitext(docx_path)
            target_path = f"{base}_{counter}{ext}"
            counter += 1

    try:
        from pdf2docx import Converter
        cv = Converter(pdf_path)
        cv.convert(target_path)
        cv.close()
        return target_path
    except Exception as exc:
        print(f"pdf2docx conversion error: {exc}")
        return target_path

def open_file(filepath):
    """Opens a PDF or DOCX file using the system default application."""
    try:
        import subprocess, sys
        if hasattr(os, "startfile"):
            os.startfile(filepath)
        elif sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", filepath])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", filepath])
        else:
            subprocess.Popen(["cmd", "/c", "start", "", filepath])
    except Exception as exc:
        messagebox.showwarning("Open File", f"Could not open file automatically.\n{exc}")

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
        # Dynamic clinic data from Clinic_Settings
        # ----------------------------------------------------------------------
        CLINIC_NAME, CLINIC_LINE, CLINIC_HOURS = get_clinic_card_info(self.app)
        FIELD_LABELS = ["Reg No",  "PID", "Date", "Age", "Name", "Address"]
        
        # Reference aspect ratio taken from the original printed card (w / h)
        CARD_ASPECT = 1716 / 492
        
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
            c.rect(x0, y0, w, h, stroke=1, fill=0)
        
            # ---------- title box ----------
            title_top = top_y(0.06)
            title_bottom = top_y(0.20)
            box_margin = w * 0.035
            c.setLineWidth(0.9)
            c.rect(x0 + box_margin, title_bottom, w - 2 * box_margin, title_top - title_bottom, stroke=1, fill=0)
            c.setFont("Times-Bold", h * 0.095)
            c.drawCentredString(x0 + w / 2, (title_top + title_bottom) / 2 - h * 0.028, CLINIC_NAME)
        
            # ---------- logo (top-right, alongside the field labels) ----------
            logo_cx = x0 + w * 0.820
            logo_cy = top_y(0.40)
            draw_logo(c, logo_cx, logo_cy, w * 0.25, h * 0.30)
        
            # ---------- field labels (left column) ----------
            field_x = x0 + w * 0.045
            field_fracs_top = 0.30
            field_fracs_bottom = 0.70
            n = len(FIELD_LABELS)
            step = (field_fracs_bottom - field_fracs_top) / (n - 1)
            c.setFont("Times-Roman", h * 0.062)
            
            field_values = ["", "", "", "", "", ""]
            gender_val = ""
            if hasattr(self, "patient_data") and self.patient_data:
                pd = self.patient_data
                gender_val = str(pd.get("gender", ""))
                if not gender_val:
                    name_lower = str(pd.get("patientname", "")).lower().strip()
                    if name_lower.startswith("mr.") or name_lower.startswith("mr ") or name_lower.startswith("master ") or name_lower.startswith("master."):
                        gender_val = "Male"
                    elif name_lower.startswith("mrs.") or name_lower.startswith("mrs ") or name_lower.startswith("ms.") or name_lower.startswith("ms ") or name_lower.startswith("miss ") or name_lower.startswith("miss."):
                        gender_val = "Female"
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
                y_pos = top_y(frac)
                c.drawString(field_x, y_pos, f"{label} : {field_values[i]}")
                if label == "Age":
                    c.drawString(x0 + w * 0.25, y_pos, f"Gender : {gender_val}")
        
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
        
            card_w = 85.6 * mm     # CR80 standard width
            card_h = 54.0 * mm     # CR80 standard height

            # Top-left with margin
            x0 = 5 * mm
            y0 = PAGE_H - card_h - 5 * mm 
        
            draw_card(c, x0, y0, card_w, card_h)
            c.showPage()
            c.save()

        # Tkinter UI (Canvas Preview)
        ws = self.app.workspace

        # Use card dimensions for scaling so card fills the preview
        CARD_W_MM = 85.6
        CARD_H_MM = 54.0
        AVAIL_W = 560   # pixels available for preview
        AVAIL_H = 380   # pixels available for preview
        from reportlab.lib.units import mm as _mm
        _card_w_pt = CARD_W_MM * _mm
        _card_h_pt = CARD_H_MM * _mm
        base_scale = min(AVAIL_W / _card_w_pt, AVAIL_H / _card_h_pt)
        self.preview_scale = base_scale

        outer = tk.Frame(ws, bg="#c0c0c0")
        outer.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        vsb = tk.Scrollbar(outer, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(outer, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        init_cw = int(_card_w_pt * base_scale) + 60
        init_ch = int(_card_h_pt * base_scale) + 30
        cv = tk.Canvas(outer, bg="#c0c0c0", width=init_cw, height=init_ch,
                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        cv.pack(fill="both", expand=True)
        vsb.config(command=cv.yview)
        hsb.config(command=cv.xview)

        def draw_page_preview():
            cv.delete("all")
            scale = self.preview_scale
            card_w = CARD_W_MM * mm
            card_h = CARD_H_MM * mm
            tk_w  = int(card_w * scale)
            tk_h  = int(card_h * scale)
            canvas_vw = tk_w + 60
            canvas_vh = tk_h + 30
            OX = (canvas_vw - tk_w) // 2
            OY = 10
            cv.config(scrollregion=(0, 0, canvas_vw, canvas_vh))

            # Card shadow + card background
            cv.create_rectangle(OX+3, OY+3, OX+tk_w+3, OY+tk_h+3, fill="#888888", outline="")
            cv.create_rectangle(OX, OY, OX+tk_w, OY+tk_h, fill="white", outline="#aaaaaa", width=1)

            tk_x0 = OX
            tk_y0 = OY

            def tk_top_y(frac):
                return tk_y0 + int(tk_h * frac)

            cv.create_rectangle(tk_x0, tk_y0, tk_x0+tk_w, tk_y0+tk_h, outline="#1a1a1a", width=1)

            title_top = tk_top_y(0.06)
            title_bottom = tk_top_y(0.20)
            box_margin = int(tk_w * 0.035)
            cv.create_rectangle(tk_x0 + box_margin, title_top, tk_x0 + tk_w - box_margin, title_bottom, outline="#1a1a1a", width=1)
            
            cv.create_text(tk_x0 + tk_w // 2, (title_top + title_bottom) // 2, text=CLINIC_NAME,
                           font=("Times New Roman", max(6, int(tk_h * 0.08)), "bold"), fill="#1a1a1a")

            logo_cx = tk_x0 + int(tk_w * 0.820)
            logo_cy = tk_top_y(0.40)
            box_w = int(tk_w * 0.50)
            box_h = int(tk_h * 0.30)
            logo_r = min(box_w, box_h) // 2
            
            if os.path.isfile(LOGO_PATH):
                try:
                    from PIL import Image as _PI, ImageTk as _ITk
                    _img = _PI.open(LOGO_PATH)
                    _img.thumbnail((box_w, box_h))
                    self._card_logo = _ITk.PhotoImage(_img)
                    cv.create_image(logo_cx, logo_cy, image=self._card_logo)
                except Exception:
                    cv.create_oval(logo_cx-logo_r, logo_cy-logo_r, logo_cx+logo_r, logo_cy+logo_r, outline="#1a1a1a")
            else:
                cv.create_oval(logo_cx-logo_r, logo_cy-logo_r, logo_cx+logo_r, logo_cy+logo_r, outline="#1a1a1a")
                cv.create_text(logo_cx, logo_cy, text="LOGO", font=("Helvetica", max(6, int(logo_r*0.4))), fill="#1a1a1a")

            field_x = tk_x0 + int(tk_w * 0.045)
            field_fracs_top = 0.25
            field_fracs_bottom = 0.65
            n = len(FIELD_LABELS)
            step = (field_fracs_bottom - field_fracs_top) / (n - 1)
            
            field_values = ["", "", "", "", "", ""]
            gender_val = ""
            if hasattr(self, "patient_data") and self.patient_data:
                pd = self.patient_data
                gender_val = str(pd.get("gender", ""))
                if not gender_val:
                    name_lower = str(pd.get("patientname", "")).lower().strip()
                    if name_lower.startswith("mr.") or name_lower.startswith("mr ") or name_lower.startswith("master ") or name_lower.startswith("master."):
                        gender_val = "Male"
                    elif name_lower.startswith("mrs.") or name_lower.startswith("mrs ") or name_lower.startswith("ms.") or name_lower.startswith("ms ") or name_lower.startswith("miss ") or name_lower.startswith("miss."):
                        gender_val = "Female"
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
                fy = tk_top_y(frac)
                cv.create_text(field_x, fy, text=f"{label} : {field_values[i]}", font=("Times New Roman", max(6, int(tk_h * 0.05))), anchor="nw", fill="#1a1a1a")
                if label == "Age":
                    cv.create_text(tk_x0 + int(tk_w * 0.25), fy, text=f"Gender : {gender_val}", font=("Times New Roman", max(6, int(tk_h * 0.05))), anchor="nw", fill="#1a1a1a")

            rule_y = tk_top_y(0.755)
            cv.create_line(tk_x0 + int(tk_w * 0.045), rule_y, tk_x0 + int(tk_w * 0.955), rule_y, fill="#1a1a1a", width=1)

            cv.create_text(tk_x0 + tk_w // 2, tk_top_y(0.815), text=CLINIC_LINE, font=("Times New Roman", max(5, int(tk_h * 0.045))), fill="#1a1a1a")

            footer_top = tk_top_y(0.865)
            footer_bottom = tk_top_y(0.955)
            cv.create_rectangle(tk_x0 + box_margin, footer_top, tk_x0 + tk_w - box_margin, footer_bottom, outline="#1a1a1a", width=1)
            cv.create_text(tk_x0 + tk_w // 2, (footer_top + footer_bottom) // 2, text=CLINIC_HOURS, font=("Times New Roman", max(5, int(tk_h * 0.045))), fill="#1a1a1a")

            try:
                zoom_lbl.config(text=f"{int(self.preview_scale / base_scale * 100)}%")
            except Exception:
                pass

        # ── zoom ─────────────────────────────────────────────────────────────
        def zoom_in():
            if self.preview_scale < 3.0:
                self.preview_scale = round(min(3.0, self.preview_scale + 0.1), 2)
                draw_page_preview()

        def zoom_out():
            if self.preview_scale > 0.2:
                self.preview_scale = round(max(0.2, self.preview_scale - 0.1), 2)
                draw_page_preview()

        def on_mouse_wheel(event):
            if getattr(event, "delta", 0) > 0 or getattr(event, "num", 0) == 4:
                zoom_in()
            else:
                zoom_out()
            return "break"

        cv.bind("<MouseWheel>", on_mouse_wheel)
        cv.bind("<Button-4>",   on_mouse_wheel)
        cv.bind("<Button-5>",   on_mouse_wheel)

        # ── control bar ──────────────────────────────────────────────────────
        ctrl_frame = tk.Frame(ws)
        ctrl_frame.pack(fill="x", pady=4)

        tk.Button(ctrl_frame, text="-", font=("Arial", 11, "bold"),
                  width=3, command=zoom_out).pack(side="left", padx=4)
        zoom_lbl = tk.Label(ctrl_frame, text="100%",
                            font=("Arial", 10), width=6)
        zoom_lbl.pack(side="left", padx=2)
        tk.Button(ctrl_frame, text="+", font=("Arial", 11, "bold"),
                  width=3, command=zoom_in).pack(side="left", padx=4)

        # Buttons
        btn_bar = tk.Frame(ws)
        btn_bar.pack(pady=8)

        def _open_pdf(path):
            open_file(path)

        def _generate_pdf():
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf", initialfile="Registration_ID_Card.pdf",
                initialdir=SCRIPT_DIR, filetypes=[("PDF files", "*.pdf")],
                title="Save Card PDF As")
            if not filepath: return
            try:
                generate_pdf(filepath)
                docx_path = convert_pdf_to_docx(filepath)
                messagebox.showinfo("Done", f"Card saved successfully:\n📄 PDF: {filepath}\n📝 Word: {docx_path}")
                _open_pdf(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"PDF generation failed:\n{exc}")

        def _generate_word():
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".docx", initialfile="Registration_ID_Card.docx",
                initialdir=SCRIPT_DIR, filetypes=[("Word Document", "*.docx")],
                title="Save Card Word Document As")
            if not filepath: return
            try:
                tmp_pdf = os.path.join(SCRIPT_DIR, "_card_temp.pdf")
                generate_pdf(tmp_pdf)
                convert_pdf_to_docx(tmp_pdf, filepath)
                messagebox.showinfo("Done", f"Word Card saved:\n{filepath}")
                open_file(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"Word generation failed:\n{exc}")

        def _print_now():
            tmp = os.path.join(SCRIPT_DIR, "_card_temp.pdf")
            try:
                generate_pdf(tmp)
                convert_pdf_to_docx(tmp)
                _open_pdf(tmp)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not open file:\n{exc}")

        def close():
            from registration import Registration
            r = Registration(self.app)
            r.registration_workspace()

        tk.Button(btn_bar, text="📄 Generate PDF", font=("Arial", 11), width=14,
                  bg="#1565C0", fg="white", command=_generate_pdf).grid(row=0, column=0, padx=6)
        tk.Button(btn_bar, text="📝 Generate Word", font=("Arial", 11), width=14,
                  bg="#673AB7", fg="white", command=_generate_word).grid(row=0, column=1, padx=6)
        tk.Button(btn_bar, text="🖨 Open / Print", font=("Arial", 11), width=14,
                  bg="#2E7D32", fg="white", command=_print_now).grid(row=0, column=2, padx=6)
        tk.Button(btn_bar, text="Close",            font=("Arial", 11), width=10,
                  bg="#ED350E", fg="white", command=close).grid(row=0, column=3, padx=6)
                  
        draw_page_preview()
    
    def select_card(self):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.colors import HexColor
        from reportlab.lib.utils import ImageReader

        PAGE_W, PAGE_H = A4

        SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
        LOGO_PATH   = os.path.join(SCRIPT_DIR, "Dental_logo.png")

        CLINIC_NAME, CLINIC_LINE, CLINIC_HOURS = get_clinic_card_info(self.app)
        FIELD_LABELS = ["Reg No", "PID", "Date", "Age", "Name", "Address"]
        CARD_ASPECT  = 716 / 492
        INK          = HexColor("#1a1a1a")

        # ── 8-up layout geometry (mirrors the PDF) ────────────────────────────
        MARGIN     = 5 * mm
        COL_GAP    = 5 * mm
        ROW_GAP    = 5 * mm
        COLS, ROWS = 2, 4
        CARD_W     = (PAGE_W - 2 * MARGIN - COL_GAP) / COLS
        CARD_H     = CARD_W / CARD_ASPECT
        GRID_H     = ROWS * CARD_H + (ROWS - 1) * ROW_GAP
        TOP_MARGIN = MARGIN + (PAGE_H - 2 * MARGIN - GRID_H) / 2

        # ── PDF helpers ───────────────────────────────────────────────────────
        def _pdf_draw_logo(c, cx, cy, box_w, box_h):
            if os.path.isfile(LOGO_PATH):
                try:
                    img = ImageReader(LOGO_PATH)
                    iw, ih = img.getSize()
                    s = min(box_w / iw, box_h / ih)
                    w2, h2 = iw * s, ih * s
                    c.drawImage(img, cx - w2/2, cy - h2/2,
                                width=w2, height=h2,
                                mask="auto", preserveAspectRatio=True)
                    return
                except Exception:
                    pass
            r = min(box_w, box_h) / 2
            c.saveState()
            c.setStrokeColor(INK); c.setDash(1, 2); c.setLineWidth(0.7)
            c.circle(cx, cy, r, stroke=1, fill=0)
            c.circle(cx, cy, r - 1.5*mm, stroke=1, fill=0)
            c.restoreState()
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", r * 0.22)
            c.drawCentredString(cx, cy + r*0.15, "ANUPAM")
            c.setFont("Helvetica", r * 0.16)
            c.drawCentredString(cx, cy - r*0.35, "DENTAL")
            c.drawCentredString(cx, cy - r*0.60, "CLINIC")

        def _pdf_draw_one_card(c, x0, y0, w, h):
            c.setFillColor(INK); c.setStrokeColor(INK)

            def top_y(frac):
                return y0 + h * (1 - frac)

            c.setLineWidth(0.4)
            c.rect(x0, y0, w, h, stroke=1, fill=0)
            tt = top_y(0.06); tb = top_y(0.20)
            bm = w * 0.035
            c.setLineWidth(0.9)
            c.rect(x0+bm, tb, w-2*bm, tt-tb, stroke=1, fill=0)
            c.setFont("Times-Bold", h*0.095)
            c.drawCentredString(x0+w/2, (tt+tb)/2 - h*0.028, CLINIC_NAME)

            _pdf_draw_logo(c, x0+w*0.820, top_y(0.40), w*0.17, h*0.42)

            fx = x0 + w*0.045
            n  = len(FIELD_LABELS)
            step = (0.70 - 0.30) / (n - 1)
            c.setFont("Times-Roman", h*0.062)
            field_values = ["", "", "", "", "", ""]
            gender_val = ""
            if hasattr(self, "patient_data") and self.patient_data:
                pd2 = self.patient_data
                gender_val = str(pd2.get("gender", ""))
                if not gender_val:
                    name_lower = str(pd2.get("patientname", "")).lower().strip()
                    if name_lower.startswith("mr.") or name_lower.startswith("mr ") or name_lower.startswith("master ") or name_lower.startswith("master."):
                        gender_val = "Male"
                    elif name_lower.startswith("mrs.") or name_lower.startswith("mrs ") or name_lower.startswith("ms.") or name_lower.startswith("ms ") or name_lower.startswith("miss ") or name_lower.startswith("miss."):
                        gender_val = "Female"
                field_values = [
                    str(pd2.get("regno", "")),
                    str(pd2.get("patientid", "")),
                    datetime.now().strftime("%d-%m-%Y"),
                    str(pd2.get("age", "")),
                    str(pd2.get("patientname", "")),
                    (str(pd2.get("address1", "")) + " " +
                     str(pd2.get("address2", ""))).strip(),
                ]
            for i, label in enumerate(FIELD_LABELS):
                y_pos = top_y(0.30 + step*i)
                c.drawString(fx, y_pos, f"{label} : {field_values[i]}")
                if label == "Age":
                    c.drawString(x0 + w * 0.25, y_pos, f"Gender : {gender_val}")

            ry = top_y(0.755)
            c.setLineWidth(0.8)
            c.line(x0+w*0.045, ry, x0+w*0.955, ry)
            c.setFont("Times-Roman", h*0.052)
            c.drawCentredString(x0+w/2, top_y(0.815), CLINIC_LINE)
            ft = top_y(0.865); fb = top_y(0.955)
            c.setLineWidth(0.9)
            c.rect(x0+bm, fb, w-2*bm, ft-fb, stroke=1, fill=0)
            c.setFont("Times-Roman", h*0.052)
            c.drawCentredString(x0+w/2, (ft+fb)/2 - h*0.017, CLINIC_HOURS)

        def _pdf_draw_eight_up(c):
            for r in range(ROWS):
                for col in range(COLS):
                    x0    = MARGIN + col * (CARD_W + COL_GAP)
                    y_top = PAGE_H - TOP_MARGIN - r * (CARD_H + ROW_GAP)
                    y0    = y_top - CARD_H
                    _pdf_draw_one_card(c, x0, y0, CARD_W, CARD_H)

        def generate_pdf(filepath):
            c = rl_canvas.Canvas(filepath, pagesize=A4)
            _pdf_draw_eight_up(c)
            c.showPage()
            c.save()

        # ── build workspace ───────────────────────────────────────────────────
        self.app.clear_workspace()
        self.app.workspace = tk.Frame(self.app.root, bd=3, relief="solid")
        self.app.workspace.pack(fill="both", expand=True, padx=10, pady=10)
        ws = self.app.workspace

        base_scale = min(500 / PAGE_H, 500 / PAGE_W)
        self.preview_scale = base_scale

        outer = tk.Frame(ws, bg="#c0c0c0")
        outer.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        vsb = tk.Scrollbar(outer, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(outer, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        init_cw = int(PAGE_W * base_scale)
        init_ch = int(PAGE_H * base_scale)
        cv = tk.Canvas(outer, bg="#c0c0c0",
                       width=init_cw + 10, height=init_ch + 10,
                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        cv.pack(fill="both", expand=True)
        vsb.config(command=cv.yview)
        hsb.config(command=cv.xview)

        # ── preview ───────────────────────────────────────────────────────────
        def draw_page_preview():
            cv.delete("all")
            scale    = self.preview_scale
            w_scaled = int(PAGE_W * scale)
            h_scaled = int(PAGE_H * scale)
            canvas_vw = w_scaled + 60
            OX = (canvas_vw - w_scaled) // 2
            OY = 10
            cv.config(scrollregion=(0, 0, canvas_vw, h_scaled + 30))

            # paper shadow + white sheet
            cv.create_rectangle(OX+4, OY+4, OX+w_scaled+4, OY+h_scaled+4,
                                 fill="#888888", outline="")
            cv.create_rectangle(OX, OY, OX+w_scaled, OY+h_scaled,
                                 fill="white", outline="#aaaaaa", width=1)

            def ppx(pt): return OX + int(pt * scale)
            def ppy(pt): return OY + int((PAGE_H - pt) * scale)

            for r in range(ROWS):
                for col in range(COLS):
                    x0_pt    = MARGIN + col * (CARD_W + COL_GAP)
                    y_top_pt = PAGE_H - TOP_MARGIN - r * (CARD_H + ROW_GAP)
                    tkx = ppx(x0_pt)
                    tky = ppy(y_top_pt)
                    tkw = int(CARD_W * scale)
                    tkh = int(CARD_H * scale)

                    def ttopy(frac, _tky=tky, _tkh=tkh):
                        return _tky + int(_tkh * frac)

                    # outer border
                    cv.create_rectangle(tkx, tky, tkx+tkw, tky+tkh,
                                        outline="#1a1a1a", width=1)

                    # title box
                    tt = ttopy(0.06); tb = ttopy(0.20)
                    bm = int(tkw * 0.035)
                    cv.create_rectangle(tkx+bm, tt, tkx+tkw-bm, tb,
                                        outline="#1a1a1a", width=1)
                    cv.create_text(tkx+tkw//2, (tt+tb)//2,
                                   text=CLINIC_NAME,
                                   font=("Times New Roman",
                                         max(6, int(tkh*0.08)), "bold"),
                                   fill="#1a1a1a")

                    # logo
                    logo_cx = tkx + int(tkw * 0.820)
                    logo_cy = ttopy(0.40)
                    lbox_w  = int(tkw * 0.50)
                    lbox_h  = int(tkh * 0.42)
                    logo_r  = min(lbox_w, lbox_h) // 2
                    if os.path.isfile(LOGO_PATH):
                        try:
                            from PIL import Image as _PI, ImageTk as _ITk
                            _img = _PI.open(LOGO_PATH)
                            _img.thumbnail((lbox_w, lbox_h))
                            if not hasattr(self, "_sc_logo"):
                                self._sc_logo = _ITk.PhotoImage(_img)
                            cv.create_image(logo_cx, logo_cy,
                                            image=self._sc_logo)
                        except Exception:
                            cv.create_oval(logo_cx-logo_r, logo_cy-logo_r,
                                           logo_cx+logo_r, logo_cy+logo_r,
                                           outline="#1a1a1a")
                    else:
                        cv.create_oval(logo_cx-logo_r, logo_cy-logo_r,
                                       logo_cx+logo_r, logo_cy+logo_r,
                                       outline="#1a1a1a")
                        cv.create_text(logo_cx, logo_cy, text="LOGO",
                                       font=("Helvetica",
                                             max(6, int(logo_r*0.4))),
                                       fill="#1a1a1a")

                    # field labels
                    fx   = tkx + int(tkw * 0.045)
                    n    = len(FIELD_LABELS)
                    step = (0.70 - 0.30) / (n - 1)
                    field_values = ["", "", "", "", "", ""]
                    gender_val = ""
                    if hasattr(self, "patient_data") and self.patient_data:
                        pd2 = self.patient_data
                        gender_val = str(pd2.get("gender", ""))
                        if not gender_val:
                            name_lower = str(pd2.get("patientname", "")).lower().strip()
                            if name_lower.startswith("mr.") or name_lower.startswith("mr ") or name_lower.startswith("master ") or name_lower.startswith("master."):
                                gender_val = "Male"
                            elif name_lower.startswith("mrs.") or name_lower.startswith("mrs ") or name_lower.startswith("ms.") or name_lower.startswith("ms ") or name_lower.startswith("miss ") or name_lower.startswith("miss."):
                                gender_val = "Female"
                        field_values = [
                            str(pd2.get("regno", "")),
                            str(pd2.get("patientid", "")),
                            datetime.now().strftime("%d-%m-%Y"),
                            str(pd2.get("age", "")),
                            str(pd2.get("patientname", "")),
                            (str(pd2.get("address1", "")) + " " +
                             str(pd2.get("address2", ""))).strip(),
                        ]
                    fnt_sz = max(6, int(tkh * 0.05))
                    for i, label in enumerate(FIELD_LABELS):
                        fy = ttopy(0.25 + step * i)
                        cv.create_text(fx, fy,
                                       text=f"{label} : {field_values[i]}",
                                       font=("Times New Roman", fnt_sz),
                                       anchor="nw", fill="#1a1a1a")
                        if label == "Age":
                            cv.create_text(tkx + int(tkw * 0.25), fy,
                                           text=f"Gender : {gender_val}",
                                           font=("Times New Roman", fnt_sz),
                                           anchor="nw", fill="#1a1a1a")

                    # horizontal rule
                    ry = ttopy(0.755)
                    cv.create_line(tkx+int(tkw*0.045), ry,
                                   tkx+int(tkw*0.955), ry,
                                   fill="#1a1a1a", width=1)

                    # clinic line
                    cv.create_text(tkx+tkw//2, ttopy(0.815),
                                   text=CLINIC_LINE,
                                   font=("Times New Roman",
                                         max(5, int(tkh*0.045))),
                                   fill="#1a1a1a")

                    # footer box
                    ft_ = ttopy(0.865); fb_ = ttopy(0.955)
                    cv.create_rectangle(tkx+bm, ft_, tkx+tkw-bm, fb_,
                                        outline="#1a1a1a", width=1)
                    cv.create_text(tkx+tkw//2, (ft_+fb_)//2,
                                   text=CLINIC_HOURS,
                                   font=("Times New Roman",
                                         max(5, int(tkh*0.045))),
                                   fill="#1a1a1a")

            zoom_lbl.config(
                text=f"{int(self.preview_scale / base_scale * 100)}%")

        # ── zoom ─────────────────────────────────────────────────────────────
        def zoom_in():
            if self.preview_scale < 3.0:
                self.preview_scale = round(min(3.0, self.preview_scale + 0.1), 2)
                draw_page_preview()

        def zoom_out():
            if self.preview_scale > 0.2:
                self.preview_scale = round(max(0.2, self.preview_scale - 0.1), 2)
                draw_page_preview()

        def on_mouse_wheel(event):
            if getattr(event, "delta", 0) > 0 or getattr(event, "num", 0) == 4:
                zoom_in()
            else:
                zoom_out()
            return "break"

        cv.bind("<MouseWheel>", on_mouse_wheel)
        cv.bind("<Button-4>",   on_mouse_wheel)
        cv.bind("<Button-5>",   on_mouse_wheel)

        # ── control bar ──────────────────────────────────────────────────────
        ctrl_frame = tk.Frame(ws)
        ctrl_frame.pack(fill="x", pady=4)

        tk.Button(ctrl_frame, text="-", font=("Arial", 11, "bold"),
                  width=3, command=zoom_out).pack(side="left", padx=4)
        zoom_lbl = tk.Label(ctrl_frame, text="100%",
                            font=("Arial", 10), width=6)
        zoom_lbl.pack(side="left", padx=2)
        tk.Button(ctrl_frame, text="+", font=("Arial", 11, "bold"),
                  width=3, command=zoom_in).pack(side="left", padx=4)

        # ── action buttons ────────────────────────────────────────────────────
        btn_bar = tk.Frame(ws)
        btn_bar.pack(pady=8)

        def _open_pdf(path):
            open_file(path)

        def _generate_pdf():
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile="Anupam_Dental_8up_Cards.pdf",
                initialdir=SCRIPT_DIR,
                filetypes=[("PDF files", "*.pdf")],
                title="Save 8-Up Card Sheet As")
            if not filepath:
                return
            try:
                generate_pdf(filepath)
                docx_path = convert_pdf_to_docx(filepath)
                messagebox.showinfo("Done", f"8-up card sheet saved successfully:\n📄 PDF: {filepath}\n📝 Word: {docx_path}")
                _open_pdf(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"PDF generation failed:\n{exc}")

        def _generate_word():
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".docx",
                initialfile="Anupam_Dental_8up_Cards.docx",
                initialdir=SCRIPT_DIR,
                filetypes=[("Word Document", "*.docx")],
                title="Save 8-Up Word Sheet As")
            if not filepath:
                return
            try:
                tmp_pdf = os.path.join(SCRIPT_DIR, "_8up_cards_temp.pdf")
                generate_pdf(tmp_pdf)
                convert_pdf_to_docx(tmp_pdf, filepath)
                messagebox.showinfo("Done", f"8-up Word sheet saved:\n{filepath}")
                open_file(filepath)
            except Exception as exc:
                messagebox.showerror("Error", f"Word sheet generation failed:\n{exc}")

        def _print_now():
            tmp = os.path.join(SCRIPT_DIR, "_8up_cards_temp.pdf")
            try:
                generate_pdf(tmp)
                convert_pdf_to_docx(tmp)
                _open_pdf(tmp)
            except Exception as exc:
                messagebox.showerror("Error", f"Could not open file:\n{exc}")

        def _close():
            self.app.personal()

        tk.Button(btn_bar, text="📄 Generate PDF", font=("Arial", 11),
                  width=14, bg="#1565C0", fg="white",
                  command=_generate_pdf).grid(row=0, column=0, padx=6)
        tk.Button(btn_bar, text="📝 Generate Word", font=("Arial", 11),
                  width=14, bg="#673AB7", fg="white",
                  command=_generate_word).grid(row=0, column=1, padx=6)
        tk.Button(btn_bar, text="🖨 Open / Print", font=("Arial", 11),
                  width=14, bg="#2E7D32", fg="white",
                  command=_print_now).grid(row=0, column=2, padx=6)
        tk.Button(btn_bar, text="Close", font=("Arial", 11),
                  width=10, bg="#ED350E", fg="white",
                  command=_close).grid(row=0, column=3, padx=6)

        draw_page_preview()
