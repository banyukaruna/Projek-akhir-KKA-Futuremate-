"""Sistem desain FutureMate dengan tema gelap dan aksen hijau lembut."""
import customtkinter as ctk

COLORS = {
    "background": "#111416",
    "surface": "#1A1F22",
    "surface_alt": "#242B2F",
    "border": "#303A3F",
    "primary": "#79A98B",
    "primary_hover": "#689879",
    "primary_soft": "#294237",
    "text": "#E7ECE9",
    "muted": "#A0AAA5",
    "success": "#83B894",
    "warning": "#D7AA68",
    "danger": "#D87979",
    "danger_hover": "#C76868",
}

def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
