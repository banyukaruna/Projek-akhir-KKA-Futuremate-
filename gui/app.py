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
            self._tugas_page()
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

        title_entry = ctk.CTkEntry(
            form, placeholder_text="Nama tugas atau kegiatan", height=38
        )
        title_entry.grid(row=0, column=0, padx=(16, 8), pady=(16, 8), sticky="ew")

        subject_entry = ctk.CTkEntry(
            form, placeholder_text="Mata pelajaran", height=38
        )
        subject_entry.grid(row=0, column=1, padx=(8, 16), pady=(16, 8), sticky="ew")

        date_entry = ctk.CTkEntry(
            form, placeholder_text="Tenggat: YYYY-MM-DD", height=38
        )
        date_entry.insert(0, date.today().isoformat())
        date_entry.grid(row=1, column=0, padx=(16, 8), pady=8, sticky="ew")

        type_menu = ctk.CTkOptionMenu(
            form, values=["Tugas", "Ujian", "Sesi Belajar"],
            fg_color=COLORS["surface_alt"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"], text_color=COLORS["text"]
        )
        type_menu.grid(row=1, column=1, padx=(8, 16), pady=8, sticky="ew")

        difficulty_menu = ctk.CTkOptionMenu(
            form, values=["1", "2", "3", "4", "5"],
            fg_color=COLORS["surface_alt"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"], text_color=COLORS["text"]
        )
        difficulty_menu.set("3")
        difficulty_menu.grid(row=2, column=0, padx=(16, 8), pady=(8, 4), sticky="ew")

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
                        text_color="#071923",
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
            text_color="#071923"
        ).grid(row=2, column=1, padx=(8, 16), pady=(8, 4), sticky="ew")

        ctk.CTkLabel(
            form,
            text="Tingkat kesulitan berlaku untuk jenis Tugas. Gunakan tanggal YYYY-MM-DD.",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=10)
        ).grid(row=3, column=0, columnspan=2, padx=16, pady=(4, 14), sticky="w")

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
        ctk.CTkLabel(panel, text="Pilih hari dan jam luang. Sesi disusun berdasarkan deadline.",
                     text_color=COLORS["muted"], font=ctk.CTkFont(size=10)).pack(anchor="w", padx=18, pady=(0, 10))

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
                          fg_color=COLORS["primary"], text_color="#071923").pack(pady=12)

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

        ctk.CTkButton(panel, text="Buat ulang jadwal otomatis", command=generate_schedule,
                      height=36, fg_color=COLORS["primary"],
                      hover_color=COLORS["primary_hover"], text_color="#071923").pack(
                          fill="x", padx=14, pady=(0, 12))
        refresh_schedule()

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
