"""Entry point GUI FutureMate. Jalankan dengan: python -m gui.app"""
from pathlib import Path
import customtkinter as ctk

from gui.theme import COLORS, apply_theme
from gui.components.sidebar import Sidebar
from gui.pages.tugas import TugasPage
from services.penyimpanan import Penyimpanan
from services.sistem_kesiapan import SistemKesiapan
from services.notifikasi import Notifikasi
from models.pengguna import Murid
from exceptions import FutureMateError

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class FutureMateApp(ctk.CTk):
    def __init__(self):
        apply_theme()
        super().__init__()
        self.title("FutureMate | Shape Your Future")
        self.geometry("1180x760")
        self.minsize(960, 640)
        self.configure(fg_color=COLORS["background"])

        self.storage = Penyimpanan(DATA / "data.json", DATA / "jurusan.json")
        self.kesiapan = SistemKesiapan()
        try:
            self.katalog = self.storage.muat_katalog()
            self.murid_data = self.storage.muat()
        except FutureMateError as error:
            self.katalog, self.murid_data = [], {}
            self.after(200, lambda: self._show_error(str(error)))

        self.current_student = None
        self.current_page = "Dashboard"
        self._show_welcome()

    def _show_error(self, message):
        self._message("Gagal memuat data", message)

    def _clear(self):
        for child in self.winfo_children():
            child.destroy()

    def _message(self, title, message):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("420x180")
        dialog.transient(self)
        ctk.CTkLabel(dialog, text=message, wraplength=360,
                     text_color=COLORS["text"]).pack(padx=24, pady=28)
        ctk.CTkButton(dialog, text="Tutup", command=dialog.destroy,
                      fg_color=COLORS["primary"], text_color="#071923").pack()

    def _show_welcome(self):
        self._clear()
        panel = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=20)
        panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.56, relheight=0.62)
        ctk.CTkLabel(panel, text="FutureMate", font=ctk.CTkFont(size=34, weight="bold"),
                     text_color=COLORS["text"]).pack(pady=(42, 5))
        ctk.CTkLabel(panel, text="Rencanakan langkahmu. Kenali potensimu.",
                     text_color=COLORS["muted"], font=ctk.CTkFont(size=14)).pack(pady=(0, 30))
        ctk.CTkLabel(panel, text="Nama murid", anchor="w",
                     text_color=COLORS["text"]).pack(fill="x", padx=54)
        self.name_entry = ctk.CTkEntry(panel, height=42, placeholder_text="Masukkan nama kamu")
        self.name_entry.pack(fill="x", padx=54, pady=(7, 16))
        ctk.CTkLabel(panel, text="Kelas (isi jika akun baru)", anchor="w",
                     text_color=COLORS["text"]).pack(fill="x", padx=54)
        self.class_entry = ctk.CTkEntry(panel, height=42, placeholder_text="Contoh: XI-2")
        self.class_entry.pack(fill="x", padx=54, pady=(7, 20))
        ctk.CTkButton(panel, text="Masuk ke FutureMate", height=44,
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                      text_color="#071923", font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._login).pack(fill="x", padx=54)
        ctk.CTkLabel(panel, text="Data tersimpan secara lokal di data/data.json",
                     text_color=COLORS["muted"], font=ctk.CTkFont(size=10)).pack(pady=18)
        self.name_entry.focus()

    def _login(self):
        name = self.name_entry.get().strip()
        kelas = self.class_entry.get().strip()
        if not name:
            self._message("Nama belum diisi", "Masukkan nama murid untuk melanjutkan.")
            return
        key = name.lower()
        if key not in self.murid_data:
            if not kelas:
                self._message("Kelas belum diisi", "Isi kelas untuk membuat akun baru.")
                return
            self.murid_data[key] = Murid(name, kelas)
        self.current_student = self.murid_data[key]
        self._save()
        self._show_main()

    def _save(self):
        if self.current_student:
            self.storage.simpan(self.murid_data)

    def _show_main(self):
        self._clear()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = Sidebar(self, self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.content = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew", padx=30, pady=26)
        self.content.grid_columnconfigure(0, weight=1)
        self.show_page("Dashboard")

    def _page_header(self, title, subtitle):
        ctk.CTkLabel(self.content, text=title, font=ctk.CTkFont(size=27, weight="bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.content, text=subtitle, font=ctk.CTkFont(size=12),
                     text_color=COLORS["muted"]).grid(row=1, column=0, sticky="w", pady=(5, 22))

    def _card(self, parent, title, value, note, color=None):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=14)
        ctk.CTkLabel(card, text=title, text_color=COLORS["muted"],
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=18, pady=(17, 5))
        ctk.CTkLabel(card, text=value, text_color=color or COLORS["text"],
                     font=ctk.CTkFont(size=27, weight="bold")).pack(anchor="w", padx=18)
        ctk.CTkLabel(card, text=note, text_color=COLORS["muted"],
                     font=ctk.CTkFont(size=10)).pack(anchor="w", padx=18, pady=(3, 16))
        return card

    def show_page(self, page):
        self.current_page = page
        self.sidebar.set_active(page)
        for child in self.content.winfo_children():
            child.destroy()
        if page == "Dashboard":
            self._dashboard()
        elif page == "Tugas & Jadwal":
            TugasPage(self.content, self.current_student, self._save, COLORS).grid(
                row=0, column=0, sticky="nsew"
            )
        else:
            self._placeholder(page)

    def _dashboard(self):
        murid = self.current_student
        result = self.kesiapan.hitung(murid)
        self._page_header("Dashboard", f"Selamat datang, {murid.nama}. Ini ringkasan progresmu.")
        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=2, column=0, sticky="ew")
        for col in range(3):
            cards.grid_columnconfigure(col, weight=1)
        active = murid.item_aktif()
        avg = murid.nilai.rata_rata()
        targets = len(murid.targets)
        self._card(cards, "Skor kesiapan", f"{result['total']}/100",
                   self.kesiapan.kategori(result["total"]), COLORS["primary"]).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._card(cards, "Tugas aktif", str(len(active)),
                   "Item yang belum selesai").grid(row=0, column=1, sticky="ew", padx=8)
        self._card(cards, "Rata-rata nilai", f"{avg:.1f}",
                   "Belum ada nilai" if not murid.nilai.daftar_mapel() else "Dari seluruh mata pelajaran").grid(row=0, column=2, sticky="ew", padx=(8, 0))

        lower = ctk.CTkFrame(self.content, fg_color="transparent")
        lower.grid(row=3, column=0, sticky="nsew", pady=(22, 0))
        lower.grid_columnconfigure((0, 1), weight=1)
        lower.grid_rowconfigure(0, weight=1)

        progress = ctk.CTkFrame(lower, fg_color=COLORS["surface"], corner_radius=14)
        progress.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        ctk.CTkLabel(progress, text="Komponen kesiapan", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(18, 12))
        for label, score in result["komponen"].items():
            line = ctk.CTkFrame(progress, fg_color="transparent")
            line.pack(fill="x", padx=18, pady=7)
            ctk.CTkLabel(line, text=label, text_color=COLORS["muted"]).pack(side="left")
            ctk.CTkLabel(line, text=f"{score:g}/{self.kesiapan.BOBOT[label]}",
                         text_color=COLORS["text"]).pack(side="right")
            bar = ctk.CTkProgressBar(progress, height=7, progress_color=COLORS["primary"])
            bar.pack(fill="x", padx=18, pady=(0, 5))
            bar.set(score / self.kesiapan.BOBOT[label] if self.kesiapan.BOBOT[label] else 0)

        right = ctk.CTkFrame(lower, fg_color=COLORS["surface"], corner_radius=14)
        right.grid(row=0, column=1, sticky="nsew", padx=(9, 0))
        ctk.CTkLabel(right, text="Prioritas terdekat", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(18, 12))
        if active:
            for item in active[:5]:
                ctk.CTkLabel(right, text=f"• {item.judul}", text_color=COLORS["text"],
                             anchor="w", wraplength=340).pack(fill="x", padx=18, pady=5)
                ctk.CTkLabel(right, text=f"{item.mapel}  ·  {item.deadline:%d %b %Y}",
                             text_color=COLORS["muted"], anchor="w",
                             font=ctk.CTkFont(size=10)).pack(fill="x", padx=31, pady=(0, 5))
        else:
            ctk.CTkLabel(right, text="Belum ada tugas aktif.",
                         text_color=COLORS["muted"]).pack(anchor="w", padx=18)

        roadmap = ctk.CTkFrame(self.content, fg_color=COLORS["surface"], corner_radius=14)
        roadmap.grid(row=4, column=0, sticky="ew", pady=(18, 0))
        ctk.CTkLabel(roadmap, text="Saran langkah berikutnya",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(16, 8))
        for suggestion in self.kesiapan.roadmap(murid)[:3]:
            ctk.CTkLabel(roadmap, text=f"•  {suggestion}", text_color=COLORS["muted"],
                         anchor="w", justify="left", wraplength=780).pack(fill="x", padx=18, pady=4)
        ctk.CTkLabel(roadmap, text=f"{targets} target masa depan tersimpan",
                     text_color=COLORS["primary"], font=ctk.CTkFont(size=11, weight="bold")
                     ).pack(anchor="w", padx=18, pady=(10, 15))

    def _placeholder(self, page):
        self._page_header(page, "Bagian ini akan dibangun pada tahap berikutnya.")
        panel = ctk.CTkFrame(self.content, fg_color=COLORS["surface"], corner_radius=14)
        panel.grid(row=2, column=0, sticky="ew")
        ctk.CTkLabel(panel, text="Halaman sedang disiapkan",
                     font=ctk.CTkFont(size=19, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=22, pady=(22, 8))
        ctk.CTkLabel(panel, text="Navigasi dan struktur halaman sudah aktif. Fitur pengelolaan data akan ditambahkan bertahap.",
                     text_color=COLORS["muted"], wraplength=700, justify="left"
                     ).pack(anchor="w", padx=22, pady=(0, 22))

    def on_closing(self):
        try:
            self._save()
        finally:
            self.destroy()


def main():
    app = FutureMateApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
