"""Sidebar navigasi utama FutureMate."""
import customtkinter as ctk
from gui.theme import COLORS

NAV_ITEMS = [
    ("⌂", "Dashboard"),
    ("▤", "Tugas & Jadwal"),
    ("▥", "Nilai Akademik"),
    ("◎", "Target Masa Depan"),
    ("✳", "Tes Minat"),
    ("▧", "Portofolio"),
]

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate):
        super().__init__(master, width=236, corner_radius=0, fg_color=COLORS["surface"])
        self.grid_propagate(False)
        self.on_navigate = on_navigate
        self.buttons = {}
        ctk.CTkLabel(self, text="FutureMate", font=ctk.CTkFont(size=25, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=22, pady=(28, 2))
        ctk.CTkLabel(self, text="SHAPE YOUR FUTURE", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=COLORS["primary"]).pack(anchor="w", padx=23, pady=(0, 28))
        for icon, label in NAV_ITEMS:
            button = ctk.CTkButton(
                self, text=f"  {icon}    {label}", anchor="w", height=43,
                corner_radius=10, font=ctk.CTkFont(size=13),
                fg_color="transparent", hover_color=COLORS["surface_alt"],
                text_color=COLORS["muted"],
                command=lambda page=label: self.on_navigate(page),
            )
            button.pack(fill="x", padx=12, pady=3)
            self.buttons[label] = button
        ctk.CTkLabel(self, text="Belajar hari ini.\nSiap untuk masa depan.",
                     justify="left", text_color=COLORS["muted"],
                     font=ctk.CTkFont(size=11)).pack(side="bottom", anchor="w", padx=22, pady=24)

    def set_active(self, active):
        for label, button in self.buttons.items():
            selected = label == active
            button.configure(
                fg_color=COLORS["primary"] if selected else "transparent",
                text_color="#071923" if selected else COLORS["muted"],
                hover_color=COLORS["primary_hover"] if selected else COLORS["surface_alt"],
                font=ctk.CTkFont(size=13, weight="bold" if selected else "normal"),
            )
