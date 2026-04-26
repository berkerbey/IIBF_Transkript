"""
WelcomeDialog — İlk çalıştırmada gösterilen estetik bilgilendirme ekranı.
"""
import os
import json
import tkinter as tk
import customtkinter as ctk
from PIL import Image

# ─── DESIGN TOKENS ────────────────────────────────────────────────────────────
_BG_RIGHT    = "#FAFAF8"    # Çok hafif krem/beyaz arası premium arkaplan
_BG_LEFT     = "#0F172A"    # Çok koyu lacivert/siyah arası (Notion Dark mode / Modern AI)
_PRIMARY     = "#2563EB"    # Canlı mavi
_PRIMARY_H   = "#1D4ED8"    # Hover mavi
_TEXT_MAIN   = "#0F172A"    # Siyahımsı koyu lacivert
_TEXT_MUTED  = "#64748B"    # Slate gri
_BORDER      = "#E2E8F0"
_FONT        = "Segoe UI Variable Display"

class WelcomeDialog(ctk.CTkToplevel):
    def __init__(self, parent, config_path="config.json"):
        super().__init__(parent)
        self.parent = parent
        self.config_path = config_path

        self.title("Hoş Geldiniz — PAÜ İİBF Transkripsiyon Aracı")
        self.geometry("820x520")
        self.resizable(False, False)
        self.configure(fg_color=_BG_RIGHT)
        
        # Make the window completely borderless/modern if supported, otherwise just a clean dialog
        self.overrideredirect(True) # Borderless window for a premium installer feel
        
        self.grab_set()
        self.focus_set()

        # Outline border for the borderless window
        self._main_frame = ctk.CTkFrame(self, fg_color=_BG_RIGHT, corner_radius=12, 
                                        border_width=1, border_color="#CBD5E1")
        self._main_frame.pack(fill="both", expand=True)

        self.after(10, self._center)
        self._build_ui()

    def _center(self):
        self.update_idletasks()
        pw = self.master.winfo_width()
        ph = self.master.winfo_height()
        px = self.master.winfo_x()
        py = self.master.winfo_y()
        w, h = 820, 520
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # ─── LAYOUT: 2 Columns ────────────────────────────────────────────────
        
        # LEFT PANEL (Dark, Branding)
        left_panel = ctk.CTkFrame(self._main_frame, fg_color=_BG_LEFT, corner_radius=0, width=280)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        # RIGHT PANEL (Content)
        right_panel = ctk.CTkFrame(self._main_frame, fg_color="transparent", corner_radius=0)
        right_panel.pack(side="right", fill="both", expand=True)
        
        self._build_left_panel(left_panel)
        self._build_right_panel(right_panel)

    def _build_left_panel(self, parent):
        # Logos and Branding
        logo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        logo_frame.pack(pady=(40, 20))

        # Try to load logos
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        pau_path = os.path.join(assets_dir, "pau_logo.png")
        iibf_path = os.path.join(assets_dir, "iibf_logo.png")
        
        logo_size = 80
        
        if os.path.exists(pau_path):
            try:
                img = Image.open(pau_path)
                pau_img = ctk.CTkImage(light_image=img, dark_image=img, size=(logo_size, logo_size))
                ctk.CTkLabel(logo_frame, image=pau_img, text="").pack(pady=(0, 15))
            except: pass

        if os.path.exists(iibf_path):
            try:
                img = Image.open(iibf_path)
                # IIBF logo is usually taller
                iibf_img = ctk.CTkImage(light_image=img, dark_image=img, size=(logo_size*0.75, logo_size))
                ctk.CTkLabel(logo_frame, image=iibf_img, text="").pack(pady=(0, 20))
            except: pass

        # Vertical Title or Decorative text
        ctk.CTkLabel(parent, 
                     text="YAPAY ZEKA VE\nDİJİTAL UYGULAMALAR\nKOORDİNATÖRLÜĞÜ", 
                     font=ctk.CTkFont(family=_FONT, size=11, weight="bold"),
                     text_color="#94A3B8", 
                     justify="center").pack(pady=(20, 0))

        # Bottom version info
        ctk.CTkLabel(parent, 
                     text="Sürüm 1.0\n2026 © Tüm Hakları Saklıdır", 
                     font=ctk.CTkFont(family=_FONT, size=9),
                     text_color="#475569",
                     justify="center").pack(side="bottom", pady=24)

    def _build_right_panel(self, parent):
        # Top right corner close button (since it's borderless)
        close_btn = ctk.CTkButton(parent, text="✕", width=30, height=30, 
                                  fg_color="transparent", hover_color="#F1F5F9", 
                                  text_color=_TEXT_MUTED, font=("Arial", 14),
                                  command=self._on_accept)
        close_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # Content Container
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=48, pady=48)

        # Header
        ctk.CTkLabel(content, 
                     text="Akademik Transkripsiyon Asistanı", 
                     font=ctk.CTkFont(family=_FONT, size=24, weight="bold"),
                     text_color=_TEXT_MAIN, anchor="w").pack(anchor="w", pady=(10, 4))
        
        ctk.CTkLabel(content, 
                     text="Araştırmacılar için güvenli, yerel ve yüksek doğruluklu çözümleme.", 
                     font=ctk.CTkFont(family=_FONT, size=14),
                     text_color=_TEXT_MUTED, anchor="w").pack(anchor="w", pady=(0, 32))

        # Features List
        features = [
            ("⚡ OpenAI Whisper Altyapısı", "Dünyanın en gelişmiş açık kaynaklı ses tanıma modelinin donanım hızlandırmalı versiyonunu kullanır."),
            ("🔒 %100 Yerel İşleme ve Gizlilik", "Hiçbir veri internete veya üçüncü şahıslara iletilmez. KVKK standartlarına tam uyumludur."),
            ("📊 MAXQDA & ATLAS.ti Uyumluluğu", "Zaman damgalı özel TXT ve DOCX çıktıları sayesinde nitel analiz programlarına anında aktarım yapılabilir."),
        ]

        for icon_title, desc in features:
            f = ctk.CTkFrame(content, fg_color="transparent")
            f.pack(fill="x", pady=10)
            
            ctk.CTkLabel(f, text=icon_title, 
                         font=ctk.CTkFont(family=_FONT, size=13, weight="bold"), 
                         text_color=_TEXT_MAIN, anchor="w").pack(anchor="w")
                         
            ctk.CTkLabel(f, text=desc, 
                         font=ctk.CTkFont(family=_FONT, size=12), 
                         text_color=_TEXT_MUTED, anchor="w", 
                         justify="left", wraplength=420).pack(anchor="w", pady=(2, 0))

        # Spacer
        ctk.CTkFrame(content, fg_color="transparent", height=1).pack(fill="both", expand=True)

        # Action Area
        action_frame = ctk.CTkFrame(content, fg_color="transparent")
        action_frame.pack(fill="x", side="bottom")

        # Academic Notice
        ctk.CTkLabel(action_frame, 
                     text="Bu yazılım PAÜ İİBF akademik personeli için özel olarak geliştirilmiştir.", 
                     font=ctk.CTkFont(family=_FONT, size=11, slant="italic"),
                     text_color=_TEXT_MUTED, anchor="w").pack(side="left")

        # Start Button
        ctk.CTkButton(
            action_frame, 
            text="Başla ➔",
            font=ctk.CTkFont(family=_FONT, size=13, weight="bold"),
            height=40, width=120,
            fg_color=_PRIMARY, hover_color=_PRIMARY_H,
            text_color="#FFFFFF", corner_radius=6,
            command=self._on_accept
        ).pack(side="right")

    def _on_accept(self):
        # Update config to mark welcome as shown
        try:
            config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            config["welcome_shown"] = True
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            import logging
            logging.error(f"Could not save welcome_shown config: {e}")

        self.grab_release()
        self.destroy()
