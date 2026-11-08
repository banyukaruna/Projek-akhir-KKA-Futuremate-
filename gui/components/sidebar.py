"""Sidebar navigasi utama FutureMate dengan pemilih tema."""
import customtkinter as ctk
from gui.theme import COLORS, THEMES, get_theme, set_theme

NAV_ITEMS = [
    ("⌂", "Dashboard", "Dashboard"),
    ("▤", "Tugas & Jadwal", "Tugas & Jadwal"),
    ("▥", "Nilai Akademik", "Nilai Akademik"),
    ("✳", "Minat RIASEC", "Minat Bakat"),
    ("▧", "Portofolio", "Portofolio"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate, on_theme_change=None):
        super().__init__(
            master, width=236, corner_radius=0,
            fg_color=COLORS["surface"]
        )
        self.grid_propagate(False)
        self.on_navigate = on_navigate
        self.on_theme_change = on_theme_change
        self.buttons = {}

        ctk.CTkLabel(
            self, text="FutureMate",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=22, pady=(30, 2))

        ctk.CTkLabel(
            self, text="PLAN WITH PURPOSE",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLORS["muted"]
        ).pack(anchor="w", padx=23, pady=(0, 30))

        ctk.CTkLabel(
            self, text="MENU UTAMA",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLORS["muted"]
        ).pack(anchor="w", padx=22, pady=(0, 9))

        for icon, label, page in NAV_ITEMS:
            button = ctk.CTkButton(
                self,
                text=f"  {icon}    {label}",
                anchor="w",
                height=42,
                corner_radius=9,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color=COLORS["surface_alt"],
                text_color=COLORS["muted"],
                command=lambda target=page: self.on_navigate(target),
            )
            button.pack(fill="x", padx=12, pady=3)
            self.buttons[page] = button

        # Pemilih tema
        ctk.CTkLabel(
            self, text="TAMPILAN",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLORS["muted"]
        ).pack(anchor="w", padx=22, pady=(20, 8))

        theme_keys = list(THEMES.keys())
        theme_labels = [THEMES[k]["label"] for k in theme_keys]
        self.theme_var = ctk.StringVar(value=THEMES.get(
            getattr(master, "current_theme", "dark"), THEMES["dark"]
        )["label"])

        def on_theme_selected(choice):
            self.theme_var.set(choice)
            for key, label in zip(theme_keys, theme_labels):
                if label == choice:
                    if self.on_theme_change:
                        self.on_theme_change(key)
                    break

        self.theme_menu = ctk.CTkOptionMenu(
            self,
            values=theme_labels,
            variable=self.theme_var,
            command=on_theme_selected,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["surface_alt"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["surface_alt"],
            dropdown_hover_color=COLORS["primary_soft"],
            dropdown_text_color=COLORS["text"],
            height=32,
            corner_radius=8,
        )
        self.theme_menu.pack(fill="x", padx=12, pady=(0, 18))

        footer = ctk.CTkFrame(
            self, fg_color=COLORS["surface_alt"], corner_radius=10
        )
        footer.pack(side="bottom", fill="x", padx=14, pady=18)
        ctk.CTkLabel(
            footer, text="Belajar hari ini.",
            justify="left", text_color=COLORS["text"],
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w", padx=12, pady=(10, 1))
        ctk.CTkLabel(
            footer, text="Siapkan langkah esok hari.",
            justify="left", text_color=COLORS["muted"],
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=12, pady=(0, 10))

    def set_active(self, active):
        for label, button in self.buttons.items():
            selected = label == active
            button.configure(
                fg_color=COLORS["primary_soft"] if selected else "transparent",
                text_color=COLORS["primary"] if selected else COLORS["muted"],
                hover_color=COLORS["surface_alt"],
                font=ctk.CTkFont(
                    size=13, weight="bold" if selected else "normal"
                ),
            )

    def refresh_theme(self):
        """Perbarui warna dropdown tema setelah ganti tema."""
        self.theme_menu.configure(
            fg_color=COLORS["surface_alt"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["surface_alt"],
            dropdown_hover_color=COLORS["primary_soft"],
            dropdown_text_color=COLORS["text"],
        )

    def update_theme_display(self, theme_key):
        """Tampilkan tema yang sedang aktif pada dropdown."""
        label = get_theme(theme_key).get("label", THEMES["dark"]["label"])
        self.theme_var.set(label)
