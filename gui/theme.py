"""Konfigurasi visual FutureMate."""
import customtkinter as ctk

COLORS = {
    "background": "#0B1220",
    "surface": "#111C2E",
    "surface_alt": "#17253A",
    "border": "#26364D",
    "primary": "#19B8A5",
    "primary_hover": "#129889",
    "text": "#F3F6FA",
    "muted": "#9AAAC0",
    "success": "#45C49A",
    "warning": "#F2B65D",
    "danger": "#E87575",
}

def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
