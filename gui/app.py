"""Entry point GUI FutureMate. Jalankan dengan: python -m gui.app"""
from pathlib import Path
import customtkinter as ctk

from gui.theme import COLORS, apply_theme
from gui.components.sidebar import Sidebar
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

        # Ukuran jendela mengikuti resolusi layar agar tidak langsung terpotong.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = min(1180, max(760, int(screen_width * 0.90)))
        window_height = min(800, max(560, int(screen_height * 0.84)))
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(min(760, screen_width), min(560, screen_height))
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
                      fg_color=COLORS["primary"], text_color=COLORS["text"]).pack()

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
                      text_color=COLORS["text"], font=ctk.CTkFont(size=14, weight="bold"),
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
        # Area konten dibuat scrollable agar halaman panjang tetap bisa diakses
        # pada layar laptop yang lebih kecil.
        self.content = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["background"], corner_radius=0
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=14, pady=12)
        self.content.grid_columnconfigure(0, weight=1)
        self.show_page("Dashboard")

    def _page_header(self, title, subtitle):
        ctk.CTkLabel(self.content, text=title, font=ctk.CTkFont(size=27, weight="bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.content, text=subtitle, font=ctk.CTkFont(size=12),
                     text_color=COLORS["muted"]).grid(row=1, column=0, sticky="w", pady=(5, 22))

    def _card(self, parent, title, value, note, color=None):
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"]
        )
        accent = ctk.CTkFrame(
            card, width=4, corner_radius=3,
            fg_color=color or COLORS["success"]
        )
        accent.pack(side="left", fill="y", padx=(0, 12), pady=13)

        details = ctk.CTkFrame(card, fg_color="transparent")
        details.pack(side="left", fill="both", expand=True, pady=13, padx=(0, 12))
        ctk.CTkLabel(
            details, text=title, text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            details, text=value, text_color=COLORS["text"],
            font=ctk.CTkFont(size=25, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            details, text=note, text_color=COLORS["muted"],
            font=ctk.CTkFont(size=10), wraplength=220, justify="left"
        ).pack(anchor="w", pady=(3, 0))
        return card

    def show_page(self, page):
        self.current_page = page
        self.sidebar.set_active(page)
        for child in self.content.winfo_children():
            child.destroy()
        pages = {
            "Dashboard": self._dashboard,
            "Tugas & Jadwal": self._tugas_page,
            "Nilai Akademik": self._nilai_page,
            "Target Masa Depan": self._target_page,
            "Tes Minat": self._tes_minat_page,
            "Portofolio": self._portofolio_page,
        }
        pages.get(page, self._dashboard)()

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
                   self.kesiapan.kategori(result["total"]), COLORS["success"]).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._card(cards, "Tugas aktif", str(len(active)),
                   "Item yang belum selesai").grid(row=0, column=1, sticky="ew", padx=8)
        self._card(cards, "Rata-rata nilai", f"{avg:.1f}",
                   "Belum ada nilai" if not murid.nilai.daftar_mapel() else "Dari seluruh mata pelajaran").grid(row=0, column=2, sticky="ew", padx=(8, 0))

        guide = ctk.CTkFrame(
            self.content, fg_color=COLORS["surface_alt"],
            corner_radius=12, border_width=1, border_color=COLORS["border"]
        )
        guide.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        ctk.CTkLabel(
            guide, text="Cara membaca dashboard",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(
            guide,
            text=("Skor kesiapan merangkum nilai akademik (30 poin), ketepatan tugas (25), "
                  "portofolio (20), dan kecocokan target (25). Tugas aktif menunjukkan "
                  "kegiatan yang belum selesai. Rata-rata nilai dihitung dari nilai yang "
                  "sudah kamu masukkan."),
            text_color=COLORS["muted"], justify="left", wraplength=820,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=16, pady=(0, 12))

        lower = ctk.CTkFrame(self.content, fg_color="transparent")
        lower.grid(row=4, column=0, sticky="nsew", pady=(18, 0))
        lower.grid_columnconfigure((0, 1), weight=1)
        lower.grid_rowconfigure(0, weight=1)

        progress = ctk.CTkFrame(
            lower, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"]
        )
        progress.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        ctk.CTkLabel(progress, text="Komponen kesiapan", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(18, 4))
        ctk.CTkLabel(
            progress, text="Setiap bar menunjukkan kontribusi komponen terhadap skor maksimalnya.",
            text_color=COLORS["muted"], wraplength=380, justify="left",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=18, pady=(0, 8))
        for label, score in result["komponen"].items():
            line = ctk.CTkFrame(progress, fg_color="transparent")
            line.pack(fill="x", padx=18, pady=7)
            ctk.CTkLabel(line, text=label, text_color=COLORS["muted"]).pack(side="left")
            ctk.CTkLabel(line, text=f"{score:g}/{self.kesiapan.BOBOT[label]}",
                         text_color=COLORS["text"]).pack(side="right")
            bar = ctk.CTkProgressBar(progress, height=7, progress_color=COLORS["primary"])
            bar.pack(fill="x", padx=18, pady=(0, 5))
            bar.set(score / self.kesiapan.BOBOT[label] if self.kesiapan.BOBOT[label] else 0)

        right = ctk.CTkFrame(
            lower, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"]
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(9, 0))
        ctk.CTkLabel(right, text="Prioritas terdekat", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(18, 4))
        ctk.CTkLabel(
            right, text="Daftar ini membantu kamu melihat kegiatan aktif dengan tenggat terdekat.",
            text_color=COLORS["muted"], wraplength=360, justify="left",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=18, pady=(0, 8))
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

        roadmap = ctk.CTkFrame(
            self.content, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"]
        )
        roadmap.grid(row=5, column=0, sticky="ew", pady=(18, 0))
        ctk.CTkLabel(roadmap, text="Saran langkah berikutnya",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(16, 8))
        for suggestion in self.kesiapan.roadmap(murid)[:3]:
            ctk.CTkLabel(roadmap, text=f"•  {suggestion}", text_color=COLORS["muted"],
                         anchor="w", justify="left", wraplength=780).pack(fill="x", padx=18, pady=4)
        ctk.CTkLabel(roadmap, text=f"{targets} target masa depan tersimpan",
                     text_color=COLORS["primary"], font=ctk.CTkFont(size=11, weight="bold")
                     ).pack(anchor="w", padx=18, pady=(10, 15))


    # ==========================================================
    # HALAMAN TUGAS & JADWAL
    # Seluruh kode halaman ini sengaja digabung di gui/app.py.
    # ==========================================================

    def _tugas_page(self):
        from datetime import date
        from models.item import Tugas, Ujian, SesiBelajar

        self.content.grid_rowconfigure(3, weight=1)
        self._page_header(
            "Tugas & Jadwal",
            "Catat tugas, ujian, dan sesi belajar agar tenggat waktumu terpantau."
        )

        form = ctk.CTkFrame(self.content, fg_color=COLORS["surface"], corner_radius=14)
        form.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        form.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(
            form, text="Tambah kegiatan. Isi nama, mata pelajaran, tenggat, dan jenis kegiatan.",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=11)
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(12, 0), sticky="w")

        title_entry = ctk.CTkEntry(
            form, placeholder_text="Nama tugas atau kegiatan", height=38
        )
        title_entry.grid(row=1, column=0, padx=(16, 8), pady=(10, 8), sticky="ew")

        subject_entry = ctk.CTkEntry(
            form, placeholder_text="Mata pelajaran", height=38
        )
        subject_entry.grid(row=1, column=1, padx=(8, 16), pady=(10, 8), sticky="ew")

        date_entry = ctk.CTkEntry(
            form, placeholder_text="Tenggat: YYYY-MM-DD", height=38
        )
        date_entry.insert(0, date.today().isoformat())
        date_entry.grid(row=2, column=0, padx=(16, 8), pady=8, sticky="ew")

        type_menu = ctk.CTkOptionMenu(
            form, values=["Tugas", "Ujian", "Sesi Belajar"],
            fg_color=COLORS["surface_alt"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"], text_color=COLORS["text"]
        )
        type_menu.grid(row=2, column=1, padx=(8, 16), pady=8, sticky="ew")

        difficulty_menu = ctk.CTkOptionMenu(
            form, values=["1", "2", "3", "4", "5"],
            fg_color=COLORS["surface_alt"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"], text_color=COLORS["text"]
        )
        difficulty_menu.set("3")
        difficulty_menu.grid(row=3, column=0, padx=(16, 8), pady=(8, 4), sticky="ew")

        list_panel = ctk.CTkFrame(self.content, fg_color=COLORS["surface"], corner_radius=14)
        list_panel.grid(row=3, column=0, sticky="nsew")
        list_panel.grid_columnconfigure(0, weight=1)
        list_panel.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(list_panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(15, 8))
        ctk.CTkLabel(
            header, text="Daftar kegiatan",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        count_label = ctk.CTkLabel(header, text="", text_color=COLORS["muted"])
        count_label.pack(side="right")

        items_frame = ctk.CTkScrollableFrame(
            list_panel, fg_color="transparent", corner_radius=0
        )
        items_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        def show_message(message):
            self._message("FutureMate", message)

        def refresh_list():
            for child in items_frame.winfo_children():
                child.destroy()

            active = self.current_student.item_aktif()
            completed = [item for item in self.current_student.items if item.selesai]
            count_label.configure(
                text=f"{len(active)} aktif · {len(completed)} selesai"
            )

            if not self.current_student.items:
                ctk.CTkLabel(
                    items_frame,
                    text="Belum ada kegiatan. Tambahkan melalui formulir di atas.",
                    text_color=COLORS["muted"]
                ).pack(anchor="w", padx=8, pady=12)
                return

            for item in active + completed:
                row = ctk.CTkFrame(
                    items_frame, fg_color=COLORS["surface_alt"], corner_radius=10
                )
                row.pack(fill="x", padx=4, pady=5)

                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="both", expand=True, padx=12, pady=9)

                status = "Selesai" if item.selesai else item.prioritas().value
                ctk.CTkLabel(
                    info, text=f"{item.judul}  ·  {item.jenis()}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["text"]
                ).pack(anchor="w")
                ctk.CTkLabel(
                    info,
                    text=f"{item.mapel}  |  Tenggat {item.deadline:%d-%m-%Y}  |  {status}",
                    text_color=COLORS["muted"], font=ctk.CTkFont(size=10)
                ).pack(anchor="w", pady=(3, 0))

                actions = ctk.CTkFrame(row, fg_color="transparent")
                actions.pack(side="right", padx=8)

                if not item.selesai:
                    ctk.CTkButton(
                        actions, text="Selesai", width=72, height=30,
                        fg_color=COLORS["primary"],
                        hover_color=COLORS["primary_hover"],
                        text_color=COLORS["text"],
                        command=lambda current=item: complete_item(current)
                    ).pack(side="left", padx=3)

                ctk.CTkButton(
                    actions, text="Hapus", width=62, height=30,
                    fg_color=COLORS["danger"], hover_color="#c95d5d",
                    command=lambda current=item: delete_item(current)
                ).pack(side="left", padx=3)

        def complete_item(item):
            item.tandai_selesai()
            self._save()
            refresh_list()

        def delete_item(item):
            self.current_student.items.remove(item)
            self._save()
            refresh_list()

        def add_item():
            title = title_entry.get().strip()
            subject = subject_entry.get().strip()
            raw_date = date_entry.get().strip()

            if not title or not subject or not raw_date:
                show_message(
                    "Nama kegiatan, mata pelajaran, dan tenggat wajib diisi."
                )
                return

            try:
                deadline = date.fromisoformat(raw_date)
                kind = type_menu.get()

                if kind == "Tugas":
                    item = Tugas(
                        title, subject, deadline, int(difficulty_menu.get())
                    )
                elif kind == "Ujian":
                    item = Ujian(title, subject, deadline)
                else:
                    item = SesiBelajar(title, subject, deadline)

                self.current_student.tambah_item(item)
                self._save()
                title_entry.delete(0, "end")
                subject_entry.delete(0, "end")
                refresh_list()
            except ValueError:
                show_message(
                    "Tanggal harus menggunakan format YYYY-MM-DD, "
                    "misalnya 2026-11-20."
                )

        ctk.CTkButton(
            form, text="Tambah kegiatan", height=38, command=add_item,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"]
        ).grid(row=3, column=1, padx=(8, 16), pady=(8, 4), sticky="ew")

        ctk.CTkLabel(
            form,
            text="Tingkat kesulitan berlaku untuk jenis Tugas. Gunakan tanggal YYYY-MM-DD.",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=10)
        ).grid(row=4, column=0, columnspan=2, padx=16, pady=(4, 14), sticky="w")

        refresh_list()
        self._jadwal_panel()

    def _jadwal_panel(self):
        from datetime import date, datetime
        from services.penjadwalan import Penjadwalan

        panel = ctk.CTkFrame(self.content, fg_color=COLORS["surface"], corner_radius=14)
        panel.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(panel, text="Jadwal belajar otomatis",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(
            panel,
            text=("Pilih hari dan rentang waktu yang biasanya kamu punya. Sistem menyusun "
                  "sesi 60 menit untuk kegiatan aktif berdasarkan tenggat dan prioritas."),
            text_color=COLORS["muted"], font=ctk.CTkFont(size=10),
            wraplength=820, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 8))
        ctk.CTkLabel(
            panel,
            text="Jadwal dibuat untuk 30 hari ke depan. Setiap sesi berjarak 75 menit, termasuk jeda 15 menit.",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=10),
            wraplength=820, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 10))

        pref = self.current_student.preferensi_jadwal
        days_frame = ctk.CTkFrame(panel, fg_color="transparent")
        days_frame.pack(fill="x", padx=14)
        day_vars = []
        for index, day in enumerate(Penjadwalan.HARI):
            var = ctk.BooleanVar(value=index in pref.get("hari", []))
            day_vars.append(var)
            ctk.CTkCheckBox(days_frame, text=day[:3], variable=var,
                            text_color=COLORS["text"], checkbox_width=16,
                            checkbox_height=16).pack(side="left", padx=5, pady=5)

        time_frame = ctk.CTkFrame(panel, fg_color="transparent")
        time_frame.pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(time_frame, text="Mulai", text_color=COLORS["muted"]).pack(side="left")
        start_entry = ctk.CTkEntry(time_frame, width=85, height=32)
        start_entry.insert(0, pref.get("mulai", "16:00"))
        start_entry.pack(side="left", padx=(7, 16))
        ctk.CTkLabel(time_frame, text="Selesai", text_color=COLORS["muted"]).pack(side="left")
        end_entry = ctk.CTkEntry(time_frame, width=85, height=32)
        end_entry.insert(0, pref.get("selesai", "18:00"))
        end_entry.pack(side="left", padx=7)

        schedule_frame = ctk.CTkScrollableFrame(panel, fg_color=COLORS["surface_alt"],
                                                height=190, corner_radius=10)
        schedule_frame.pack(fill="x", padx=14, pady=(4, 12))

        def refresh_schedule():
            for child in schedule_frame.winfo_children():
                child.destroy()
            sessions = sorted(self.current_student.jadwal,
                              key=lambda s: (s["tanggal"], s["mulai"]))
            if not sessions:
                ctk.CTkLabel(schedule_frame, text="Belum ada jadwal. Tekan tombol Buat Jadwal.",
                             text_color=COLORS["muted"]).pack(anchor="w", padx=8, pady=10)
                return
            for index, session in enumerate(sessions):
                row = ctk.CTkFrame(schedule_frame, fg_color=COLORS["surface"], corner_radius=8)
                row.pack(fill="x", padx=4, pady=4)
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=9, pady=7)
                tanggal_obj = date.fromisoformat(session["tanggal"])
                ctk.CTkLabel(info, text=f'{session["judul"]} · {session["mapel"]}',
                             text_color=COLORS["text"],
                             font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
                ctk.CTkLabel(info,
                             text=f'{Penjadwalan.HARI[tanggal_obj.weekday()]}, {tanggal_obj:%d-%m-%Y} · {session["mulai"]} · {session["durasi"]} menit',
                             text_color=COLORS["muted"], font=ctk.CTkFont(size=10)).pack(anchor="w")
                ctk.CTkButton(row, text="Edit", width=58, height=28,
                              command=lambda i=index: edit_session(i)).pack(side="right", padx=8)

        def edit_session(index):
            session = self.current_student.jadwal[index]
            dialog = ctk.CTkToplevel(self)
            dialog.title("Edit sesi belajar")
            dialog.geometry("340x250")
            dialog.transient(self)
            dialog.grab_set()
            ctk.CTkLabel(dialog, text=session["judul"], text_color=COLORS["text"]).pack(pady=(16, 8))
            date_input = ctk.CTkEntry(dialog, placeholder_text="Tanggal YYYY-MM-DD")
            date_input.insert(0, session["tanggal"])
            date_input.pack(fill="x", padx=22, pady=5)
            time_input = ctk.CTkEntry(dialog, placeholder_text="Jam HH:MM")
            time_input.insert(0, session["mulai"])
            time_input.pack(fill="x", padx=22, pady=5)
            duration_input = ctk.CTkEntry(dialog, placeholder_text="Durasi menit")
            duration_input.insert(0, str(session["durasi"]))
            duration_input.pack(fill="x", padx=22, pady=5)

            def save_edit():
                try:
                    Penjadwalan.ubah_sesi(session, date_input.get().strip(),
                                          time_input.get().strip(), duration_input.get().strip())
                    self._save()
                    dialog.destroy()
                    refresh_schedule()
                except ValueError as error:
                    self._message("Jadwal tidak valid", str(error))

            ctk.CTkButton(dialog, text="Simpan perubahan", command=save_edit,
                          fg_color=COLORS["primary"], text_color=COLORS["text"]).pack(pady=12)

        def generate_schedule():
            try:
                selected_days = [i for i, var in enumerate(day_vars) if var.get()]
                start, end = start_entry.get().strip(), end_entry.get().strip()
                datetime.strptime(start, "%H:%M")
                datetime.strptime(end, "%H:%M")
                self.current_student.preferensi_jadwal = {
                    "hari": selected_days, "mulai": start, "selesai": end
                }
                self.current_student.jadwal = Penjadwalan.buat_jadwal(
                    self.current_student.item_aktif(), selected_days, start, end
                )
                self._save()
                refresh_schedule()
                if not self.current_student.jadwal:
                    self._message("Jadwal belum terbentuk",
                                  "Tidak ada slot yang cocok. Periksa deadline dan waktu luangmu.")
            except ValueError as error:
                self._message("Pengaturan tidak valid", str(error))

        ctk.CTkLabel(
            panel,
            text="Kamu bisa mengubah tanggal, jam, dan durasi lewat tombol Edit. Membuat ulang jadwal akan mengganti jadwal yang tersimpan saat ini.",
            text_color=COLORS["warning"], font=ctk.CTkFont(size=10),
            wraplength=820, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 8))
        ctk.CTkButton(panel, text="Buat ulang jadwal otomatis", command=generate_schedule,
                      height=36, fg_color=COLORS["primary"],
                      hover_color=COLORS["primary_hover"], text_color=COLORS["text"]).pack(
                          fill="x", padx=14, pady=(0, 12))
        refresh_schedule()

    def _section_card(self, parent, title, description):
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"]
        )
        row_index = len(parent.winfo_children())
        card.grid(row=row_index, column=0, sticky="ew", pady=(0, 14))
        parent.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=18, pady=(16, 3))
        ctk.CTkLabel(
            card, text=description, text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11), wraplength=820, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 12))
        return card

    def _nilai_page(self):
        from models.nilai import NilaiTidakValidError
        self._page_header(
            "Nilai Akademik",
            "Catat hasil belajarmu dan pantau perkembangan setiap mata pelajaran."
        )
        form = self._section_card(
            self.content, "Tambah nilai",
            "Masukkan mata pelajaran dan nilai yang kamu peroleh. Nilai harus berada pada rentang 0 sampai 100."
        )
        fields = ctk.CTkFrame(form, fg_color="transparent")
        fields.pack(fill="x", padx=18, pady=(0, 12))
        fields.grid_columnconfigure((0, 1), weight=1)
        subject = ctk.CTkEntry(fields, placeholder_text="Contoh: Matematika", height=38)
        subject.grid(row=0, column=0, padx=(0, 7), sticky="ew")
        score = ctk.CTkEntry(fields, placeholder_text="Nilai, contoh: 88", height=38)
        score.grid(row=0, column=1, padx=(7, 0), sticky="ew")
        message = ctk.CTkLabel(form, text="", text_color=COLORS["danger"])
        message.pack(anchor="w", padx=18)

        summary = ctk.CTkFrame(self.content, fg_color="transparent")
        summary.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        summary.grid_columnconfigure((0, 1), weight=1)
        avg_card = self._card(summary, "Rata-rata keseluruhan", "0.0", "Rata-rata dari seluruh mapel")
        avg_card.grid(row=0, column=0, sticky="ew", padx=(0, 7))
        count_card = self._card(summary, "Mata pelajaran", "0", "Jumlah mapel yang memiliki nilai")
        count_card.grid(row=0, column=1, sticky="ew", padx=(7, 0))

        history = self._section_card(
            self.content, "Riwayat nilai",
            "Tren membandingkan nilai terbaru dengan rata-rata nilai sebelumnya pada mapel yang sama."
        )
        rows = ctk.CTkFrame(history, fg_color="transparent")
        rows.pack(fill="x", padx=18, pady=(0, 14))

        def refresh():
            for child in rows.winfo_children():
                child.destroy()
            murid = self.current_student
            avg = murid.nilai.rata_rata()
            avg_card.winfo_children()[1].winfo_children()[1].configure(text=f"{avg:.1f}")
            count_card.winfo_children()[1].winfo_children()[1].configure(text=str(len(murid.nilai.daftar_mapel())))
            if not murid.nilai.daftar_mapel():
                ctk.CTkLabel(rows, text="Belum ada nilai. Tambahkan nilai pertamamu di atas.",
                             text_color=COLORS["muted"]).pack(anchor="w", pady=8)
                return
            for mapel in murid.nilai.daftar_mapel():
                line = ctk.CTkFrame(rows, fg_color=COLORS["surface_alt"], corner_radius=9)
                line.pack(fill="x", pady=4)
                vals = murid.nilai.to_dict().get(mapel, [])
                trend = murid.nilai.tren(mapel)
                ctk.CTkLabel(line, text=mapel, text_color=COLORS["text"],
                             font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=12, pady=10)
                ctk.CTkLabel(line, text=f"{murid.nilai.rata_mapel(mapel):.1f}  ·  {len(vals)} data  ·  Tren {trend}",
                             text_color=COLORS["muted"], font=ctk.CTkFont(size=10)).pack(side="right", padx=12)

        def add_score():
            try:
                mapel = subject.get().strip()
                if not mapel:
                    raise ValueError("Nama mata pelajaran wajib diisi.")
                value = float(score.get().strip().replace(",", "."))
                self.current_student.nilai.tambah(mapel, value)
                self._save()
                subject.delete(0, "end")
                score.delete(0, "end")
                message.configure(text="")
                refresh()
            except ValueError as error:
                message.configure(text=str(error) if str(error) else "Masukkan nilai angka yang valid.")
            except Exception as error:
                message.configure(text=str(error))

        ctk.CTkButton(form, text="Simpan nilai", command=add_score, height=36,
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                      text_color=COLORS["text"]).pack(anchor="e", padx=18, pady=(0, 14))
        refresh()

    def _target_page(self):
        from datetime import date
        from models.target import Jurusan, Beasiswa, Lomba
        self._page_header(
            "Target Masa Depan",
            "Simpan tujuan pendidikan dan peluang yang ingin kamu persiapkan."
        )
        form = self._section_card(
            self.content, "Tambah target",
            "Pilih jenis target. Untuk jurusan, pilih dari katalog. Untuk beasiswa dan lomba, isi syarat sesuai informasi resmi yang kamu miliki."
        )
        grid = ctk.CTkFrame(form, fg_color="transparent")
        grid.pack(fill="x", padx=18, pady=(0, 10))
        grid.grid_columnconfigure((0, 1), weight=1)
        kind = ctk.CTkOptionMenu(
            grid, values=["Jurusan", "Beasiswa", "Lomba"],
            fg_color=COLORS["surface_alt"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"], text_color=COLORS["text"]
        )
        kind.grid(row=0, column=0, padx=(0, 7), pady=4, sticky="ew")
        catalog_names = [f"{j.nama_jurusan} | {j.kampus}" for j in self.katalog]
        catalog = ctk.CTkOptionMenu(
            grid, values=catalog_names or ["Katalog kosong"],
            fg_color=COLORS["surface_alt"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"], text_color=COLORS["text"]
        )
        catalog.grid(row=0, column=1, padx=(7, 0), pady=4, sticky="ew")
        name = ctk.CTkEntry(grid, placeholder_text="Nama beasiswa atau lomba")
        name.grid(row=1, column=0, padx=(0, 7), pady=4, sticky="ew")
        deadline = ctk.CTkEntry(grid, placeholder_text="Deadline YYYY-MM-DD (opsional)")
        deadline.grid(row=1, column=1, padx=(7, 0), pady=4, sticky="ew")
        average = ctk.CTkEntry(grid, placeholder_text="Rata-rata minimum, contoh 80")
        average.grid(row=2, column=0, padx=(0, 7), pady=4, sticky="ew")
        extra = ctk.CTkEntry(grid, placeholder_text="Prestasi minimum / mata pelajaran")
        extra.grid(row=2, column=1, padx=(7, 0), pady=4, sticky="ew")
        extra_value = ctk.CTkEntry(grid, placeholder_text="Nilai minimum mapel (khusus lomba)")
        extra_value.grid(row=3, column=0, padx=(0, 7), pady=4, sticky="ew")
        hint = ctk.CTkLabel(form, text="Jurusan menggunakan syarat yang tersedia di katalog.",
                            text_color=COLORS["muted"], font=ctk.CTkFont(size=10))
        hint.pack(anchor="w", padx=18, pady=(0, 8))
        result_area = ctk.CTkFrame(self.content, fg_color="transparent")
        result_area.grid(row=3, column=0, sticky="ew")
        result_area.grid_columnconfigure(0, weight=1)

        def refresh():
            for child in result_area.winfo_children():
                child.destroy()
            if not self.current_student.targets:
                ctk.CTkLabel(result_area, text="Belum ada target tersimpan.",
                             text_color=COLORS["muted"]).pack(anchor="w", pady=8)
            for target in self.current_student.targets:
                card = ctk.CTkFrame(result_area, fg_color=COLORS["surface"],
                                    corner_radius=12, border_width=1, border_color=COLORS["border"])
                card.pack(fill="x", pady=5)
                fraction = target.kecocokan(self.current_student) * 100
                ctk.CTkLabel(card, text=f"{target.jenis()} · {target.nama}",
                             text_color=COLORS["text"], font=ctk.CTkFont(size=13, weight="bold")
                             ).pack(anchor="w", padx=15, pady=(12, 3))
                ctk.CTkLabel(card, text=f"Kecocokan syarat: {fraction:.0f}%",
                             text_color=COLORS["primary"], font=ctk.CTkFont(size=11, weight="bold")
                             ).pack(anchor="w", padx=15, pady=(0, 5))
                for requirement in target.cek_syarat(self.current_student):
                    mark = "Terpenuhi" if requirement.terpenuhi else "Belum terpenuhi"
                    ctk.CTkLabel(card, text=f"• {requirement.deskripsi} · {mark}",
                                 text_color=COLORS["muted"], wraplength=780, justify="left"
                                 ).pack(anchor="w", padx=18, pady=2)
                ctk.CTkButton(card, text="Hapus target", width=100, height=28,
                              fg_color=COLORS["danger"],
                              command=lambda t=target: remove(t)).pack(anchor="e", padx=12, pady=10)

        def remove(target):
            self.current_student.targets.remove(target)
            self._save()
            refresh()

        def add_target():
            try:
                selected = kind.get()
                if selected == "Jurusan":
                    if not self.katalog:
                        raise ValueError("Katalog jurusan belum tersedia.")
                    chosen = catalog.get()
                    target = next(j for j in self.katalog if f"{j.nama_jurusan} | {j.kampus}" == chosen)
                    target = Jurusan(target.nama_jurusan, target.kampus, target.rata_min,
                                     target.syarat_mapel, target.riasec)
                else:
                    target_name = name.get().strip()
                    if not target_name:
                        raise ValueError("Nama target wajib diisi.")
                    raw_deadline = deadline.get().strip()
                    due = date.fromisoformat(raw_deadline) if raw_deadline else None
                    minimum = float(average.get().strip())
                    if selected == "Beasiswa":
                        target = Beasiswa(target_name, due, minimum, int(extra.get().strip()))
                    else:
                        subject_name = extra.get().strip()
                        if not subject_name:
                            raise ValueError("Isi nama mata pelajaran untuk target lomba.")
                        target = Lomba(target_name, due, subject_name, float(extra_value.get().strip()))
                self.current_student.tambah_target(target)
                self._save()
                name.delete(0, "end")
                deadline.delete(0, "end")
                average.delete(0, "end")
                extra.delete(0, "end")
                extra_value.delete(0, "end")
                refresh()
            except (ValueError, StopIteration) as error:
                self._message("Target belum tersimpan", str(error) or "Periksa kembali isian target.")

        ctk.CTkButton(form, text="Simpan target", command=add_target, height=36,
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                      text_color=COLORS["text"]).pack(anchor="e", padx=18, pady=(0, 14))
        refresh()

    def _tes_minat_page(self):
        from services.tes_minat import PERTANYAAN, NAMA_TIPE, ProfilMinat
        self._page_header(
            "Tes Minat",
            "Kenali kecenderungan minatmu melalui 12 pernyataan singkat."
        )
        intro = self._section_card(
            self.content, "Tentang tes RIASEC",
            "Pilih angka 1 sampai 5 untuk setiap pernyataan. 1 berarti sangat tidak sesuai, sedangkan 5 berarti sangat sesuai. Hasil membantu eksplorasi, bukan menentukan masa depan secara mutlak."
        )
        answers = []
        for question, _ in PERTANYAAN:
            block = ctk.CTkFrame(intro, fg_color=COLORS["surface_alt"], corner_radius=9)
            block.pack(fill="x", padx=18, pady=4)
            ctk.CTkLabel(block, text=question, text_color=COLORS["text"],
                         wraplength=760, justify="left").pack(anchor="w", padx=12, pady=(9, 3))
            choice = ctk.CTkSegmentedButton(
                block, values=["1", "2", "3", "4", "5"],
                selected_color=COLORS["primary"], selected_hover_color=COLORS["primary_hover"],
                unselected_color=COLORS["surface"], text_color=COLORS["text"]
            )
            choice.set("3")
            choice.pack(anchor="e", padx=10, pady=(0, 8))
            answers.append(choice)

        result_card = self._section_card(
            self.content, "Hasil tes dan rekomendasi",
            "Setelah mengirim jawaban, kamu akan melihat tiga minat teratas dan jurusan yang paling sesuai dengan profilmu."
        )
        result_body = ctk.CTkFrame(result_card, fg_color="transparent")
        result_body.pack(fill="x", padx=18, pady=(0, 14))

        def render_saved():
            for child in result_body.winfo_children():
                child.destroy()
            profile = self.current_student.profil_minat
            if not profile:
                ctk.CTkLabel(result_body, text="Kamu belum mengisi tes minat.",
                             text_color=COLORS["muted"]).pack(anchor="w")
                return
            top = ProfilMinat.tipe_teratas(profile)
            ctk.CTkLabel(result_body, text="Minat dominan: " + " · ".join(
                f"{t} ({NAMA_TIPE[t]})" for t in top),
                text_color=COLORS["text"], wraplength=780, justify="left"
            ).pack(anchor="w", pady=5)
            for jurusan, match in ProfilMinat.rekomendasikan(profile, self.katalog, 5):
                ctk.CTkLabel(result_body, text=f"{jurusan.nama_jurusan} · {jurusan.kampus} · kecocokan minat {match:.0f}%",
                             text_color=COLORS["muted"], wraplength=780, justify="left"
                             ).pack(anchor="w", pady=3)

        def submit():
            profile = ProfilMinat.hitung([int(choice.get()) for choice in answers])
            self.current_student.profil_minat = profile
            self._save()
            render_saved()

        ctk.CTkButton(intro, text="Hitung hasil tes", command=submit, height=38,
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                      text_color=COLORS["text"]).pack(anchor="e", padx=18, pady=14)
        render_saved()

    def _portofolio_page(self):
        from models.portofolio import Prestasi
        self._page_header(
            "Portofolio",
            "Dokumentasikan prestasi dan pengalaman yang mendukung rencana masa depanmu."
        )
        form = self._section_card(
            self.content, "Tambah pencapaian",
            "Catat kegiatan, proyek, sertifikat, atau prestasi. Tingkat pencapaian menentukan poin portofolio."
        )
        grid = ctk.CTkFrame(form, fg_color="transparent")
        grid.pack(fill="x", padx=18, pady=(0, 10))
        grid.grid_columnconfigure((0, 1), weight=1)
        title = ctk.CTkEntry(grid, placeholder_text="Nama prestasi atau kegiatan", height=38)
        title.grid(row=0, column=0, padx=(0, 7), pady=4, sticky="ew")
        category = ctk.CTkEntry(grid, placeholder_text="Kategori, contoh: Akademik", height=38)
        category.grid(row=0, column=1, padx=(7, 0), pady=4, sticky="ew")
        level = ctk.CTkOptionMenu(
            grid, values=Prestasi.TINGKAT, fg_color=COLORS["surface_alt"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"]
        )
        level.grid(row=1, column=0, padx=(0, 7), pady=4, sticky="ew")
        year = ctk.CTkEntry(grid, placeholder_text="Tahun, contoh: 2026", height=38)
        year.grid(row=1, column=1, padx=(7, 0), pady=4, sticky="ew")
        summary = ctk.CTkFrame(self.content, fg_color="transparent")
        summary.pack(fill="x", pady=(0, 14))
        summary.grid_columnconfigure((0, 1), weight=1)
        points_card = self._card(summary, "Total poin", "0", "Poin berdasarkan tingkat pencapaian")
        points_card.grid(row=0, column=0, sticky="ew", padx=(0, 7))
        total_card = self._card(summary, "Jumlah pencapaian", "0", "Jumlah item portofolio")
        total_card.grid(row=0, column=1, sticky="ew", padx=(7, 0))
        listing = self._section_card(
            self.content, "Daftar portofolio",
            "Gunakan tombol hapus jika ingin menghapus catatan yang tidak lagi diperlukan."
        )
        rows = ctk.CTkFrame(listing, fg_color="transparent")
        rows.pack(fill="x", padx=18, pady=(0, 14))

        def refresh():
            for child in rows.winfo_children():
                child.destroy()
            records = self.current_student.portofolio.daftar()
            points_card.winfo_children()[1].winfo_children()[1].configure(text=str(self.current_student.portofolio.total_poin()))
            total_card.winfo_children()[1].winfo_children()[1].configure(text=str(len(records)))
            if not records:
                ctk.CTkLabel(rows, text="Belum ada pencapaian yang dicatat.",
                             text_color=COLORS["muted"]).pack(anchor="w", pady=8)
            for record in records:
                line = ctk.CTkFrame(rows, fg_color=COLORS["surface_alt"], corner_radius=9)
                line.pack(fill="x", pady=4)
                info = ctk.CTkFrame(line, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=12, pady=9)
                ctk.CTkLabel(info, text=record.judul, text_color=COLORS["text"],
                             font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
                ctk.CTkLabel(info, text=f"{record.kategori} · {record.tingkat} · {record.tahun} · {record.poin} poin",
                             text_color=COLORS["muted"], font=ctk.CTkFont(size=10)).pack(anchor="w", pady=(2, 0))
                ctk.CTkButton(line, text="Hapus", width=65, height=28,
                              fg_color=COLORS["danger"],
                              command=lambda r=record: remove(r)).pack(side="right", padx=10)

        def remove(record):
            records = self.current_student.portofolio.daftar()
            records.remove(record)
            rebuilt = type(self.current_student.portofolio)()
            for item in records:
                rebuilt.tambah(item)
            self.current_student.portofolio = rebuilt
            self._save()
            refresh()

        def add_record():
            try:
                title_value = title.get().strip()
                category_value = category.get().strip()
                if not title_value or not category_value:
                    raise ValueError("Nama pencapaian dan kategori wajib diisi.")
                year_value = int(year.get().strip())
                if year_value < 1900 or year_value > 2100:
                    raise ValueError("Tahun harus berada pada rentang 1900 sampai 2100.")
                record = Prestasi(title_value, category_value, level.get(), year_value)
                self.current_student.portofolio.tambah(record)
                self._save()
                title.delete(0, "end")
                category.delete(0, "end")
                year.delete(0, "end")
                refresh()
            except ValueError as error:
                self._message("Data belum tersimpan", str(error))

        ctk.CTkButton(form, text="Simpan pencapaian", command=add_record, height=36,
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                      text_color=COLORS["text"]).pack(anchor="e", padx=18, pady=(0, 14))
        refresh()

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
