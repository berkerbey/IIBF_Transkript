"""
ModelDownloadDialog — Estetik model indirme onay & progress penceresi.
"""
import threading
import tkinter as tk
import customtkinter as ctk
from src.logger import logger

# Color constants (match gui.py palette)
_BG        = "#F7F6F3"
_CARD      = "#FFFFFF"
_BORDER    = "#D6D3CA"
_PRIMARY   = "#1E40AF"
_P_LIGHT   = "#DBEAFE"
_SUCCESS   = "#16A34A"
_ERROR     = "#DC2626"
_TEXT      = "#111827"
_MUTED     = "#6B7280"
_FONT      = "Segoe UI Variable Display"
_MONO      = "Consolas"

MODEL_META = {
    "faster-whisper-tiny":     {"size": "75 MB",  "label": "Tiny"},
    "faster-whisper-base":     {"size": "145 MB", "label": "Base"},
    "faster-whisper-small":    {"size": "465 MB", "label": "Small"},
    "faster-whisper-medium":   {"size": "1.4 GB", "label": "Medium"},
    "faster-whisper-large-v2": {"size": "3.1 GB", "label": "Large v2"},
}


class ModelDownloadDialog(ctk.CTkToplevel):
    """
    Gösterim:
      - Model zaten indirildiyse bu pencereyi HİÇ açmayın.
      - Açıldığında kullanıcıya onay sor, onaylandığında model indir.
    Kullanım:
        dlg = ModelDownloadDialog(parent, model_name, on_success)
        dlg.grab_set()
    on_success: callable — indirme başarıyla tamamlandığında çağrılır.
    """

    def __init__(self, parent, model_name: str, on_success=None):
        super().__init__(parent)
        self.model_name  = model_name
        self.on_success  = on_success
        self._cancelled  = False
        self._thread     = None

        meta   = MODEL_META.get(model_name, {"size": "?", "label": model_name})
        label  = meta["label"]
        size   = meta["size"]

        self.title("Model İndirme")
        self.geometry("460x340")
        self.resizable(False, False)
        self.configure(fg_color=_BG)
        self.grab_set()
        self.focus_set()

        # Center on parent
        self.after(10, self._center)

        self._build_ui(label, size)

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_width()
        ph = self.master.winfo_height()
        px = self.master.winfo_x()
        py = self.master.winfo_y()
        w, h = 460, 340
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self, label, size):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=_PRIMARY, corner_radius=0, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"  ⬇  Model İndirme Gerekiyor",
                     font=ctk.CTkFont(family=_FONT, size=15, weight="bold"),
                     text_color="#FFFFFF").pack(side="left", padx=20, pady=14)

        # Body
        body = ctk.CTkFrame(self, fg_color=_BG)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(body,
                     text=f"'{label}' modeli henüz indirilmemiş.",
                     font=ctk.CTkFont(family=_FONT, size=14, weight="bold"),
                     text_color=_TEXT, anchor="w").pack(anchor="w")

        ctk.CTkLabel(body,
                     text=(f"Tahmini boyut: {size}\n"
                           "Tüm işlem yerel olarak gerçekleşir.\n"
                           "İndirme tamamlandıktan sonra transkripsiyon otomatik başlar."),
                     font=ctk.CTkFont(family=_FONT, size=12),
                     text_color=_MUTED, anchor="w", justify="left").pack(anchor="w", pady=(6, 16))

        # Progress area (hidden until download starts)
        self._prog_frame = ctk.CTkFrame(body, fg_color=_CARD, corner_radius=10,
                                        border_width=1, border_color=_BORDER)
        self._prog_bar = ctk.CTkProgressBar(self._prog_frame, height=8,
                                            progress_color=_PRIMARY,
                                            fg_color=_P_LIGHT,
                                            corner_radius=4)
        self._prog_bar.set(0)
        self._prog_bar.pack(fill="x", padx=16, pady=(14, 6))
        self._prog_lbl = ctk.CTkLabel(self._prog_frame, text="Başlatılıyor...",
                                      font=ctk.CTkFont(family=_MONO, size=10),
                                      text_color=_MUTED)
        self._prog_lbl.pack(anchor="w", padx=16, pady=(0, 12))

        # Buttons
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x", pady=(8, 0))

        self._btn_cancel = ctk.CTkButton(
            btn_row, text="İptal",
            font=ctk.CTkFont(family=_FONT, size=13),
            height=40, width=120,
            fg_color=_CARD, hover_color="#E8E6E0",
            text_color=_MUTED, border_width=1, border_color=_BORDER,
            corner_radius=8, command=self._cancel)
        self._btn_cancel.pack(side="left")

        self._btn_download = ctk.CTkButton(
            btn_row, text="  ⬇  İndir ve Başlat",
            font=ctk.CTkFont(family=_FONT, size=13, weight="bold"),
            height=40,
            fg_color=_PRIMARY, hover_color="#1E3A8A",
            text_color="#FFFFFF", corner_radius=8,
            command=self._start_download)
        self._btn_download.pack(side="right")

    def _start_download(self):
        self._btn_download.configure(state="disabled", text="İndiriliyor...")
        self._btn_cancel.configure(text="Durdur")
        self._prog_frame.pack(fill="x", pady=(0, 12))
        self._thread = threading.Thread(target=self._download_worker, daemon=True)
        self._thread.start()

    def _download_worker(self):
        try:
            from faster_whisper import WhisperModel
            short = self.model_name.replace("faster-whisper-", "")
            # Load triggers download; intercept tqdm output for progress
            import sys, time, re

            class _Intercept:
                def __init__(self, orig, cb):
                    self.orig, self.cb = orig, cb
                    self._t = 0
                def write(self, s):
                    self.orig.write(s)
                    if time.time() - self._t > 0.15:
                        clean = s.split('\r')[-1].strip()
                        if clean and ('%|' in clean or 'MB' in clean or 'kB' in clean):
                            self.cb(clean)
                            self._t = time.time()
                def flush(self): self.orig.flush()

            def _cb(text):
                # Parse percentage if present
                m = re.search(r'(\d+)%', text)
                pct = int(m.group(1)) / 100 if m else None
                self.after(0, lambda t=text, p=pct: self._update_progress(t, p))

            orig = sys.stderr
            sys.stderr = _Intercept(orig, _cb)
            try:
                WhisperModel(short, device="cpu", compute_type="int8",
                             download_root=str(
                                 __import__('pathlib').Path.cwd() / "models"))
            finally:
                sys.stderr = orig

            if not self._cancelled:
                self.after(0, self._on_done)
        except Exception as e:
            if not self._cancelled:
                self.after(0, lambda: self._on_error(str(e)))

    def _update_progress(self, text, pct):
        if pct is not None:
            self._prog_bar.set(pct)
        self._prog_lbl.configure(text=text[:80])

    def _on_done(self):
        self._prog_bar.set(1.0)
        self._prog_lbl.configure(text="✓  İndirme tamamlandı!", text_color=_SUCCESS)
        self._btn_cancel.configure(state="disabled")
        logger.info(f"Model başarıyla indirildi: {self.model_name}")
        self.after(800, self._finish_success)

    def _finish_success(self):
        self.grab_release()
        self.destroy()
        if self.on_success:
            self.on_success()

    def _on_error(self, msg):
        self._prog_lbl.configure(text=f"Hata: {msg[:60]}", text_color=_ERROR)
        self._btn_download.configure(state="normal", text="Tekrar Dene")
        logger.error(f"Model indirme hatası: {msg}")

    def _cancel(self):
        self._cancelled = True
        self.grab_release()
        self.destroy()
