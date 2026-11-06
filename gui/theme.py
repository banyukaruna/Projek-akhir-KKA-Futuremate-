"""Konfigurasi visual FutureMate dengan palet hangat dan natural."""
import customtkinter as ctk

COLORS = {
    "background": "#F4F3EE",
    "surface": "#FFFFFF",
    "surface_alt": "#E9EEE8",
    "border": "#D9E0D7",
    "primary": "#B8CBB9",
    "primary_hover": "#A5BBA8",
    "text": "#26352D",
    "muted": "#77837A",
    "success": "#63866B",
    "warning": "#B98545",
    "danger": "#B85C54",
}

def apply_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
