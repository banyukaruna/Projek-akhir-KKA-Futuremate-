"""Sistem desain FutureMate dengan berbagai tema warna unik.

Tema yang tersedia: dark, light, ocean, sunset, forest, midnight, cyberpunk.
Gunakan set_theme(nama) untuk mengganti tema secara runtime.
"""
import customtkinter as ctk

THEMES = {
    "dark": {
        "label": "Gelap Elegan",
        "background": "#0F1214",
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
    },
    "light": {
        "label": "Cerah Sejuk",
        "background": "#F5F7F6",
        "surface": "#FFFFFF",
        "surface_alt": "#EEF2F1",
        "border": "#D5DCDB",
        "primary": "#4A7C59",
        "primary_hover": "#3E6A4A",
        "primary_soft": "#E3EFE6",
        "text": "#1A1F22",
        "muted": "#6B7A76",
        "success": "#5C8D6B",
        "warning": "#B8860B",
        "danger": "#C0504D",
        "danger_hover": "#A43E3C",
    },
    "ocean": {
        "label": "Laut Dalam",
        "background": "#0A192F",
        "surface": "#112240",
        "surface_alt": "#1E3A5F",
        "border": "#2C5282",
        "primary": "#2DD4BF",
        "primary_hover": "#14B8A6",
        "primary_soft": "#1E4A6B",
        "text": "#E6F7FF",
        "muted": "#A8B2C1",
        "success": "#4FD1C5",
        "warning": "#FFAB00",
        "danger": "#FF6B6B",
        "danger_hover": "#E55555",
    },
    "sunset": {
        "label": "Matahari Terbenam",
        "background": "#2D1B2E",
        "surface": "#3A243D",
        "surface_alt": "#4A2E4F",
        "border": "#5A3A5F",
        "primary": "#F472B6",
        "primary_hover": "#EC4899",
        "primary_soft": "#5A2E4F",
        "text": "#FFF0F3",
        "muted": "#D8B4C1",
        "success": "#B5EAD7",
        "warning": "#FFD7BA",
        "danger": "#FF6B6B",
        "danger_hover": "#E55555",
    },
    "forest": {
        "label": "Hutan Hijau",
        "background": "#1B2620",
        "surface": "#26382E",
        "surface_alt": "#324A3D",
        "border": "#4A6050",
        "primary": "#4A9E6E",
        "primary_hover": "#3E825C",
        "primary_soft": "#2E4A3E",
        "text": "#E8F5E9",
        "muted": "#A5C9A5",
        "success": "#66BB6A",
        "warning": "#FFCA28",
        "danger": "#EF5350",
        "danger_hover": "#E53935",
    },
    "midnight": {
        "label": "Malam Kosmik",
        "background": "#0F0C29",
        "surface": "#1A182E",
        "surface_alt": "#241F3E",
        "border": "#3E3A5E",
        "primary": "#B388FF",
        "primary_hover": "#9A6BFF",
        "primary_soft": "#3A2E5E",
        "text": "#E3E0FF",
        "muted": "#B8B4D0",
        "success": "#81C784",
        "warning": "#FFD54F",
        "danger": "#E57373",
        "danger_hover": "#D32F2F",
    },
    "cyberpunk": {
        "label": "Cyberpunk Neon",
        "background": "#050505",
        "surface": "#0A0A0A",
        "surface_alt": "#141414",
        "border": "#3300FF",
        "primary": "#00FFFF",
        "primary_hover": "#00E6E6",
        "primary_soft": "#003333",
        "text": "#E0E0E0",
        "muted": "#888888",
        "accent": "#FF00FF",
        "accent_hover": "#CC00CC",
        "success": "#00FF00",
        "warning": "#FFFF00",
        "danger": "#FF0040",
        "danger_hover": "#CC0033",
    },
}

DEFAULT_THEME = "dark"

# Kompatibilitas dengan kode lama yang mengimpor COLORS
COLORS = THEMES[DEFAULT_THEME].copy()


def get_theme(name=None):
    """Ambil kamus warna sesuai nama tema. Jika tidak ditemukan, gunakan default."""
    if name is None:
        name = DEFAULT_THEME
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def set_theme(name):
    """Ganti tema warna aktif dan perbarui COLORS secara global.

    Memutasi dictionary COLORS yang sama agar semua modul yang sudah
    mengimpor COLORS langsung melihat perubahan tanpa perlu impor ulang.

    Returns kamus warna tema baru.
    """
    new_colors = THEMES.get(name, THEMES[DEFAULT_THEME]).copy()
    COLORS.clear()
    COLORS.update(new_colors)
    mode = "light" if name == "light" else "dark"
    ctk.set_appearance_mode(mode)
    return COLORS


def apply_theme(name=None):
    """Set mode tampilan CustomTkinter (kompatibel dengan kode lama).

    Jika name diberikan, juga memperbarui COLORS ke tema tersebut.
    """
    theme = get_theme(name)
    mode = "light" if (name == "light") else "dark"
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme("blue")
    COLORS.clear()
    COLORS.update(theme)
