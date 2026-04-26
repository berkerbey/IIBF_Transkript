import os
import sys
import threading
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from src.logger import logger
from src.transcriber import Transcriber
from src.exporters import export_txt, export_docx, export_srt
from src.model_download_dialog import ModelDownloadDialog
from src.welcome_dialog import WelcomeDialog


# ─── TOOLTIP HELPER ───────────────────────────────────────────────────────────
class _Tooltip:
    """
    Estetik hover+click tooltip.
    widget: tetikleyici widget
    text:   gösterilecek metin
    """
    def __init__(self, widget, text: str, delay=400):
        self._widget  = widget
        self._text    = text
        self._delay   = delay
        self._win     = None
        self._after   = None
        self._visible = False

        widget.bind("<Enter>",    self._schedule)
        widget.bind("<Leave>",    self._hide)
        widget.bind("<Button-1>", self._toggle)
        widget.bind("<Destroy>",  lambda _: self._hide())

    def _schedule(self, _=None):
        if not self._visible:
            self._cancel()
            self._after = self._widget.after(self._delay, self._show)

    def _cancel(self):
        if self._after:
            self._widget.after_cancel(self._after)
            self._after = None

    def _show(self, _=None):
        if self._win or not self._widget.winfo_exists():
            return
        self._visible = True
        x = self._widget.winfo_rootx() + self._widget.winfo_width() + 8
        y = self._widget.winfo_rooty()

        self._win = tk.Toplevel(self._widget)
        self._win.wm_overrideredirect(True)
        self._win.wm_geometry(f"+{x}+{y}")
        self._win.attributes("-topmost", True)

        frame = tk.Frame(self._win, bg="#1C2B3A",
                         highlightbackground="#3B5268", highlightthickness=1)
        frame.pack()

        # Title bar
        tk.Label(frame, text="◈  Teknik Özellikler",
                 bg="#243548", fg="#60A5FA",
                 font=("Consolas", 10, "bold"),
                 padx=12, pady=6, anchor="w").pack(fill="x")

        # Body
        tk.Label(frame, text=self._text,
                 bg="#1C2B3A", fg="#CBD5E1",
                 font=("Consolas", 10),
                 justify="left", padx=14, pady=10,
                 anchor="w").pack(fill="x")

    def _hide(self, _=None):
        self._cancel()
        self._visible = False
        if self._win:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None

    def _toggle(self, _=None):
        if self._visible:
            self._hide()
        else:
            self._cancel()
            self._show()


# ─── DESIGN TOKENS ────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Light")

# ── Surface / Background (Tailwind Slate, clean & modern) ─────────────────────
SURFACE_BG        = "#FAFAFA"  # App background (Pristine White/Light Gray)
SURFACE_CARD      = "#FFFFFF"  # Card / panel surface
SURFACE_RAISED    = "#F1F5F9"  # Slightly raised element
SURFACE_BORDER    = "#E2E8F0"  # Dividers / card borders
SURFACE_HOVER     = "#F8FAFC"  # Hover state
SURFACE_DEEP      = "#F8FAFC"  # DropZone interior

# ── Sidebar Tokens ────────────────────────────────────────────────────────────
SIDEBAR_BG        = "#0F172A"  # Very dark slate (Linear/Notion dark style)
SIDEBAR_BORDER    = "#1E293B"  # Dark divider
SIDEBAR_TEXT      = "#94A3B8"  # Slate 400
SIDEBAR_TEXT_ACT  = "#FFFFFF"  # White for active
SIDEBAR_ACTIVE    = "#1E293B"  # Slate 800 for active item
SIDEBAR_ACCENT    = "#3B82F6"  # Blue accent line

# ── Legacy aliases (keep old names pointing to new values so nothing breaks) ───
STEEL_BG          = SURFACE_BG
STEEL_BG_ALT      = SURFACE_RAISED
STEEL_FRAME       = SURFACE_CARD
STEEL_FRAME_MID   = SURFACE_RAISED
STEEL_FRAME_HOVER = SURFACE_HOVER
STEEL_ACCENT      = "#E2E8F0"
STEEL_SURFACE_H   = "#F1F5F9"
STEEL_DEEP        = SURFACE_DEEP
STEEL_HEADER      = "#0F172A"

# ── Primary & Accent ──────────────────────────────────────────────────────────
PRIMARY           = "#2563EB"  # Vivid blue (Tailwind blue-600)
PRIMARY_DARK      = "#1D4ED8"  # Hover / pressed
PRIMARY_LIGHT     = "#DBEAFE"  # Tinted surface (blue-100)
ACCENT_GOLD       = "#F59E0B"  # Warm amber accent

# ── Legacy aliases ─────────────────────────────────────────────────────────────
PAU_BLUE          = PRIMARY
PAU_BLUE_DARK     = PRIMARY_DARK
PAU_BLUE_LIGHT    = "#3B82F6"

# ── Text hierarchy ────────────────────────────────────────────────────────────
TEXT_BRIGHT       = "#FFFFFF"
TEXT_PRIMARY      = "#0F172A"  # slate-900
TEXT_SECONDARY    = "#475569"  # slate-600
TEXT_MUTED        = "#64748B"  # slate-500
TEXT_INVERSE      = "#FFFFFF"

# ── Semantic ──────────────────────────────────────────────────────────────────
COLOR_SUCCESS     = "#16A34A"  # green-600
COLOR_WARNING     = "#D97706"  # amber-600
COLOR_ERROR       = "#DC2626"  # red-600
COLOR_INFO        = PRIMARY

# ── Typography ────────────────────────────────────────────────────────────────
FONT_SANS = "Segoe UI Variable Display" if sys.platform == "win32" else "Inter"
FONT_MONO = "Consolas"


# Whisper model definitions
WHISPER_MODELS = [
    {"id": "faster-whisper-tiny",     "name": "Tiny",   "size": "75 MB",  "speed": 3, "acc": 2, "rec": False},
    {"id": "faster-whisper-base",     "name": "Base",   "size": "145 MB", "speed": 3, "acc": 3, "rec": False},
    {"id": "faster-whisper-small",    "name": "Small",  "size": "465 MB", "speed": 2, "acc": 3, "rec": False},
    {"id": "faster-whisper-medium",   "name": "Medium", "size": "1.4 GB", "speed": 2, "acc": 4, "rec": True},
    {"id": "faster-whisper-large-v2", "name": "Large",  "size": "3.1 GB", "speed": 1, "acc": 5, "rec": False},
]

GUIDE_STEPS = [
    ("Dosyayı Yükleyin",
     "Ana İşlem sekmesindeki alana ses veya video dosyanızı sürükleyin ya da\n"
     "tıklayarak seçin. Desteklenen formatlar: MP3, WAV, M4A, FLAC, MP4, MKV, MOV."),
    ("Ayarları Yapın",
     "Ayarlar sekmesinden Whisper modelini, hedef dili ve çıktı formatlarını seçin.\n"
     "Akademik araştırmalar için 'Medium' modeli önerilir."),
    ("Analizi Başlatın",
     "'ANALİZİ BAŞLAT' butonuna tıklayın. Tüm işlem cihazınızda gerçekleşir.\n"
     "İnternet gerekmez, hiçbir ses verisi dışarıya iletilmez."),
    ("İlerlemeyi İzleyin",
     "İlerleme çubuğu ve durum mesajı süreci gösterir.\n"
     "İşlem süresi ses uzunluğu ve donanımınıza göre değişir."),
    ("Çıktıları Alın",
     "'Klasörü Aç' ile outputs/ klasörünü açın.\n"
     "TXT/DOCX dosyaları MAXQDA ve ATLAS.ti ile doğrudan kullanılabilir."),
]

FAQS = [
    ("İnternet bağlantısı gerekiyor mu?",
     "Hayır. Model bir kez indirilir, tüm işlemler çevrimdışı gerçekleşir."),
    ("MAXQDA ile nasıl kullanırım?",
     "TXT çıktısı doğrudan MAXQDA'ya aktarılabilir. Zaman damgaları MAXQDA formatıyla uyumludur."),
    ("GPU olmadan çalışır mı?",
     "Evet. Uygulama CPU'da int8 optimizasyonuyla çalışır. GPU varsa otomatik kullanılır."),
    ("Desteklenen dosya formatları nelerdir?",
     "MP3, WAV, M4A, FLAC, OGG, MP4, MKV, MOV, WEBM formatları desteklenmektedir."),
]


# ─── LOG HANDLER ──────────────────────────────────────────────────────────────

class TextboxLogHandler(logging.Handler):
    """Streams log records into a CTkTextbox with per-level color tags."""

    LEVEL_LABELS = {
        "INFO":     "BİLGİ",
        "WARNING":  "UYARI",
        "ERROR":    "HATA",
        "CRITICAL": "KRİTİK",
        "DEBUG":    "HATA AYIKLA",
    }

    def __init__(self, textbox: ctk.CTkTextbox):
        super().__init__()
        self.textbox = textbox
        tb = textbox._textbox
        tb.tag_configure("ts",       foreground="#708090", font=(FONT_MONO, 11))
        tb.tag_configure("INFO",     foreground=COLOR_INFO,    font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("WARNING",  foreground=COLOR_WARNING, font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("ERROR",    foreground=COLOR_ERROR,   font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("CRITICAL", foreground=COLOR_ERROR,   font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("DEBUG",    foreground=TEXT_MUTED,    font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("msg",      foreground="#334455",     font=(FONT_MONO, 11))

    def emit(self, record):
        try:
            import time
            ts    = time.strftime("%H:%M:%S", time.localtime(record.created))
            level = record.levelname
            label = self.LEVEL_LABELS.get(level, level)
            msg   = record.getMessage()
            tb    = self.textbox._textbox

            def _insert():
                tb.configure(state="normal")
                tb.insert("end", f"{ts}  ", "ts")
                tb.insert("end", f"[{label}]  ", level)
                tb.insert("end", f"{msg}\n", "msg")
                tb.see("end")
                tb.configure(state="disabled")

            self.textbox.after(0, _insert)
        except Exception:
            pass


# ─── WAVEFORM CANVAS ──────────────────────────────────────────────────────────

class WaveformCanvas(tk.Canvas):
    """Decorative static waveform bar visualization."""

    BARS = [6, 10, 16, 22, 12, 26, 18, 12, 24, 16, 22, 8, 16, 20, 14, 28, 20, 10, 22, 16]

    def __init__(self, master, bg_color, **kwargs):
        super().__init__(master, height=28, bg=bg_color, highlightthickness=0, **kwargs)
        self.bind("<Configure>", self._draw)

    def _draw(self, _=None):
        self.delete("all")
        x = 0
        for h in self.BARS:
            y1 = (28 - h) // 2
            self.create_rectangle(x, y1, x + 2, y1 + h, fill=PAU_BLUE_LIGHT, outline="")
            x += 5


# ─── DROP ZONE (DASHED BORDER VIA CANVAS) ────────────────────────────────────

class DropZone(tk.Canvas):
    """Canvas-based drop zone that renders a proper dashed border."""

    def __init__(self, master, on_click, **kwargs):
        super().__init__(
            master,
            highlightthickness=0,
            bg=SURFACE_DEEP,
            **kwargs,
        )
        self._on_click = on_click
        self._hover    = False
        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>",  lambda _: on_click())
        self.bind("<Enter>",     lambda _: self._set_hover(True))
        self.bind("<Leave>",     lambda _: self._set_hover(False))

    def _set_hover(self, state):
        self._hover = state
        self._draw()

    def _draw(self, _=None):
        self.delete("all")
        w = self.winfo_width()  or 400
        h = self.winfo_height() or 150
        
        # Background fill - Light pristine theme
        self.configure(bg="#F1F5F9" if self._hover else "#FAFAF9") # slate-100 / warm pristine
        
        # Draw rounded rectangle (faked with arcs if needed, but standard rectangle is fine for dash)
        border_color = PRIMARY if self._hover else "#CBD5E1" # slate-300
        self.create_rectangle(
            4, 4, w - 4, h - 4,
            outline=border_color, dash=(6, 6), width=2,
        )
        # Upload icon circle
        cx, cy_icon = w // 2, h // 2 - 24
        r = 28
        icon_fill   = PRIMARY_LIGHT if self._hover else "#F8FAFC"
        self.create_oval(cx - r, cy_icon - r, cx + r, cy_icon + r,
                         fill=icon_fill, outline=border_color if not self._hover else "", width=1)
        self.create_text(cx, cy_icon, text="↑",
                         font=(FONT_SANS, 18, "bold"),
                         fill=PRIMARY if self._hover else TEXT_MUTED)
        # Main label
        label_color = PRIMARY if self._hover else TEXT_PRIMARY
        self.create_text(cx, h // 2 + 18,
                         text="Ses veya Video Dosyası Sürükleyin ya da Tıklayın",
                         font=(FONT_SANS, 14, "bold"), fill=label_color)
        # Format hint
        self.create_text(cx, h // 2 + 40,
                         text="MP3  ·  WAV  ·  M4A  ·  FLAC  ·  MP4  ·  MKV  ·  MOV",
                         font=(FONT_SANS, 11), fill=TEXT_MUTED)


# ─── MAIN APPLICATION ─────────────────────────────────────────────────────────

class App(ctk.CTk):

    def __init__(self, config=None):
        super().__init__()
        self.config_data = config or {}

        self.title("PAÜ İİBF — Akademik Transkripsiyon Asistanı")
        self.geometry("960x620")
        self.minsize(860, 600)
        self.configure(fg_color=SURFACE_BG)

        # Runtime state
        self.audio_paths   = []
        self.active_idx    = -1
        self.transcribing  = False
        self.success_banner = None
        
        import threading
        self.cancel_event = threading.Event()

        # Settings variables
        self.var_model = tk.StringVar(value=self.config_data.get("model_name", "faster-whisper-medium"))
        self.var_lang  = tk.StringVar(value="tr")
        self.var_hw    = tk.StringVar(value="cpu")
        self.var_txt   = tk.BooleanVar(value=True)
        self.var_docx  = tk.BooleanVar(value=True)
        self.var_srt   = tk.BooleanVar(value=True)
        self.var_vtt   = tk.BooleanVar(value=False)
        self.var_normalize = tk.BooleanVar(value=True)
        self.var_prompt    = tk.StringVar(value="")

        self._model_card_refs = {}  # id → (frame, name_lbl, stars_lbl)

        self._load_assets()
        self._load_icons()
        self._build_ui()
        self._attach_log_handler()

        logger.info("Uygulama başlatıldı.")
        logger.info(f"ffmpeg kontrolü: {self._ffmpeg_status()}")

        # Başlat nabız animasyonu
        self.after(800, self._pulse_btn_start)
        
        # İlk çalışma kontrolü
        self.after(500, self._check_first_run)

    def _check_first_run(self):
        if not self.config_data.get("welcome_shown", False):
            # Show aesthetic welcome popup
            config_path = "config.json"
            if getattr(sys, 'frozen', False):
                config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
            WelcomeDialog(self, config_path)

    def _pulse_btn_start(self):
        try:
            if hasattr(self, "btn_start") and self.btn_start.winfo_exists():
                if self.audio_paths and not self.transcribing:
                    self._pulse_state = not getattr(self, "_pulse_state", False)
                    self.btn_start.configure(fg_color="#1D4ED8" if self._pulse_state else PRIMARY)
                elif not self.transcribing:
                    self.btn_start.configure(fg_color=PRIMARY)
        except Exception:
            pass
        finally:
            self.after(800, self._pulse_btn_start)

    def _load_icons(self):
        from src.icons import create_icon
        self.icn_play   = ctk.CTkImage(light_image=create_icon("play",   color=TEXT_SECONDARY), size=(14, 14))
        self.icn_stop   = ctk.CTkImage(light_image=create_icon("stop",   color="#FFFFFF"),       size=(14, 14))
        self.icn_close  = ctk.CTkImage(light_image=create_icon("close",  color=COLOR_ERROR),     size=(12, 12))
        self.icn_folder = ctk.CTkImage(light_image=create_icon("folder", color=TEXT_SECONDARY),  size=(16, 16))
        logger.info(f"Yapılandırma yüklendi (model: {self.var_model.get()}, dil: {self.var_lang.get()}).")

    # ── ASSETS ────────────────────────────────────────────────────────────────

    def _load_assets(self):
        self.pau_logo_img  = None
        self.iibf_logo_img = None
        self.bg_texture_img = None
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

        for attr, fname, size in [
            ("pau_logo_img",  "pau_logo.png",  (72, 72)),
            ("iibf_logo_img", "iibf_logo.png", (54, 72)),
        ]:
            path = os.path.join(assets_dir, fname)
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    setattr(self, attr, ctk.CTkImage(light_image=img, dark_image=img, size=size))
                except Exception as e:
                    logger.error(f"Logo yüklenemedi ({fname}): {e}")

        bg_path = os.path.join(assets_dir, "bg.png")
        if os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                self.bg_texture_img = ctk.CTkImage(light_image=bg_img, dark_image=bg_img, size=(1920, 100))
            except Exception as e:
                logger.error(f"Arkaplan yüklenemedi: {e}")

        # Set window icon
        icon_path = os.path.join(assets_dir, "icon.ico")
        if not os.path.exists(icon_path):
            # Fallback for different working directories
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "assets", "icon.ico")
        
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                logger.warning(f"Icon could not be loaded: {e}")

    def _ffmpeg_status(self):
        import shutil
        return "bulundu" if shutil.which("ffmpeg") else "bulunamadı (PATH kontrolü yapın)"

    # ── UI CONSTRUCTION ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.geometry("1120x700")
        self.minsize(980, 640)
        self._active_nav = "main"
        self._build_sidebar()
        self._build_content_area()

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, width=200, corner_radius=0)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        tk.Frame(sb, bg=SIDEBAR_BORDER, width=1).pack(side="right", fill="y")

        inner = ctk.CTkFrame(sb, fg_color="transparent")
        inner.pack(fill="both", expand=True, side="left")

        # Logo row: PAÜ logo + İİBF logo side by side (no text)
        logo_row = ctk.CTkFrame(inner, fg_color="transparent")
        logo_row.pack(fill="x", padx=16, pady=(20, 4))
        if self.pau_logo_img:
            ctk.CTkLabel(logo_row, image=self.pau_logo_img, text="").pack(side="left", padx=(0, 6))
        if self.iibf_logo_img:
            ctk.CTkLabel(logo_row, image=self.iibf_logo_img, text="").pack(side="left", padx=(0, 10))

        ctk.CTkFrame(inner, height=1, fg_color=SIDEBAR_BORDER).pack(fill="x", padx=12, pady=12)


        # Nav items
        self._nav_container = ctk.CTkFrame(inner, fg_color="transparent")
        self._nav_container.pack(fill="x", padx=8)
        self._nav_items = [
            ("main",      "\u2302", "Ana İşlem"),
            ("settings",  "\u2699", "Ayarlar"),
            ("console",   "\u25a4", "Bilgi Konsolu"),
            ("guide",     "\u25a3", "Kullanım Kılavuzu"),
            ("technical", "\u25c8", "Teknik Bilgiler"),
            ("about",     "\u25cb", "Hakkında"),
        ]
        for key, icon, label in self._nav_items:
            self._make_nav_btn(self._nav_container, key, icon, label)

        ctk.CTkFrame(inner, fg_color="transparent").pack(fill="both", expand=True)

        # Status badge
        ctk.CTkFrame(inner, height=1, fg_color=SIDEBAR_BORDER).pack(fill="x", padx=12, pady=(0, 10))
        sb_badge = ctk.CTkFrame(inner, fg_color="#1A3A28", corner_radius=8)
        sb_badge.pack(fill="x", padx=12, pady=(0, 8))
        sb_inner = ctk.CTkFrame(sb_badge, fg_color="transparent")
        sb_inner.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(sb_inner, text="\u2713",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#4ADE80").pack(side="left", padx=(0, 8))
        sc = ctk.CTkFrame(sb_inner, fg_color="transparent")
        sc.pack(side="left")
        ctk.CTkLabel(sc, text="Sistem Haz\u0131r",
                     font=ctk.CTkFont(family=FONT_SANS, size=11, weight="bold"),
                     text_color="#4ADE80").pack(anchor="w")
        ctk.CTkLabel(sc, text="T\u00fcm sistemler \u00e7al\u0131\u015f\u0131yor",
                     font=ctk.CTkFont(family=FONT_SANS, size=9),
                     text_color=SIDEBAR_TEXT).pack(anchor="w")
        vr = ctk.CTkFrame(inner, fg_color="transparent")
        vr.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkLabel(vr, text="v1.0.0",
                     font=ctk.CTkFont(family=FONT_MONO, size=10),
                     text_color=SIDEBAR_TEXT).pack(side="left")

    def _make_nav_btn(self, parent, key, icon, label):
        active = (key == self._active_nav)
        f = ctk.CTkFrame(parent,
                         fg_color=SIDEBAR_ACTIVE if active else "transparent",
                         corner_radius=8)
        f.pack(fill="x", pady=1)
        if active:
            tk.Frame(f, bg=SIDEBAR_ACCENT, width=3).pack(side="left", fill="y")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", padx=(6 if active else 10), pady=8)
        ctk.CTkLabel(row, text=icon,
                     font=ctk.CTkFont(size=13),
                     text_color=SIDEBAR_ACCENT if active else SIDEBAR_TEXT).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(row, text=label,
                     font=ctk.CTkFont(family=FONT_SANS, size=12,
                                      weight="bold" if active else "normal"),
                     text_color=SIDEBAR_TEXT_ACT if active else SIDEBAR_TEXT).pack(side="left")
        def _switch(e=None, k=key):
            self._active_nav = k
            for w in self._nav_container.winfo_children(): w.destroy()
            for ki, ic, lb in self._nav_items: self._make_nav_btn(self._nav_container, ki, ic, lb)
            for t in self._all_tabs: t.pack_forget()
            self._tab_map[k].pack(fill="both", expand=True)
        for w in [f, row] + list(row.winfo_children()):
            w.bind("<Button-1>", _switch)
            w.configure(cursor="hand2")



    def _build_content_area(self):
        content = ctk.CTkFrame(self, fg_color=SURFACE_BG, corner_radius=0)
        content.pack(side="left", fill="both", expand=True)

        # Top bar
        topbar = ctk.CTkFrame(content, fg_color=SURFACE_BG, height=72, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkFrame(content, fg_color=SURFACE_BORDER, height=1, corner_radius=0).pack(fill="x")
        
        # Topbar: centered title block
        tb_inner = ctk.CTkFrame(topbar, fg_color="transparent")
        tb_inner.pack(fill="both", expand=True, padx=32)

        # Center column: title + badge
        center = ctk.CTkFrame(tb_inner, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(center, text="Akademik Transkripsiyon Aracı",
                     font=ctk.CTkFont(family=FONT_SANS, size=18, weight="bold", letterSpacing=1) if sys.platform != "win32" else ctk.CTkFont(family=FONT_SANS, size=18, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="center")
        sub = ctk.CTkFrame(center, fg_color="transparent")
        sub.pack(anchor="center", pady=(4, 0))
        badge = ctk.CTkFrame(sub, fg_color=PRIMARY_LIGHT, corner_radius=6)
        badge.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(badge, text=" OpenAI Whisper ",
                     font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold"),
                     text_color=PRIMARY).pack(padx=6, pady=2)
        ctk.CTkLabel(sub, text="Lokal çözümleme · Yüksek doğruluk",
                     font=ctk.CTkFont(family=FONT_SANS, size=11),
                     text_color=TEXT_MUTED).pack(side="left")

        # Page container
        pages = ctk.CTkFrame(content, fg_color=SURFACE_BG, corner_radius=0)
        pages.pack(fill="both", expand=True)

        # Create tab frames
        self.tab_main      = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)
        self.tab_settings  = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)
        self.tab_console   = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)
        self.tab_guide     = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)
        self.tab_technical = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)
        self.tab_about     = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)

        self._all_tabs = [self.tab_main, self.tab_settings, self.tab_console,
                          self.tab_guide, self.tab_technical, self.tab_about]
        self._tab_map = {
            "main": self.tab_main, "settings": self.tab_settings,
            "console": self.tab_console, "guide": self.tab_guide,
            "technical": self.tab_technical, "about": self.tab_about,
        }

        self._build_main_tab()
        self._build_settings_tab()
        self._build_console_tab()
        self._build_guide_tab()
        self._build_technical_tab()
        self._build_about_tab()

        # Show main tab
        self.tab_main.pack(fill="both", expand=True)

        # Footer
        ctk.CTkFrame(content, fg_color=SURFACE_BORDER, height=1, corner_radius=0).pack(fill="x", side="bottom")
        footer = ctk.CTkFrame(content, fg_color=SURFACE_BG, height=36, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkLabel(footer,
                     text="© 2026 PAÜ İİBF  ·  Yapay Zeka ve Dijital Uygulamalar Koordinatörlüğü.",
                     font=ctk.CTkFont(family=FONT_SANS, size=10),
                     text_color=TEXT_MUTED).place(relx=0.5, rely=0.5, anchor="center")



    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1 — ANA İŞLEM
    # ═══════════════════════════════════════════════════════════════════════════


    def _build_main_tab(self):
        p = self.tab_main

        # Drop zone / file card container
        self.file_zone = ctk.CTkFrame(p, fg_color="transparent")
        self.file_zone.pack(fill="x", padx=32, pady=(24, 16))
        self._show_drop_zone()

        # Status row
        status_row = ctk.CTkFrame(p, fg_color="transparent")
        status_row.pack(fill="x", padx=32)

        self.status_dot = tk.Canvas(
            status_row, width=8, height=8,
            bg=SURFACE_BG, highlightthickness=0,
        )
        self.status_dot.pack(side="left", padx=(0, 8))
        self.status_dot.create_oval(1, 1, 7, 7, fill=COLOR_SUCCESS, outline="")

        self.lbl_status = ctk.CTkLabel(
            status_row,
            text="Sistem hazır. Ses veya video dosyası bekleniyor.",
            font=ctk.CTkFont(family=FONT_SANS, size=12),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.lbl_status.pack(side="left", fill="x", expand=True)

        # Progress bar — slim, primary blue
        self.progress_bar = ctk.CTkProgressBar(
            p,
            height=4,
            progress_color=PRIMARY,
            fg_color=SURFACE_BORDER,
            corner_radius=2,
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=32, pady=(8, 0))

        # Action buttons
        btn_row = ctk.CTkFrame(p, fg_color="transparent")
        btn_row.pack(fill="x", padx=32, pady=(16, 16))

        self.btn_start = ctk.CTkButton(
            btn_row,
            text="  ANALİZİ BAŞLAT",
            font=ctk.CTkFont(family=FONT_SANS, size=15, weight="bold"),
            height=52,
            state="disabled",
            command=self.start_transcription,
            fg_color=PRIMARY,
            hover_color=PRIMARY_DARK,
            text_color="#FFFFFF",
            corner_radius=10,
        )
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.btn_open_folder = ctk.CTkButton(
            btn_row,
            text=" Klasörü Aç",
            image=self.icn_folder,
            font=ctk.CTkFont(family=FONT_SANS, size=13),
            height=52,
            width=140,
            command=self.open_output_folder,
            fg_color=SURFACE_CARD,
            hover_color=SURFACE_HOVER,
            text_color=TEXT_SECONDARY,
            corner_radius=10,
            border_width=1,
            border_color=SURFACE_BORDER,
        )
        self.btn_open_folder.pack(side="right")

    def _show_drop_zone(self):
        for w in self.file_zone.winfo_children():
            w.destroy()
        self._drop_canvas = DropZone(self.file_zone, on_click=self.select_file, height=160)
        self._drop_canvas.pack(fill="x")

        # Try to register as a drag-and-drop target (requires tkinterdnd2)
        try:
            self._drop_canvas.drop_target_register("DND_Files")
            self._drop_canvas.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

        # Browse button below drop zone
        self.btn_browse = ctk.CTkButton(
            self.file_zone,
            text="Dosya Seç",
            font=ctk.CTkFont(family=FONT_SANS, size=12),
            height=34,
            width=120,
            command=self.select_file,
            fg_color="#FFFFFF",
            hover_color="#EBE9E4",
            text_color=TEXT_SECONDARY,
            corner_radius=8,
            border_width=1,
            border_color="#D6D3CA",
        )
        self.btn_browse.pack(pady=(10, 0))

    def _render_queue(self):
        for w in self.file_zone.winfo_children():
            w.destroy()

        if not self.audio_paths:
            self._show_drop_zone()
            return

        scroll = ctk.CTkScrollableFrame(
            self.file_zone, fg_color="transparent",
            scrollbar_button_color=STEEL_ACCENT,
            height=200
        )
        scroll.pack(fill="x", expand=True)

        for i, filepath in enumerate(self.audio_paths):
            self._build_queue_card(scroll, filepath, i)

        # Append files button
        ctk.CTkButton(
            self.file_zone,
            text="+ Yeni Dosya Ekle",
            font=ctk.CTkFont(family=FONT_SANS, size=11),
            height=30,
            command=self.select_file,
            fg_color="transparent",
            hover_color=SURFACE_HOVER,
            text_color=PRIMARY,
            border_width=1,
            border_color=PRIMARY_LIGHT,
            corner_radius=6,
        ).pack(pady=(8, 0))

    def _build_queue_card(self, parent, filepath, idx):
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].upper().lstrip(".") or "—"
        try:
            size_str = f"{os.path.getsize(filepath) / (1024 * 1024):.1f} MB"
        except Exception:
            size_str = "—"

        is_active = (idx == self.active_idx)

        # ── CARD ─────────────────────────────────────────────────────────────
        # Active  → white background, blue border
        # Inactive → muted steel-gray background, thin border
        card_bg      = SURFACE_HOVER if is_active else SURFACE_CARD
        card_border  = PRIMARY       if is_active else SURFACE_BORDER
        card_bw      = 2             if is_active else 1

        card = ctk.CTkFrame(
            parent,
            fg_color=card_bg,
            border_color=card_border,
            border_width=card_bw,
            corner_radius=12,
        )
        card.pack(fill="x", pady=(0, 6))

        # Blue accent left strip on active
        if is_active:
            accent_strip = tk.Frame(card, bg=PRIMARY, width=4)
            accent_strip.pack(side="left", fill="y")

        # ── INNER CONTENT ROW ────────────────────────────────────────────────
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True,
                     padx=(10, 8), pady=10)

        # File name
        ctk.CTkLabel(
            content,
            text=filename,
            font=ctk.CTkFont(family=FONT_SANS, size=12,
                             weight="bold" if is_active else "normal"),
            text_color=TEXT_PRIMARY if is_active else TEXT_SECONDARY,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            content,
            text=f"{size_str}  ·  {ext}",
            font=ctk.CTkFont(family=FONT_SANS, size=10),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # ── ACTION BUTTONS (active only) ─────────────────────────────────────
        if is_active:
            btn_col = ctk.CTkFrame(card, fg_color="transparent")
            btn_col.pack(side="right", anchor="center", padx=(0, 12))

            self.btn_preview = ctk.CTkButton(
                btn_col, text=" Önizle",
                image=self.icn_play,
                font=ctk.CTkFont(family=FONT_SANS, size=10),
                height=28, width=80,
                fg_color="#E8E6E0", hover_color="#D4EDDA",
                text_color=TEXT_SECONDARY, corner_radius=6,
                command=lambda p=filepath: self._toggle_preview(p),
            )
            self.btn_preview.pack(pady=(0, 4))

            ctk.CTkButton(
                btn_col, text=" Kaldır",
                image=self.icn_close,
                font=ctk.CTkFont(family=FONT_SANS, size=10),
                height=28, width=80,
                fg_color="#E8E6E0", hover_color="#FDDEDE",
                text_color=COLOR_ERROR, corner_radius=6,
                command=lambda i=idx: self._remove_file(i),
            ).pack()

        # ── CLICK TO SELECT ──────────────────────────────────────────────────
        def _select(_=None):
            if not self.transcribing:
                if getattr(self, "is_previewing", False):
                    self._stop_preview()
                self.active_idx = idx
                self._render_queue()

        card.bind("<Button-1>", _select)
        card.configure(cursor="hand2")
        for child in card.winfo_children():
            try:
                child.bind("<Button-1>", _select)
                child.configure(cursor="hand2")
            except Exception:
                pass

    def _show_success_banner(self):
        if self.success_banner and self.success_banner.winfo_exists():
            self.success_banner.destroy()

        banner = ctk.CTkFrame(
            self.tab_main,
            fg_color="#D4EDDA",
            corner_radius=12,
        )
        banner.pack(fill="x", padx=32, pady=(0, 8), before=self.progress_bar)

        inner = ctk.CTkFrame(banner, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(inner, text="✓",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=COLOR_SUCCESS).pack(side="left", padx=(0, 16))

        txt = ctk.CTkFrame(inner, fg_color="transparent")
        txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(txt, text="Transkripsiyon Tamamlandı",
                     font=ctk.CTkFont(family=FONT_SANS, size=14, weight="bold"),
                     text_color="#065F46", anchor="w").pack(anchor="w")
        ctk.CTkLabel(txt, text="Tüm çıktı dosyaları outputs/ klasörüne kaydedildi.",
                     font=ctk.CTkFont(family=FONT_SANS, size=11),
                     text_color="#6EE7B7", anchor="w").pack(anchor="w")


        self.success_banner = banner



    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2 — AYARLAR
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_settings_tab(self):
        scroll = ctk.CTkScrollableFrame(
            self.tab_settings, fg_color="transparent",
            scrollbar_button_color=STEEL_ACCENT,
        )
        scroll.pack(fill="both", expand=True, padx=36, pady=24)

        # Section label
        ctk.CTkLabel(
            scroll, text="W H I S P E R   M O D E L   S E Ç İ M İ",
            font=ctk.CTkFont(family=FONT_SANS, size=10, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 10))

        # Model cards grid
        model_row = ctk.CTkFrame(scroll, fg_color="transparent")
        model_row.pack(fill="x", pady=(0, 18))
        for _i in range(len(WHISPER_MODELS)):
            model_row.columnconfigure(_i, weight=1)

        for i, m in enumerate(WHISPER_MODELS):
            self._build_model_card(model_row, m, i)

        ctk.CTkFrame(scroll, height=1, fg_color=STEEL_ACCENT).pack(fill="x", pady=(0, 14))

        # Settings rows
        self._settings_row(scroll, "Hedef Dil",        self._build_lang_row)
        self._settings_row(scroll, "Çıktı Formatları", self._build_formats_row)
        self._settings_row(scroll, "Donanım",          self._build_hardware_row)
        self._settings_row(scroll, "Çıktı Klasörü",    self._build_output_dir_row)
        self._settings_row(scroll, "Ses İyileştirme",  self._build_normalize_row)
        self._settings_row(scroll, "Özel Dağarcık",    self._build_prompt_row)

    def _build_normalize_row(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="right")
        ctk.CTkCheckBox(
            f, text="Otomatik Gürültü ve Ses Seviyesi İyileştirme (Önerilir)", variable=self.var_normalize,
            fg_color=PAU_BLUE, hover_color=PAU_BLUE_LIGHT, text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family=FONT_SANS, size=12)
        ).pack(side="right")

    def _build_prompt_row(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="right", fill="x", expand=True, padx=(15, 0))
        ctk.CTkEntry(
            f, textvariable=self.var_prompt,
            placeholder_text="Örn: Pamukkale Üniversitesi, Rektörlük, Makroekonomi...",
            font=ctk.CTkFont(family=FONT_SANS, size=12),
            fg_color=STEEL_DEEP, text_color=TEXT_PRIMARY,
            border_color="#A0AAB5", border_width=1, corner_radius=6,
        ).pack(fill="x", expand=True)

    def _build_model_card(self, parent, m, col):
        sel = m["id"] == self.var_model.get()
        frame = ctk.CTkFrame(
            parent,
            fg_color=PAU_BLUE_DARK if sel else STEEL_FRAME_MID,
            border_color=PAU_BLUE_LIGHT if sel else SURFACE_BORDER,
            border_width=2 if sel else 1,
            corner_radius=11,
        )
        frame.grid(row=0, column=col, sticky="nsew",
                   padx=(0, 8) if col < len(WHISPER_MODELS) - 1 else 0)

        # Recommended badge
        if m["rec"]:
            ctk.CTkLabel(
                frame, text="Önerilir",
                font=ctk.CTkFont(family=FONT_SANS, size=9, weight="bold"),
                fg_color=PAU_BLUE_LIGHT, text_color="white",
                corner_radius=8, padx=8, pady=2,
            ).pack(anchor="e", padx=8, pady=(8, 0))
        else:
            ctk.CTkLabel(frame, text="", height=14).pack()

        # Name
        name_lbl = ctk.CTkLabel(
            frame,
            text=m["name"].upper(),
            font=ctk.CTkFont(family=FONT_SANS, size=15, weight="bold"),
            text_color=TEXT_BRIGHT if sel else TEXT_SECONDARY,
        )
        name_lbl.pack()

        # Size
        ctk.CTkLabel(
            frame, text=m["size"],
            font=ctk.CTkFont(family=FONT_SANS, size=10),
            text_color=TEXT_MUTED,
        ).pack(pady=(2, 0))

        # Speed bars
        bars_f = ctk.CTkFrame(frame, fg_color="transparent")
        bars_f.pack(pady=(8, 2))
        ctk.CTkLabel(bars_f, text="Hız",
                     font=ctk.CTkFont(size=9), text_color=TEXT_MUTED).pack(side="left", padx=(0, 4))
        for j in range(3):
            active = j < m["speed"]
            color = (PAU_BLUE_LIGHT if sel else STEEL_ACCENT) if active else STEEL_FRAME_MID
            ctk.CTkFrame(bars_f, width=8, height=10 + j * 4,
                         fg_color=color, corner_radius=2).pack(side="left", padx=1)

        # Accuracy stars
        stars_lbl = ctk.CTkLabel(
            frame,
            text="★" * m["acc"] + "☆" * (5 - m["acc"]),
            font=ctk.CTkFont(size=13),
            text_color="#f0c040" if sel else TEXT_MUTED,
        )
        stars_lbl.pack(pady=(2, 12))

        # Click binding — rebind all children
        def make_handler(model_id):
            def handler(_=None):
                self.var_model.set(model_id)
                self._refresh_model_cards()
            return handler

        cb = make_handler(m["id"])
        for widget in [frame, name_lbl, stars_lbl]:
            widget.bind("<Button-1>", cb)
            widget.configure(cursor="hand2")

        self._model_card_refs[m["id"]] = (frame, name_lbl, stars_lbl)

    def _refresh_model_cards(self):
        sel = self.var_model.get()
        for mid, (frame, name_lbl, stars_lbl) in self._model_card_refs.items():
            is_sel = mid == sel
            frame.configure(
                fg_color=PAU_BLUE_DARK if is_sel else STEEL_FRAME_MID,
                border_color=PAU_BLUE_LIGHT if is_sel else SURFACE_BORDER,
                border_width=2 if is_sel else 1,
            )
            name_lbl.configure(text_color=TEXT_BRIGHT if is_sel else TEXT_SECONDARY)
            stars_lbl.configure(text_color="#f0c040" if is_sel else TEXT_MUTED)

    def _settings_row(self, parent, label, builder_fn):
        row = ctk.CTkFrame(
            parent,
            fg_color=STEEL_FRAME_MID,
            border_color=SURFACE_BORDER,
            border_width=1,
            corner_radius=10,
        )
        row.pack(fill="x", pady=(0, 10))

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=14)

        ctk.CTkLabel(
            inner, text=label,
            font=ctk.CTkFont(family=FONT_SANS, size=13, weight="bold"),
            text_color=TEXT_PRIMARY, anchor="w",
        ).pack(side="left")

        builder_fn(inner)

    def _build_lang_row(self, parent):
        lang_map = {"tr": "Türkçe", "auto": "Otomatik Algıla", "en": "İngilizce", "de": "Almanca"}

        def _on_change(display_val):
            reverse = {v: k for k, v in lang_map.items()}
            self.var_lang.set(reverse.get(display_val, "tr"))

        ctk.CTkOptionMenu(
            parent,
            values=list(lang_map.values()),
            command=_on_change,
            fg_color=STEEL_ACCENT,
            button_color=STEEL_FRAME_HOVER,
            button_hover_color=STEEL_SURFACE_H,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=STEEL_FRAME_MID,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color=STEEL_FRAME_HOVER,
            dynamic_resizing=False,
            width=170,
        ).pack(side="right")

    def _build_formats_row(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="right")
        for var, text in [
            (self.var_txt,  "TXT"),
            (self.var_docx, "DOCX"),
            (self.var_srt,  "SRT"),
            (self.var_vtt,  "VTT"),
        ]:
            ctk.CTkCheckBox(
                f, text=text, variable=var,
                fg_color=PAU_BLUE, hover_color=PAU_BLUE_LIGHT,
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(family=FONT_SANS, size=12),
            ).pack(side="left", padx=8)

    def _build_hardware_row(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="right")
        for val, lbl in [("auto", "Otomatik"), ("cuda", "GPU (CUDA)"), ("cpu", "Yalnızca CPU")]:
            ctk.CTkRadioButton(
                f, text=lbl, variable=self.var_hw, value=val,
                fg_color=PAU_BLUE, hover_color=PAU_BLUE_LIGHT,
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(family=FONT_SANS, size=12),
            ).pack(side="left", padx=10)

    def _build_output_dir_row(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="right")
        output_dir = os.path.join(os.getcwd(), "outputs")
        display    = ("..." + output_dir[-44:]) if len(output_dir) > 48 else output_dir

        ctk.CTkLabel(
            f, text=display,
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            fg_color="#E2E8F0",
            text_color=TEXT_MUTED,
            corner_radius=6,
            padx=10, pady=5,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            f, text="Aç",
            font=ctk.CTkFont(family=FONT_SANS, size=12, weight="bold"),
            height=34, width=56,
            fg_color=STEEL_ACCENT, hover_color=STEEL_FRAME_HOVER,
            text_color=TEXT_PRIMARY, corner_radius=7,
            command=self.open_output_folder,
        ).pack(side="left")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3 — BİLGİ KONSOLU
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_console_tab(self):
        p = self.tab_console

        # Toolbar
        toolbar = ctk.CTkFrame(p, fg_color="#D0D8E0", corner_radius=0, height=38)
        toolbar.pack(fill="x", padx=28, pady=(20, 0))
        toolbar.pack_propagate(False)

        tinner = ctk.CTkFrame(toolbar, fg_color="transparent")
        tinner.pack(fill="both", expand=True, padx=10, pady=6)

        for lbl, cmd in [
            ("Kopyala", self._console_copy),
            ("Kaydet",  self._console_save),
            ("Temizle", self._console_clear),
        ]:
            ctk.CTkButton(
                tinner, text=lbl,
                font=ctk.CTkFont(family=FONT_SANS, size=11),
                height=26, width=72,
                fg_color=STEEL_FRAME_MID,
                hover_color=STEEL_ACCENT,
                text_color=TEXT_SECONDARY,
                corner_radius=5,
                command=cmd,
            ).pack(side="left", padx=3)

        ctk.CTkButton(
            tinner, text="↓  Oto. Kaydır",
            font=ctk.CTkFont(family=FONT_SANS, size=11),
            height=26, width=100,
            fg_color=PAU_BLUE_DARK,
            hover_color=PAU_BLUE,
            text_color=TEXT_SECONDARY,
            corner_radius=5,
        ).pack(side="right", padx=3)

        # Console textbox
        self.console_box = ctk.CTkTextbox(
            p,
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            fg_color=STEEL_DEEP,
            text_color="#334455",
            corner_radius=0,
            border_width=0,
            wrap="word",
            state="disabled",
        )
        self.console_box.pack(fill="both", expand=True, padx=28, pady=(0, 28))

    def _attach_log_handler(self):
        handler = TextboxLogHandler(self.console_box)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def _console_copy(self):
        try:
            text = self.console_box._textbox.get("1.0", "end-1c")
            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception:
            pass

    def _console_save(self):
        try:
            text = self.console_box._textbox.get("1.0", "end-1c")
            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Metin Dosyası", "*.txt"), ("Tüm Dosyalar", "*.*")],
                title="Konsol Günlüğünü Kaydet",
            )
            if path:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(text)
        except Exception:
            pass

    def _console_clear(self):
        self.console_box._textbox.configure(state="normal")
        self.console_box._textbox.delete("1.0", "end")
        self.console_box._textbox.configure(state="disabled")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 4 — KULLANIM KILAVUZU
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_guide_tab(self):
        p = self.tab_guide

        container = ctk.CTkFrame(p, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=28, pady=24)

        # Left: step number nav
        nav = ctk.CTkFrame(container, fg_color="transparent", width=56)
        nav.pack(side="left", fill="y", padx=(0, 20))
        nav.pack_propagate(False)

        self._guide_step_btns = []
        for i in range(len(GUIDE_STEPS)):
            n = i + 1
            btn = ctk.CTkButton(
                nav, text=str(n),
                font=ctk.CTkFont(family=FONT_SANS, size=14, weight="bold"),
                width=40, height=40, corner_radius=20,
                fg_color=PAU_BLUE if n == 1 else STEEL_FRAME_MID,
                hover_color=PAU_BLUE_DARK,
                text_color=TEXT_BRIGHT if n == 1 else TEXT_MUTED,
                command=lambda x=n: self._show_guide_step(x),
            )
            btn.pack(pady=4)
            self._guide_step_btns.append(btn)

        # Right: scrollable content
        self._guide_scroll = ctk.CTkScrollableFrame(
            container, fg_color="transparent",
            scrollbar_button_color=STEEL_ACCENT,
        )
        self._guide_scroll.pack(side="left", fill="both", expand=True)

        self._guide_step_card = None
        self._show_guide_step(1)

        # FAQ section
        ctk.CTkFrame(self._guide_scroll, height=1, fg_color=STEEL_ACCENT).pack(
            fill="x", pady=(20, 12))
        ctk.CTkLabel(
            self._guide_scroll, text="S I K   S O R U L A N   S O R U L A R",
            font=ctk.CTkFont(family=FONT_SANS, size=10, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 6))

        for i, (q, a) in enumerate(FAQS):
            self._build_faq_item(self._guide_scroll, q, a)

    def _show_guide_step(self, step_num):
        if self._guide_step_card and self._guide_step_card.winfo_exists():
            self._guide_step_card.destroy()

        for i, btn in enumerate(self._guide_step_btns):
            n = i + 1
            btn.configure(
                fg_color=PAU_BLUE if n == step_num else STEEL_FRAME_MID,
                text_color=TEXT_BRIGHT if n == step_num else TEXT_MUTED,
            )

        title, body = GUIDE_STEPS[step_num - 1]
        card = ctk.CTkFrame(
            self._guide_scroll,
            fg_color=STEEL_FRAME_MID,
            border_color="#A0AAB5",
            border_width=1,
            corner_radius=12,
        )
        card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            card, text=f"{step_num}. {title}",
            font=ctk.CTkFont(family=FONT_SANS, size=16, weight="bold"),
            text_color=TEXT_BRIGHT, anchor="w",
        ).pack(fill="x", padx=26, pady=(22, 8))

        ctk.CTkLabel(
            card, text=body,
            font=ctk.CTkFont(family=FONT_SANS, size=13),
            text_color=TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=500,
        ).pack(fill="x", padx=26, pady=(0, 22))

        self._guide_step_card = card

    def _build_faq_item(self, parent, question, answer):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x")

        ctk.CTkFrame(wrapper, height=1, fg_color="#A0AAB5").pack(fill="x")

        header_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        header_row.pack(fill="x", pady=10)

        q_lbl = ctk.CTkLabel(
            header_row, text=question,
            font=ctk.CTkFont(family=FONT_SANS, size=13, weight="bold"),
            text_color=TEXT_SECONDARY, anchor="w",
        )
        q_lbl.pack(side="left", fill="x", expand=True)

        toggle_lbl = ctk.CTkLabel(
            header_row, text="+",
            font=ctk.CTkFont(size=18),
            text_color=TEXT_MUTED, width=24,
        )
        toggle_lbl.pack(side="right")

        a_lbl = ctk.CTkLabel(
            wrapper, text=answer,
            font=ctk.CTkFont(family=FONT_SANS, size=12),
            text_color=TEXT_MUTED,
            anchor="w", justify="left", wraplength=480,
        )
        state = {"open": False}

        def toggle(_=None):
            state["open"] = not state["open"]
            if state["open"]:
                a_lbl.pack(fill="x", pady=(0, 10))
                toggle_lbl.configure(text="−")
            else:
                a_lbl.pack_forget()
                toggle_lbl.configure(text="+")

        for w in [header_row, q_lbl, toggle_lbl]:
            w.bind("<Button-1>", toggle)
            w.configure(cursor="hand2")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 5 — TEKNİK BİLGİLER
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_technical_tab(self):
        scroll = ctk.CTkScrollableFrame(
            self.tab_technical, fg_color="transparent",
            scrollbar_button_color=STEEL_ACCENT,
        )
        scroll.pack(fill="both", expand=True, padx=36, pady=24)

        # ── Model Kartları ────────────────────────────────────────────────────
        ctk.CTkLabel(scroll,
                     text="Y A P A Y   Z E K A   M O D E L L E R İ",
                     font=ctk.CTkFont(family=FONT_SANS, size=10, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(anchor="w", pady=(0, 12))

        MODEL_TECH = [
            {
                "id":    "faster-whisper-tiny",
                "name":  "Tiny",
                "size":  "75 MB",
                "desc":  "En hızlı model. Kısa notlar ve hızlı taramalar için idealdir.",
                "tip": (
                    "Parametreler: 39 M\n"
                    "Doğruluk (WER): Düşük\n"
                    "Hız Çarpanı:   ~8×\n"
                    "RAM Kullanımı: ~1 GB\n"
                    "Quantization:  int8\n"
                    "Dil Desteği:   99+"
                ),
            },
            {
                "id":    "faster-whisper-base",
                "name":  "Base",
                "size":  "145 MB",
                "desc":  "Tiny'den daha doğru. Gündelik kısa kayıtlar için yeterlidir.",
                "tip": (
                    "Parametreler: 74 M\n"
                    "Doğruluk (WER): Orta-düşük\n"
                    "Hız Çarpanı:   ~6×\n"
                    "RAM Kullanımı: ~1 GB\n"
                    "Quantization:  int8\n"
                    "Dil Desteği:   99+"
                ),
            },
            {
                "id":    "faster-whisper-small",
                "name":  "Small",
                "size":  "465 MB",
                "desc":  "Hız ve doğruluk dengesi. Standart akademik görüşmeler için uygundur.",
                "tip": (
                    "Parametreler: 244 M\n"
                    "Doğruluk (WER): Orta\n"
                    "Hız Çarpanı:   ~4×\n"
                    "RAM Kullanımı: ~2 GB\n"
                    "Quantization:  int8\n"
                    "Dil Desteği:   99+"
                ),
            },
            {
                "id":    "faster-whisper-medium",
                "name":  "Medium  ★ Önerilir",
                "size":  "1.4 GB",
                "desc":  "Akademik transkripsiyon için en dengeli seçim. Türkçe desteği güçlüdür.",
                "tip": (
                    "Parametreler: 769 M\n"
                    "Doğruluk (WER): Yüksek\n"
                    "Hız Çarpanı:   ~2×\n"
                    "RAM Kullanımı: ~3 GB\n"
                    "Quantization:  int8\n"
                    "Dil Desteği:   99+"
                ),
            },
            {
                "id":    "faster-whisper-large-v2",
                "name":  "Large v2",
                "size":  "3.1 GB",
                "desc":  "En yüksek doğruluk. Uzun ve karmaşık akademik içerikler için idealdir.",
                "tip": (
                    "Parametreler: 1550 M\n"
                    "Doğruluk (WER): Çok Yüksek\n"
                    "Hız Çarpanı:   ~1×\n"
                    "RAM Kullanımı: ~6 GB\n"
                    "Quantization:  int8\n"
                    "Dil Desteği:   99+"
                ),
            },
        ]

        for m in MODEL_TECH:
            installed = Transcriber.find_model_path(m["id"]) is not None
            self._build_tech_model_card(scroll, m, installed)

        # ── Sistem Bilgileri ──────────────────────────────────────────────────
        ctk.CTkFrame(scroll, height=1, fg_color=STEEL_ACCENT).pack(fill="x", pady=(24, 16))
        ctk.CTkLabel(scroll,
                     text="S İ S T E M   B İ L G İ L E R İ",
                     font=ctk.CTkFont(family=FONT_SANS, size=10, weight="bold"),
                     text_color=TEXT_MUTED, anchor="w").pack(anchor="w", pady=(0, 10))

        sys_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        sys_grid.pack(fill="x")
        sys_grid.columnconfigure(0, weight=1)
        sys_grid.columnconfigure(1, weight=1)

        rows = self._collect_sys_info()
        for i, (lbl, val) in enumerate(rows):
            r, c = divmod(i, 2)
            cell = ctk.CTkFrame(sys_grid, fg_color=STEEL_FRAME_MID,
                                corner_radius=8, border_width=1, border_color="#C9C5BC")
            cell.grid(row=r, column=c, sticky="ew", padx=(0, 8) if c == 0 else 0, pady=4)
            inner = ctk.CTkFrame(cell, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)
            ctk.CTkLabel(inner, text=lbl,
                         font=ctk.CTkFont(family=FONT_SANS, size=10),
                         text_color=TEXT_MUTED, anchor="w").pack(anchor="w")
            ctk.CTkLabel(inner, text=val,
                         font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
                         text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w")

    def _build_tech_model_card(self, parent, m, installed):
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=12,
                            border_width=1, border_color="#D6D3CA")
        card.pack(fill="x", pady=(0, 8))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)

        # Left: name + desc
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        name_row = ctk.CTkFrame(left, fg_color="transparent")
        name_row.pack(anchor="w")

        ctk.CTkLabel(name_row, text=m["name"],
                     font=ctk.CTkFont(family=FONT_SANS, size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        # Installed badge
        if installed:
            bdg = ctk.CTkFrame(name_row, fg_color="#D1FAE5", corner_radius=6)
            bdg.pack(side="left", padx=(10, 0))
            ctk.CTkLabel(bdg, text=" ✓ Yüklü ",
                         font=ctk.CTkFont(family=FONT_SANS, size=9, weight="bold"),
                         text_color="#065F46").pack(padx=4, pady=2)
        else:
            bdg = ctk.CTkFrame(name_row, fg_color="#F3F4F6", corner_radius=6)
            bdg.pack(side="left", padx=(10, 0))
            ctk.CTkLabel(bdg, text=" ⬇ İndirilmedi ",
                         font=ctk.CTkFont(family=FONT_SANS, size=9),
                         text_color=TEXT_MUTED).pack(padx=4, pady=2)

        ctk.CTkLabel(left, text=m["desc"],
                     font=ctk.CTkFont(family=FONT_SANS, size=11),
                     text_color=TEXT_SECONDARY, anchor="w",
                     wraplength=380, justify="left").pack(anchor="w", pady=(4, 0))

        # Right: size + info button
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", anchor="center", padx=(12, 0))

        ctk.CTkLabel(right, text=m["size"],
                     font=ctk.CTkFont(family=FONT_MONO, size=11),
                     text_color=TEXT_MUTED).pack(anchor="e")

        # ⓘ tooltip button
        info_btn = ctk.CTkLabel(right, text=" ⓘ ",
                                font=ctk.CTkFont(family=FONT_SANS, size=16),
                                text_color=PRIMARY, cursor="hand2")
        info_btn.pack(anchor="e", pady=(6, 0))

        tip_text = m["tip"]
        _Tooltip(info_btn, tip_text)

    def _collect_sys_info(self):
        import platform, subprocess, shutil
        rows = []

        # Python
        rows.append(("Python Sürümü", platform.python_version()))

        # OS
        rows.append(("İşletim Sistemi", f"{platform.system()} {platform.release()}"))

        # CPU
        try:
            import psutil
            rows.append(("CPU Çekirdek", str(psutil.cpu_count(logical=False))))
            ram = psutil.virtual_memory()
            rows.append(("Toplam RAM", f"{ram.total // (1024**3)} GB"))
        except ImportError:
            rows.append(("CPU", platform.processor()[:30] or "—"))
            rows.append(("RAM", "—"))

        # FFmpeg
        try:
            from src.utils import get_ffmpeg_path
            ffmpeg = get_ffmpeg_path()
            res = subprocess.run([ffmpeg, "-version"], capture_output=True, text=True, timeout=3)
            ver = res.stdout.splitlines()[0].split("version")[1].strip().split(" ")[0] if res.returncode == 0 else "—"
            rows.append(("FFmpeg", ver))
        except Exception:
            rows.append(("FFmpeg", shutil.which("ffmpeg") and "Sistem PATH" or "Bulunamadı"))

        # CUDA
        try:
            import torch
            cuda = f"CUDA {torch.version.cuda}" if torch.cuda.is_available() else "Yok (CPU modu)"
            rows.append(("CUDA / GPU", cuda))
        except ImportError:
            rows.append(("CUDA / GPU", "torch yüklü değil"))

        # faster-whisper
        try:
            import faster_whisper
            rows.append(("faster-whisper", getattr(faster_whisper, "__version__", "—")))
        except ImportError:
            rows.append(("faster-whisper", "Bulunamadı"))

        return rows

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 6 — HAKKINDA
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_about_tab(self):
        scroll = ctk.CTkScrollableFrame(
            self.tab_about, fg_color="transparent",
            scrollbar_button_color=STEEL_ACCENT,
        )
        scroll.pack(fill="both", expand=True, padx=36, pady=28)

        # Title row with logos
        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 4))

        if self.pau_logo_img:
            ctk.CTkLabel(hdr, image=self.pau_logo_img, text="").pack(side="left", padx=(0, 14))
        if self.iibf_logo_img:
            ctk.CTkLabel(hdr, image=self.iibf_logo_img, text="").pack(side="left", padx=(0, 22))

        tc = ctk.CTkFrame(hdr, fg_color="transparent")
        tc.pack(side="left")

        ctk.CTkLabel(
            tc, text="AKADEMİK TRANSKRİPSİYON ASİSTANI",
            font=ctk.CTkFont(family=FONT_SANS, size=17, weight="bold"),
            text_color=TEXT_BRIGHT, anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            tc, text="Sürüm v1.0.0  ·  Nisan 2026  ·  PAÜ İİBF YZDU Koordinatörlüğü",
            font=ctk.CTkFont(family=FONT_SANS, size=11),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkFrame(scroll, height=1, fg_color=STEEL_ACCENT).pack(fill="x", pady=(20, 20))

        # Feature cards
        features = [
            ("► Yerel İşleme & Gizlilik",
             "Tüm ses analizleri cihazınızda gerçekleşir. Hiçbir veri üçüncü taraflara iletilmez. "
             "KVKK'ya tam uyumludur."),
            ("► MAXQDA & ATLAS.ti Uyumluluğu",
             "TXT ve DOCX çıktıları zaman damgalı formatta üretilir; kalitatif analiz "
             "programlarında doğrudan kullanılabilir."),
            ("► Model Kaynağı & Teknoloji",
             "OpenAI'nin açık kaynaklı Whisper modelinin faster-whisper + CTranslate2 ile "
             "hızlandırılmış versiyonu kullanılmaktadır."),
            ("► Çevrimdışı Çalışma",
             "İnternet bağlantısı gerektirmez. Model bir kez indirilir, sonraki tüm kullanımlar "
             "tamamen çevrimdışıdır."),
        ]

        for title, body in features:
            card = ctk.CTkFrame(
                scroll,
                fg_color=STEEL_FRAME_MID,
                border_color="#A0AAB5",
                border_width=1,
                corner_radius=11,
            )
            card.pack(fill="x", pady=(0, 12))

            ctk.CTkLabel(
                card, text=title,
                font=ctk.CTkFont(family=FONT_SANS, size=13, weight="bold"),
                text_color=TEXT_PRIMARY, anchor="w",
            ).pack(fill="x", padx=20, pady=(15, 4))

            ctk.CTkLabel(
                card, text=body,
                font=ctk.CTkFont(family=FONT_SANS, size=12),
                text_color=TEXT_SECONDARY,
                anchor="w", justify="left", wraplength=560,
            ).pack(fill="x", padx=20, pady=(0, 15))

        # Contact row
        cr = ctk.CTkFrame(scroll, fg_color="transparent")
        cr.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(
            cr,
            text="PAÜ İİBF Yapay Zeka ve Dijital Uygulamalar Koordinatörlüğü",
            font=ctk.CTkFont(family=FONT_SANS, size=12),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(side="left")

    # ═══════════════════════════════════════════════════════════════════════════
    # FILE HANDLING & TRANSCRIPTION
    # ═══════════════════════════════════════════════════════════════════════════

    def select_file(self):
        if self.transcribing:
            return
        paths = filedialog.askopenfilenames(
            title="Dosya Seç",
            filetypes=(
                ("Desteklenen Formatlar", "*.mp3 *.wav *.m4a *.mp4 *.mov *.webm *.flac *.ogg *.mkv"),
                ("Tüm Dosyalar", "*.*"),
            ),
        )
        if paths:
            self._add_files(paths)

    def _on_drop(self, event):
        if self.transcribing: return
        import re
        raw = event.data
        if "{" in raw:
            paths = re.findall(r'\{([^}]+)\}', raw)
        else:
            paths = raw.split()
        self._add_files([p for p in paths if os.path.isfile(p)])

    def _add_files(self, paths):
        added = 0
        for p in paths:
            if p not in self.audio_paths:
                self.audio_paths.append(p)
                added += 1
                
        if added > 0:
            if self.active_idx == -1:
                self.active_idx = 0
                
            self.is_previewing = False
            if self.success_banner and self.success_banner.winfo_exists():
                self.success_banner.destroy()
                
            self._render_queue()
            self.btn_start.configure(state="normal")
            self._set_status(f"{len(self.audio_paths)} dosya analize hazır.", COLOR_INFO)
            self.progress_bar.set(0)

    def _remove_file(self, idx):
        if getattr(self, "is_previewing", False):
            self._stop_preview()
            
        if 0 <= idx < len(self.audio_paths):
            del self.audio_paths[idx]
            
        if not self.audio_paths:
            self.active_idx = -1
            self._show_drop_zone()
            if self.success_banner and self.success_banner.winfo_exists():
                self.success_banner.destroy()
            self.btn_start.configure(state="disabled")
            self._set_status("Sistem hazır. Ses veya video dosyası bekleniyor.", COLOR_SUCCESS)
            self.progress_bar.set(0)
        else:
            if self.active_idx >= len(self.audio_paths):
                self.active_idx = len(self.audio_paths) - 1
            self._render_queue()
            self._set_status(f"{len(self.audio_paths)} dosya analize hazır.", COLOR_INFO)

    def _toggle_preview(self, filepath):
        if self.is_previewing:
            self._stop_preview()
        else:
            self.is_previewing = True
            self.btn_preview.configure(text=" Durdur", image=self.icn_stop, fg_color="#C53030", hover_color="#9B2C2C", text_color=TEXT_INVERSE)
            threading.Thread(target=self._play_preview, args=(filepath,), daemon=True).start()

    def _play_preview(self, filepath):
        import subprocess
        import tempfile
        import winsound
        from src.utils import get_ffmpeg_path
        
        ffmpeg_exe = get_ffmpeg_path()
        if not os.path.exists(ffmpeg_exe):
            ffmpeg_exe = "ffmpeg"
            
        temp_dir = tempfile.gettempdir()
        preview_wav = os.path.join(temp_dir, "pau_preview.wav")
        
        # Extract first 60 seconds as WAV using ffmpeg silently
        cmd = [
            ffmpeg_exe, "-y", "-i", filepath,
            "-t", "60", "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
            preview_wav
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            if self.is_previewing and os.path.exists(preview_wav):
                winsound.PlaySound(preview_wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            logger.error(f"Önizleme hatası: {str(e)}")
            self.after(0, self._stop_preview)

    def _stop_preview(self):
        import winsound
        self.is_previewing = False
        if hasattr(self, "btn_preview") and self.btn_preview.winfo_exists():
            self.btn_preview.configure(text=" Önizle", image=self.icn_play, fg_color=STEEL_ACCENT, hover_color=STEEL_FRAME_HOVER, text_color=TEXT_SECONDARY)
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    def _set_status(self, text, dot_color=COLOR_SUCCESS):
        self.lbl_status.configure(text=text)
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 9, 9, fill=dot_color, outline="")

    def update_status(self, text, percent=None):
        self._set_status(f">> {text}", COLOR_INFO)
        if percent is not None:
            self.progress_bar.set(percent / 100.0)

    def start_transcription(self):
        if self.transcribing or not self.audio_paths:
            return

        selected_formats = []
        if self.var_txt.get():  selected_formats.append("txt")
        if self.var_docx.get(): selected_formats.append("docx")
        if self.var_srt.get():  selected_formats.append("srt")

        if not selected_formats:
            messagebox.showwarning("Eksik İşlem", "Ayarlar sekmesinden en az bir çıktı formatı seçin.")
            return

        # ── Model varlık kontrolü ──────────────────────────────────────────────
        model_name = self.var_model.get()
        if not Transcriber.find_model_path(model_name):
            def _on_download_success():
                # Model indirildi, transkripsiyon başlat
                self.start_transcription()
            dlg = ModelDownloadDialog(self, model_name, on_success=_on_download_success)
            return

        lang_map = {"tr": "tr", "en": "en", "auto": None, "de": "de"}
        language = lang_map.get(self.var_lang.get(), "tr")
        hw       = self.var_hw.get()

        device   = self.config_data.get("device", "cpu") if hw == "auto" else ("cpu" if hw == "cpu" else "cuda")

        self.transcribing = True
        self.cancel_event.clear()
        self.btn_start.configure(state="normal", text="✕ İPTAL ET",
                                 fg_color="#C53030", hover_color="#9B2C2C",
                                 command=self._cancel_transcription)
        
        logger.info("─── YENİ BATCH ANALİZ BAŞLATILDI ───")
        logger.info(f"Kuyruktaki Dosya Sayısı: {len(self.audio_paths)}")
        logger.info(f"Kullanılan Donanım: {device.upper()}")
        logger.info(f"Yapay Zeka Modeli: {self.var_model.get()}")
        logger.info(f"Çıktı Formatları: {', '.join([f.upper() for f in selected_formats])}")

        self.update_status("İşleme başlıyor...", 2)

        threading.Thread(
            target=self._worker,
            args=(language, selected_formats,
                  self.var_model.get(), device,
                  self.config_data.get("compute_type", "int8")),
            daemon=True,
        ).start()

    def _worker(self, language, formats, model_name, device, compute_type):
        try:
            import time
            total_files = len(self.audio_paths)
            
            self.after(10, self.update_status, "AI modeli belleğe yükleniyor...", 5)
            tr = Transcriber(model_name=model_name, device=device, compute_type=compute_type)

            for idx, audio_path in enumerate(self.audio_paths):
                if self.cancel_event.is_set():
                    break
                    
                self.after(0, lambda i=idx: setattr(self, 'active_idx', i))
                self.after(0, self._render_queue)
                
                filename = os.path.basename(audio_path)
                file_start_time = time.time()

                # Use a factory to capture loop variables correctly
                def make_prog(file_idx, total, t_start):
                    def _prog(pct, msg):
                        if self.cancel_event.is_set(): return
                        elapsed = time.time() - t_start
                        eta_str = ""
                        if pct and pct > 0:
                            eta = (elapsed / pct) * (100 - pct)
                            m, s = divmod(int(eta), 60)
                            eta_str = f" | Kalan Süre: ~{m}dk {s}sn"
                        self.after(10, self.update_status,
                                   f"[{file_idx+1}/{total}] {msg}{eta_str}", pct)
                    return _prog

                prog = make_prog(idx, total_files, file_start_time)

                def dl_prog(msg):
                    self.after(10, self.update_status, f"Model İndiriliyor: {msg}")

                self.after(10, self.update_status,
                           f"[{idx+1}/{total_files}] {filename} analiz ediliyor...", 10)

                segments, info = tr.transcribe(
                    audio_path, language=language, progress_callback=prog,
                    download_callback=dl_prog,
                    normalize=self.var_normalize.get(),
                    initial_prompt=self.var_prompt.get(),
                    cancel_event=self.cancel_event
                )

                if self.cancel_event.is_set():
                    continue

                if not segments:
                    logger.warning(f"'{filename}' dosyasından transkript alınamadı (boş sonuç). Atlaniyor.")
                    self.after(10, self.update_status,
                               f"[{idx+1}/{total_files}] {filename} — metin bulunamadı, atlandı.",
                               int((idx+1) / total_files * 100))
                    continue

                self.after(10, self.update_status, f"[{idx+1}/{total_files}] Metin dökümleri birleştiriliyor...", 95)

                base       = os.path.splitext(filename)[0]
                output_dir = os.path.join(os.getcwd(), "outputs")
                os.makedirs(output_dir, exist_ok=True)

                meta = {
                    "Analiz Aracı": "PAÜ İİBF Akademik Transkript Asistanı",
                    "Model":        model_name,
                    "Algılanan Dil": info.language.upper(),
                    "Süre":         f"{int(info.duration)} saniye",
                }
                if "txt"  in formats: export_txt(segments, os.path.join(output_dir, f"{base}.txt"))
                if "docx" in formats: export_docx(segments, os.path.join(output_dir, f"{base}.docx"), meta)
                if "srt"  in formats: export_srt(segments, os.path.join(output_dir, f"{base}.srt"))

            if self.cancel_event.is_set():
                self.after(10, self.update_status, "İşlem kullanıcı tarafından iptal edildi.", 0)
                self.after(50, self._reset_ui)
            else:
                self.after(10, self.update_status, "Tüm işlemler başarıyla tamamlandı. Çıktılar hazır.", 100)
                self.after(50, self._on_done)

        except Exception as exc:
            logger.error(f"Transkripsiyon hatası: {exc}")
            self.after(10, self.update_status, f"Hata: {exc}", 0)
            self.after(50, lambda e=str(exc): messagebox.showerror(
                "İşlem Başarısız",
                f"Analiz sırasında beklenmeyen bir hata oluştu:\n{e}\n\n"
                "Teknik detaylar için logs/app.log dosyasına bakın.",
            ))
            self.after(100, self._reset_ui)

    def _on_done(self):
        self._reset_ui(success=True)
        self._show_success_banner()

    def _reset_ui(self, success=False):
        self.transcribing = False
        self.cancel_event.clear()
        if hasattr(self, "btn_start") and self.btn_start.winfo_exists():
            self.btn_start.configure(
                state="normal",
                text="YENİ ANALİZİ BAŞLAT" if success else "ANALİZİ BAŞLAT",
                fg_color=PAU_BLUE,
                hover_color=PAU_BLUE_DARK,
                command=self.start_transcription
            )
        if not success:
            if not self.audio_paths:
                self._show_drop_zone()
                self._set_status("Sistem hazır.", COLOR_SUCCESS)
            else:
                self._render_queue()
                self._set_status(f"{len(self.audio_paths)} dosya analize hazır.", COLOR_INFO)
            self.progress_bar.set(0)

    def _cancel_transcription(self):
        if not self.transcribing: return
        self.cancel_event.set()
        self.btn_start.configure(state="disabled", text="[ İPTAL EDİLİYOR... ]", fg_color=STEEL_FRAME_MID)
        self.update_status("İşlem durduruluyor, lütfen bekleyin...", 0)

    def open_output_folder(self):
        output_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(output_dir, exist_ok=True)
        import platform, subprocess
        if platform.system() == "Windows":
            os.startfile(output_dir)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", output_dir])
        else:
            subprocess.Popen(["xdg-open", output_dir])


if __name__ == "__main__":
    app = App()
    app.mainloop()# -- Surfaces ---------------------------------------------------------------
SURFACE_BG        = "#F4F5F7"
SURFACE_CARD      = "#FFFFFF"
SURFACE_RAISED    = "#EAECF0"
SURFACE_BORDER    = "#D1D5DB"
SURFACE_HOVER     = "#E8EDF5"
SURFACE_DEEP      = "#F0F2F5"

# -- Sidebar (dark navy) ----------------------------------------------------
SIDEBAR_BG        = "#1C2B3A"
SIDEBAR_HOVER     = "#243548"
SIDEBAR_ACTIVE    = "#2D4A6B"
SIDEBAR_ACCENT    = "#60A5FA"
SIDEBAR_TEXT      = "#CBD5E1"
SIDEBAR_TEXT_ACT  = "#FFFFFF"
SIDEBAR_BORDER    = "#253547"

# -- Legacy aliases ---------------------------------------------------------
STEEL_BG          = SURFACE_BG
STEEL_BG_ALT      = SURFACE_RAISED
STEEL_FRAME       = SURFACE_CARD
STEEL_FRAME_MID   = SURFACE_RAISED
STEEL_FRAME_HOVER = SURFACE_HOVER
STEEL_ACCENT      = "#94A3B8"
STEEL_SURFACE_H   = "#CBD5E1"
STEEL_DEEP        = SURFACE_DEEP
STEEL_HEADER      = "#1C2B3A"

# -- Primary -----------------------------------------------------------------
PRIMARY           = "#1E40AF"
PRIMARY_DARK      = "#1E3A8A"
PRIMARY_LIGHT     = "#DBEAFE"
ACCENT_GOLD       = "#F59E0B"
PAU_BLUE          = PRIMARY
PAU_BLUE_DARK     = PRIMARY_DARK
PAU_BLUE_LIGHT    = "#3B82F6"

# -- Text -------------------------------------------------------------------
TEXT_BRIGHT       = "#FFFFFF"
TEXT_PRIMARY      = "#111827"
TEXT_SECONDARY    = "#374151"
TEXT_MUTED        = "#6B7280"
TEXT_INVERSE      = "#FFFFFF"

# -- Semantic ----------------------------------------------------------------
COLOR_SUCCESS     = "#16A34A"
COLOR_WARNING     = "#D97706"
COLOR_ERROR       = "#DC2626"
COLOR_INFO        = PRIMARY

# -- Typography --------------------------------------------------------------
FONT_SANS = "Segoe UI Variable Display" if sys.platform == "win32" else "Inter"
FONT_MONO = "Consolas"

# Whisper model definitions
WHISPER_MODELS = [
    {"id": "faster-whisper-tiny",     "name": "Tiny",   "size": "75 MB",  "speed": 3, "acc": 2, "rec": False},
    {"id": "faster-whisper-base",     "name": "Base",   "size": "145 MB", "speed": 3, "acc": 3, "rec": False},
    {"id": "faster-whisper-small",    "name": "Small",  "size": "465 MB", "speed": 2, "acc": 3, "rec": False},
    {"id": "faster-whisper-medium",   "name": "Medium", "size": "1.4 GB", "speed": 2, "acc": 4, "rec": True},
    {"id": "faster-whisper-large-v2", "name": "Large",  "size": "3.1 GB", "speed": 1, "acc": 5, "rec": False},
]

GUIDE_STEPS = [
    ("Dosyayı Yükleyin",
     "Ana İşlem sekmesindeki alana ses veya video dosyanızı sürükleyin ya da\n"
     "tıklayarak seçin. Desteklenen formatlar: MP3, WAV, M4A, FLAC, MP4, MKV, MOV."),
    ("Ayarları Yapın",
     "Ayarlar sekmesinden Whisper modelini, hedef dili ve çıktı formatlarını seçin.\n"
     "Akademik araştırmalar için 'Medium' modeli önerilir."),
    ("Analizi Başlatın",
     "'ANALİZİ BAŞLAT' butonuna tıklayın. Tüm işlem cihazınızda gerçekleşir.\n"
     "İnternet gerekmez, hiçbir ses verisi dışarıya iletilmez."),
    ("İlerlemeyi İzleyin",
     "İlerleme çubuğu ve durum mesajı süreci gösterir.\n"
     "İşlem süresi ses uzunluğu ve donanımınıza göre değişir."),
    ("Çıktıları Alın",
     "'Klasörü Aç' ile outputs/ klasörünü açın.\n"
     "TXT/DOCX dosyaları MAXQDA ve ATLAS.ti ile doğrudan kullanılabilir."),
]

FAQS = [
    ("İnternet bağlantısı gerekiyor mu?",
     "Hayır. Model bir kez indirilir, tüm işlemler çevrimdışı gerçekleşir."),
    ("MAXQDA ile nasıl kullanırım?",
     "TXT çıktısı doğrudan MAXQDA'ya aktarılabilir. Zaman damgaları MAXQDA formatıyla uyumludur."),
    ("GPU olmadan çalışır mı?",
     "Evet. Uygulama CPU'da int8 optimizasyonuyla çalışır. GPU varsa otomatik kullanılır."),
    ("Desteklenen dosya formatları nelerdir?",
     "MP3, WAV, M4A, FLAC, OGG, MP4, MKV, MOV, WEBM formatları desteklenmektedir."),
]


# ─── LOG HANDLER ──────────────────────────────────────────────────────────────

class TextboxLogHandler(logging.Handler):
    """Streams log records into a CTkTextbox with per-level color tags."""

    LEVEL_LABELS = {
        "INFO":     "BİLGİ",
        "WARNING":  "UYARI",
        "ERROR":    "HATA",
        "CRITICAL": "KRİTİK",
        "DEBUG":    "HATA AYIKLA",
    }

    def __init__(self, textbox: ctk.CTkTextbox):
        super().__init__()
        self.textbox = textbox
        tb = textbox._textbox
        tb.tag_configure("ts",       foreground="#708090", font=(FONT_MONO, 11))
        tb.tag_configure("INFO",     foreground=COLOR_INFO,    font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("WARNING",  foreground=COLOR_WARNING, font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("ERROR",    foreground=COLOR_ERROR,   font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("CRITICAL", foreground=COLOR_ERROR,   font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("DEBUG",    foreground=TEXT_MUTED,    font=(FONT_MONO, 11, "bold"))
        tb.tag_configure("msg",      foreground="#334455",     font=(FONT_MONO, 11))

    def emit(self, record):
        try:
            import time
            ts    = time.strftime("%H:%M:%S", time.localtime(record.created))
            level = record.levelname
            label = self.LEVEL_LABELS.get(level, level)
            msg   = record.getMessage()
            tb    = self.textbox._textbox

            def _insert():
                tb.configure(state="normal")
                tb.insert("end", f"{ts}  ", "ts")
                tb.insert("end", f"[{label}]  ", level)
                tb.insert("end", f"{msg}\n", "msg")
                tb.see("end")
                tb.configure(state="disabled")

            self.textbox.after(0, _insert)
        except Exception:
            pass


# ─── WAVEFORM CANVAS ──────────────────────────────────────────────────────────

class WaveformCanvas(tk.Canvas):
    """Decorative static waveform bar visualization."""

    BARS = [6, 10, 16, 22, 12, 26, 18, 12, 24, 16, 22, 8, 16, 20, 14, 28, 20, 10, 22, 16]

    def __init__(self, master, bg_color, **kwargs):
        super().__init__(master, height=28, bg=bg_color, highlightthickness=0, **kwargs)
        self.bind("<Configure>", self._draw)

    def _draw(self, _=None):
        self.delete("all")
        x = 0
        for h in self.BARS:
            y1 = (28 - h) // 2
            self.create_rectangle(x, y1, x + 2, y1 + h, fill=PAU_BLUE_LIGHT, outline="")
            x += 5


# ─── DROP ZONE (DASHED BORDER VIA CANVAS) ────────────────────────────────────

class DropZone(tk.Canvas):
    """Canvas-based drop zone that renders a proper dashed border."""

    def __init__(self, master, on_click, **kwargs):
        super().__init__(
            master,
            highlightthickness=0,
            bg=SURFACE_DEEP,
            **kwargs,
        )
        self._on_click = on_click
        self._hover    = False
        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>",  lambda _: on_click())
        self.bind("<Enter>",     lambda _: self._set_hover(True))
        self.bind("<Leave>",     lambda _: self._set_hover(False))

    def _set_hover(self, state):
        self._hover = state
        self._draw()

    def _draw(self, _=None):
        self.delete("all")
        w = self.winfo_width()  or 400
        h = self.winfo_height() or 150
        # Background fill
        self.configure(bg=SURFACE_HOVER if self._hover else SURFACE_DEEP)
        border_color = PRIMARY if self._hover else SURFACE_BORDER
        self.create_rectangle(
            8, 8, w - 8, h - 8,
            outline=border_color, dash=(8, 5), width=2,
        )
        # Upload icon circle
        cx, cy_icon = w // 2, h // 2 - 28
        r = 26
        icon_fill   = PRIMARY_LIGHT if self._hover else "#EFF6FF"
        self.create_oval(cx - r, cy_icon - r, cx + r, cy_icon + r,
                         fill=icon_fill, outline="")
        self.create_text(cx, cy_icon, text="↑",
                         font=(FONT_SANS, 16, "bold"),
                         fill=PRIMARY if self._hover else TEXT_MUTED)
        # Main label
        label_color = PRIMARY if self._hover else TEXT_SECONDARY
        self.create_text(cx, h // 2 + 10,
                         text="Ses veya Video Dosyası Sürükleyin ya da Tıklayın",
                         font=(FONT_SANS, 13), fill=label_color)
        # Format hint
        self.create_text(cx, h // 2 + 30,
                         text="MP3  ·  WAV  ·  M4A  ·  FLAC  ·  MP4  ·  MKV  ·  MOV",
                         font=(FONT_SANS, 10), fill=TEXT_MUTED)


# ─── MAIN APPLICATION ─────────────────────────────────────────────────────────
