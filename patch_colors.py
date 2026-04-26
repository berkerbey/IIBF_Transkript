"""
Comprehensive color patch: Replace white/blue UI with Notion-style
dark sidebar + warm off-white content palette.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('src/gui.py', encoding='utf-8') as f:
    src = f.read()

replacements = [
    # ── Content area & topbar background ──────────────────────────────────────
    # App window root bg
    ('self.configure(fg_color=SIDEBAR_BG)',
     'self.configure(fg_color=SURFACE_BG)'),

    # Content area frame
    ('content = ctk.CTkFrame(self, fg_color=SURFACE_BG, corner_radius=0)',
     'content = ctk.CTkFrame(self, fg_color="#F7F6F3", corner_radius=0)'),

    # Topbar: creamy/warm off-white instead of pure white
    ('topbar = ctk.CTkFrame(content, fg_color=SURFACE_CARD, height=72, corner_radius=0)',
     'topbar = ctk.CTkFrame(content, fg_color="#FFFFFF", height=64, corner_radius=0)'),

    # Topbar border
    ('ctk.CTkFrame(content, fg_color=SURFACE_BORDER, height=1, corner_radius=0).pack(fill="x")',
     'ctk.CTkFrame(content, fg_color="#E8E6E1", height=1, corner_radius=0).pack(fill="x")'),

    # Pages container bg
    ('pages = ctk.CTkFrame(content, fg_color=SURFACE_BG, corner_radius=0)',
     'pages = ctk.CTkFrame(content, fg_color="#F7F6F3", corner_radius=0)'),

    # Each tab frame bg
    ('self.tab_main     = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)',
     'self.tab_main     = ctk.CTkFrame(pages, fg_color="#F7F6F3", corner_radius=0)'),
    ('self.tab_settings = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)',
     'self.tab_settings = ctk.CTkFrame(pages, fg_color="#F7F6F3", corner_radius=0)'),
    ('self.tab_console  = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)',
     'self.tab_console  = ctk.CTkFrame(pages, fg_color="#F7F6F3", corner_radius=0)'),
    ('self.tab_guide    = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)',
     'self.tab_guide    = ctk.CTkFrame(pages, fg_color="#F7F6F3", corner_radius=0)'),
    ('self.tab_about    = ctk.CTkFrame(pages, fg_color=SURFACE_BG, corner_radius=0)',
     'self.tab_about    = ctk.CTkFrame(pages, fg_color="#F7F6F3", corner_radius=0)'),

    # Footer bar
    ('ctk.CTkFrame(content, fg_color=SURFACE_BORDER, height=1, corner_radius=0).pack(fill="x", side="bottom")',
     'ctk.CTkFrame(content, fg_color="#E8E6E1", height=1, corner_radius=0).pack(fill="x", side="bottom")'),
    ('footer = ctk.CTkFrame(content, fg_color=SURFACE_CARD, height=30, corner_radius=0)',
     'footer = ctk.CTkFrame(content, fg_color="#FFFFFF", height=30, corner_radius=0)'),

    # ── Right panel ────────────────────────────────────────────────────────────
    ('rp = ctk.CTkFrame(self, fg_color=SURFACE_CARD, width=230, corner_radius=0)',
     'rp = ctk.CTkFrame(self, fg_color="#F0EFE9", width=230, corner_radius=0)'),
    ('tk.Frame(rp, bg=SURFACE_BORDER, width=1).pack(side="left", fill="y")',
     'tk.Frame(rp, bg="#D6D3CA", width=1).pack(side="left", fill="y")'),
    ('card = ctk.CTkFrame(scroll, fg_color=SURFACE_RAISED, corner_radius=8)',
     'card = ctk.CTkFrame(scroll, fg_color="#E8E6E0", corner_radius=8)'),

    # ── Status dot background ─────────────────────────────────────────────────
    ('bg=SURFACE_BG, highlightthickness=0',
     'bg="#F7F6F3", highlightthickness=0'),

    # ── Progress bar ──────────────────────────────────────────────────────────
    ('fg_color=SURFACE_BORDER,\n            corner_radius=2,',
     'fg_color="#DDD9D2",\n            corner_radius=2,'),

    # ── Hover state for file cards ────────────────────────────────────────────
    ('fg_color=SURFACE_HOVER if is_active else SURFACE_CARD',
     'fg_color="#EBE9E4" if is_active else "#FFFFFF"'),

    # ── Card buttons ──────────────────────────────────────────────────────────
    ('fg_color=SURFACE_RAISED, hover_color=PRIMARY_LIGHT,',
     'fg_color="#E8E6E0", hover_color="#D4EDDA",'),
    ('fg_color=SURFACE_RAISED, hover_color="#FEE2E2"',
     'fg_color="#E8E6E0", hover_color="#FDDEDE"'),

    # ── "Dosya Sec" browse btn ────────────────────────────────────────────────
    ('fg_color=SURFACE_CARD,\n            hover_color=SURFACE_HOVER,\n            text_color=TEXT_SECONDARY,\n            corner_radius=8,\n            border_width=1,\n            border_color=SURFACE_BORDER,\n        )\n        self.btn_browse.pack',
     'fg_color="#FFFFFF",\n            hover_color="#EBE9E4",\n            text_color=TEXT_SECONDARY,\n            corner_radius=8,\n            border_width=1,\n            border_color="#D6D3CA",\n        )\n        self.btn_browse.pack'),

    # ── Append files button ────────────────────────────────────────────────────
    ('hover_color=SURFACE_HOVER,\n            text_color=PRIMARY,\n            border_width=1,\n            border_color=PRIMARY_LIGHT,',
     'hover_color="#EBE9E4",\n            text_color=PRIMARY,\n            border_width=1,\n            border_color="#BFD4F7",'),

    # ── "Klasoru Ac" secondary button ─────────────────────────────────────────
    ('fg_color=SURFACE_CARD,\n            hover_color=SURFACE_HOVER,\n            text_color=TEXT_SECONDARY,\n            corner_radius=10,\n            border_width=1,\n            border_color=SURFACE_BORDER,\n        )\n        self.btn_open_folder',
     'fg_color="#FFFFFF",\n            hover_color="#EBE9E4",\n            text_color=TEXT_SECONDARY,\n            corner_radius=10,\n            border_width=1,\n            border_color="#D6D3CA",\n        )\n        self.btn_open_folder'),

    # ── DropZone bg ───────────────────────────────────────────────────────────
    ('bg=SURFACE_HOVER if self._hover else SURFACE_DEEP',
     'bg="#EBE9E4" if self._hover else "#F0EEE9"'),
    ('border_color = PRIMARY if self._hover else SURFACE_BORDER',
     'border_color = PRIMARY if self._hover else "#C9C5BC"'),
    ('icon_fill   = PRIMARY_LIGHT if self._hover else "#EFF6FF"',
     'icon_fill   = PRIMARY_LIGHT if self._hover else "#E8E6E0"'),

    # ── Success banner ────────────────────────────────────────────────────────
    ('fg_color="#ECFDF5",\n            corner_radius=12,',
     'fg_color="#D4EDDA",\n            corner_radius=12,'),
]

count = 0
for old, new in replacements:
    if old in src:
        src = src.replace(old, new, 1)
        count += 1
    else:
        print(f"  MISS: {old[:60]!r}")

with open('src/gui.py', 'w', encoding='utf-8') as f:
    f.write(src)

print(f"\nApplied {count}/{len(replacements)} replacements.")
