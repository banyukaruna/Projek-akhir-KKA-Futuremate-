"""Sidebar navigasi utama FutureMate."""
import customtkinter as ctk
from gui.theme import COLORS

NAV_ITEMS = [
    ("⌂", "Dashboard"),
    ("▤", "Tugas & Jadwal"),
    ("▥", "Nilai Akademik"),
    ("✳", "Minat Bakat"),
    ("▧", "Portofolio"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate):
        super().__init__(
            master, width=236, corner_radius=0,
            fg_color=COLORS["surface"]
        )
        self.grid_propagate(False)
        self.on_navigate = on_navigate
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

        for icon, label in NAV_ITEMS:
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
                command=lambda page=label: self.on_navigate(page),
            )
            button.pack(fill="x", padx=12, pady=3)
            self.buttons[label] = button

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
                fg_color=COLORS["surface_alt"] if selected else "transparent",
                text_color=COLORS["text"] if selected else COLORS["muted"],
                hover_color=COLORS["border"] if selected else COLORS["surface_alt"],
                font=ctk.CTkFont(
                    size=13, weight="bold" if selected else "normal"
                ),
            )
