"""Entry point GUI FutureMate. Jalankan dengan: python -m gui.app"""
from pathlib import Path
import customtkinter as ctk

from gui.theme import COLORS, apply_theme
from gui.components.sidebar import Sidebar
from services.penyimpanan import Penyimpanan
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
        try:
            self.murid_data = self.storage.muat()
        except FutureMateError as error:
            self.murid_data = {}
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

    def _notify(self, message, tone="success", duration=2200):
        """Tampilkan umpan balik singkat tanpa mengganggu alur kerja."""
        if hasattr(self, "_toast") and self._toast.winfo_exists():
            self._toast.destroy()

        colors = {
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["danger"],
        }
        toast = ctk.CTkToplevel(self)
        self._toast = toast
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(fg_color=COLORS["surface_alt"])
        ctk.CTkLabel(
            toast, text=message, text_color=colors.get(tone, COLORS["text"]),
            font=ctk.CTkFont(size=12, weight="bold"),
            wraplength=340, justify="left"
        ).pack(padx=18, pady=12)
        toast.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() - toast.winfo_width() - 24
        y = self.winfo_rooty() + 24
        toast.geometry(f"+{max(8, x)}+{max(8, y)}")
        toast.after(duration, lambda: toast.destroy() if toast.winfo_exists() else None)

    def _animate_progress(self, widget, target, duration=180, steps=9):
        """Animasi progres singkat. Aman dihentikan saat widget ditutup."""
        target = max(0.0, min(1.0, float(target)))
        try:
            previous = getattr(widget, "_progress_animation_after", None)
            if previous is not None:
                widget.after_cancel(previous)
            start = float(widget.get())
        except Exception:
            start = 0.0

        state = {"step": 0}

        def advance():
            try:
                if not widget.winfo_exists():
                    return
                state["step"] += 1
                fraction = min(1.0, state["step"] / steps)
                eased = fraction * fraction * (3 - 2 * fraction)
                widget.set(start + (target - start) * eased)
                if fraction < 1.0:
                    widget._progress_animation_after = widget.after(
                        max(12, duration // steps), advance
                    )
                else:
                    widget._progress_animation_after = None
            except Exception:
                return

        advance()

    def _confirm(self, title, message):
        """Dialog konfirmasi bertema aplikasi. Mengembalikan True jika disetujui."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("430x190")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        result = {"confirmed": False}

        ctk.CTkLabel(
            dialog, text=message, text_color=COLORS["text"],
            wraplength=370, justify="left"
        ).pack(fill="both", expand=True, padx=24, pady=(22, 12))

        actions = ctk.CTkFrame(dialog, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 18))

        def close(confirmed):
            result["confirmed"] = confirmed
            dialog.destroy()

        ctk.CTkButton(
            actions, text="Batal", fg_color=COLORS["surface"],
            hover_color=COLORS["border"], text_color=COLORS["text"],
            command=lambda: close(False)
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            actions, text="Ya, lanjutkan", fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"], text_color=COLORS["text"],
            command=lambda: close(True)
        ).pack(side="right")
        self.wait_window(dialog)
        return result["confirmed"]

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
        self._notify(f"Selamat datang, {self.current_student.nama}.")

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
            "Minat Bakat": self._minat_bakat_page,
            "Portofolio": self._portofolio_page,
        }
        pages.get(page, self._dashboard)()

    def _dashboard(self):
        murid = self.current_student

        def aktivitas_belajar():
            # Progres dan agenda memakai seluruh kegiatan dari sumber data yang sama.
            seluruh_aktivitas = murid.items
            total = len(seluruh_aktivitas)
            selesai = sum(1 for item in seluruh_aktivitas if item.selesai)
            agenda = sorted(
                (
                    (item.deadline, item.judul, item.mapel, item.jenis(), item)
                    for item in murid.item_aktif()
                ),
                key=lambda data: (data[0], data[1].casefold())
            )
            return total, selesai, agenda

        self._page_header(
            "Dashboard",
            f"Selamat datang, {murid.nama}. Ini ringkasan progresmu."
        )

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=2, column=0, sticky="ew")
        cards.grid_columnconfigure((0, 1), weight=1)
        task_card = self._card(
            cards, "Tugas aktif", str(len(murid.item_aktif())),
            "Kegiatan yang belum selesai"
        )
        task_card.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        grade_card = self._card(
            cards, "Rata-rata nilai", f"{murid.nilai.rata_rata():.1f}",
            "Belum ada nilai" if not murid.nilai.daftar_mapel()
            else "Dari seluruh mata pelajaran"
        )
        grade_card.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        def update_card(card, value, note=None):
            details = card.winfo_children()[1]
            labels = details.winfo_children()
            labels[1].configure(text=value)
            if note is not None:
                labels[2].configure(text=note)

        panel = ctk.CTkFrame(
            self.content, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"]
        )
        panel.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        panel.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            panel, text="Progres & Agenda Belajar",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=COLORS["text"]
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(16, 3))
        ctk.CTkLabel(
            panel,
            text="Ringkasan seluruh kegiatan yang tercatat",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=10)
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 12))

        progress_area = ctk.CTkFrame(panel, fg_color="transparent")
        progress_area.grid(row=2, column=0, sticky="new", padx=(18, 12), pady=(0, 16))
        agenda_area = ctk.CTkFrame(panel, fg_color="transparent")
        agenda_area.grid(row=2, column=1, sticky="new", padx=(12, 18), pady=(0, 16))

        ctk.CTkLabel(
            progress_area, text="Progres belajar",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, 10))
        progress_percent = ctk.CTkLabel(
            progress_area, text="0%",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=COLORS["primary"]
        )
        progress_percent.pack(anchor="w")
        progress_bar = ctk.CTkProgressBar(
            progress_area, height=10, progress_color=COLORS["primary"]
        )
        progress_bar.pack(fill="x", pady=(8, 8))
        activity_count = ctk.CTkLabel(
            progress_area, text="0 dari 0 aktivitas selesai",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=11)
        )
        activity_count.pack(anchor="w")
        remaining_count = ctk.CTkLabel(
            progress_area, text="0 aktivitas masih perlu dikerjakan",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=10)
        )
        remaining_count.pack(anchor="w", pady=(3, 0))

        ctk.CTkLabel(
            agenda_area, text="Agenda terdekat",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, 6))
        agenda_list = ctk.CTkFrame(agenda_area, fg_color="transparent")
        agenda_list.pack(fill="x")

        def refresh_dashboard():
            total, selesai, agenda = aktivitas_belajar()
            aktif = murid.item_aktif()
            rata_nilai = murid.nilai.rata_rata()
            progres = selesai / total if total else 0

            update_card(task_card, str(len(aktif)))
            update_card(
                grade_card, f"{rata_nilai:.1f}",
                "Belum ada nilai" if not murid.nilai.daftar_mapel()
                else "Dari seluruh mata pelajaran"
            )
            progress_percent.configure(text=f"{progres * 100:.0f}%")
            self._animate_progress(progress_bar, progres)
            activity_count.configure(text=f"{selesai} dari {total} aktivitas selesai")
            remaining_count.configure(text=f"{total - selesai} aktivitas masih perlu dikerjakan")

            for child in agenda_list.winfo_children():
                child.destroy()
            if not agenda:
                ctk.CTkLabel(
                    agenda_list, text="Belum ada kegiatan aktif.",
                    text_color=COLORS["muted"], font=ctk.CTkFont(size=11)
                ).pack(anchor="w", pady=8)
                return

            for tanggal, judul, mapel, jenis, objek in agenda[:5]:
                line = ctk.CTkFrame(
                    agenda_list, fg_color=COLORS["surface_alt"], corner_radius=9
                )
                line.pack(fill="x", pady=3)
                detail = ctk.CTkFrame(line, fg_color="transparent")
                detail.pack(side="left", fill="x", expand=True, padx=10, pady=7)
                ctk.CTkLabel(
                    detail, text=judul, text_color=COLORS["text"],
                    font=ctk.CTkFont(size=11, weight="bold"),
                    anchor="w", wraplength=270
                ).pack(anchor="w")
                ctk.CTkLabel(
                    detail, text=f"{jenis} · {mapel} · {tanggal:%d %b}",
                    text_color=COLORS["muted"], font=ctk.CTkFont(size=9),
                    anchor="w"
                ).pack(anchor="w", pady=(2, 0))

                def mark_done(current=objek):
                    if current.selesai:
                        return
                    current.tandai_selesai()
                    self._save()
                    refresh_dashboard()
                    self._notify("Aktivitas ditandai selesai.")

                ctk.CTkCheckBox(
                    line, text="Selesai", width=76,
                    checkbox_width=18, checkbox_height=18,
                    text_color=COLORS["text"], command=mark_done
                ).pack(side="right", padx=9)

        refresh_dashboard()

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
            form, values=["Mudah", "Sedang", "Sulit"],
            fg_color=COLORS["surface_alt"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"], text_color=COLORS["text"]
        )
        difficulty_menu.set("Sedang")
        difficulty_menu.grid(row=3, column=1, padx=(8, 16), pady=(8, 4), sticky="ew")

        duration_entry = ctk.CTkEntry(
            form, placeholder_text="Estimasi durasi (15-480 menit)", height=38
        )
        duration_entry.insert(0, "60")
        duration_entry.grid(row=3, column=0, padx=(16, 8), pady=(8, 4), sticky="ew")

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

        form_feedback = ctk.CTkLabel(
            form, text="", text_color=COLORS["danger"],
            font=ctk.CTkFont(size=10), wraplength=800, justify="left"
        )
        form_feedback.grid(row=6, column=0, columnspan=2, padx=16, pady=(2, 8), sticky="w")

        def show_message(message):
            form_feedback.configure(text=message, text_color=COLORS["danger"])

        def bersihkan_jadwal_tidak_terkait():
            """Hapus sesi otomatis yang sumber kegiatannya sudah tidak ada."""
            item_aktif = {
                (item.judul, item.mapel, item.jenis())
                for item in self.current_student.items
                if not item.selesai
            }
            self.current_student.jadwal = [
                sesi for sesi in self.current_student.jadwal
                if (
                    sesi.get("judul"),
                    sesi.get("mapel"),
                    sesi.get("jenis")
                ) in item_aktif
            ]

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
                difficulty_text = (
                    f"  |  Kesulitan {item.kesulitan}"
                    if item.jenis() == "Tugas" else ""
                )
                ctk.CTkLabel(
                    info,
                    text=f"{item.mapel}  |  Durasi {item.durasi_menit} menit{difficulty_text}  |  Tenggat {item.deadline:%d-%m-%Y}  |  {status}",
                    text_color=COLORS["muted"], font=ctk.CTkFont(size=10)
                ).pack(anchor="w", pady=(3, 0))

                actions = ctk.CTkFrame(row, fg_color="transparent")
                actions.pack(side="right", padx=8)

                status_var = ctk.BooleanVar(value=item.selesai)
                done_checkbox = ctk.CTkCheckBox(
                    actions, text="Selesai", variable=status_var,
                    checkbox_width=18, checkbox_height=18,
                    text_color=COLORS["text"],
                    command=lambda current=item: complete_item(current)
                )
                done_checkbox.pack(side="left", padx=3)
                if item.selesai:
                    done_checkbox.configure(state="disabled")

                ctk.CTkButton(
                    actions, text="Hapus", width=62, height=30,
                    fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                    command=lambda current=item: delete_item(current)
                ).pack(side="left", padx=3)

        def complete_item(item):
            if not item.selesai:
                item.tandai_selesai()
                bersihkan_jadwal_tidak_terkait()
                self._save()
                refresh_list()
                self._notify("Kegiatan ditandai selesai.")

        def delete_item(item):
            if not self._confirm(
                "Hapus kegiatan?",
                f"Kegiatan '{item.judul}' akan dihapus dari daftar. Tindakan ini tidak dapat dibatalkan."
            ):
                return
            self.current_student.items.remove(item)
            bersihkan_jadwal_tidak_terkait()
            self._save()
            refresh_list()
            self._notify("Kegiatan berhasil dihapus.")

        def add_item():
            title = title_entry.get().strip()
            subject = subject_entry.get().strip()
            raw_date = date_entry.get().strip()
            raw_duration = duration_entry.get().strip()

            if not title or not subject or not raw_date or not raw_duration:
                show_message(
                    "Nama, mata pelajaran, tenggat, dan durasi wajib diisi."
                )
                return

            try:
                deadline = date.fromisoformat(raw_date)
                kind = type_menu.get()
                duration = int(raw_duration)

                if kind == "Tugas":
                    item = Tugas(
                        title, subject, deadline, difficulty_menu.get(), duration
                    )
                elif kind == "Ujian":
                    item = Ujian(title, subject, deadline, duration)
                else:
                    item = SesiBelajar(title, subject, deadline, duration)

                self.current_student.tambah_item(item)
                self._save()
                refresh_list()
                title_entry.delete(0, "end")
                subject_entry.delete(0, "end")
                date_entry.delete(0, "end")
                date_entry.insert(0, date.today().isoformat())
                duration_entry.delete(0, "end")
                duration_entry.insert(0, "60")
                type_menu.set("Tugas")
                difficulty_menu.set("Sedang")
                form_feedback.configure(text="")
                self._notify("Kegiatan berhasil ditambahkan.")
            except ValueError as error:
                show_message(
                    "Periksa tanggal dan durasi. Tanggal memakai YYYY-MM-DD. "
                    "Durasi harus berupa angka 15 sampai 480 menit. "
                    f"Detail: {error}"
                )

        ctk.CTkButton(
            form, text="Tambah kegiatan", height=38, command=add_item,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"]
        ).grid(row=4, column=0, columnspan=2, padx=16, pady=(8, 4), sticky="ew")

        ctk.CTkLabel(
            form,
            text="Durasi berlaku untuk semua kegiatan. Maksimal 480 menit. Kesulitan hanya berlaku untuk Tugas.",
            text_color=COLORS["muted"], font=ctk.CTkFont(size=10)
        ).grid(row=5, column=0, columnspan=2, padx=16, pady=(4, 14), sticky="w")

        refresh_list()
        self._jadwal_panel()

    def _jadwal_panel(self):
        from datetime import date, datetime
        from services.penjadwalan import Penjadwalan

        panel = ctk.CTkFrame(self.content, fg_color=COLORS["surface"], corner_radius=14)
        panel.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            panel, text="Jadwal belajar otomatis",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(
            panel,
            text=("Atur hari dan waktu luang. FutureMate akan menyusun sesi untuk "
                  "semua kegiatan aktif, termasuk tugas, ujian, dan sesi belajar."),
            text_color=COLORS["muted"], font=ctk.CTkFont(size=10),
            wraplength=820, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 8))
        ctk.CTkLabel(
            panel,
            text="Jadwal mencakup 30 hari ke depan. Setiap sesi maksimal 60 menit dengan jeda 15 menit.",
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
            ctk.CTkCheckBox(
                days_frame, text=day[:3], variable=var,
                text_color=COLORS["text"], checkbox_width=16,
                checkbox_height=16
            ).pack(side="left", padx=5, pady=5)

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

        schedule_frame = ctk.CTkScrollableFrame(
            panel, fg_color=COLORS["surface_alt"], height=190, corner_radius=10
        )
        schedule_frame.pack(fill="x", padx=14, pady=(4, 12))

        def refresh_schedule():
            for child in schedule_frame.winfo_children():
                child.destroy()
            sessions = sorted(
                self.current_student.jadwal,
                key=lambda session: (session.get("tanggal", ""), session.get("mulai", ""))
            )
            if not sessions:
                ctk.CTkLabel(
                    schedule_frame,
                    text="Belum ada jadwal. Tekan tombol Buat Jadwal Otomatis.",
                    text_color=COLORS["muted"]
                ).pack(anchor="w", padx=8, pady=10)
                return

            for session in sessions:
                row = ctk.CTkFrame(
                    schedule_frame, fg_color=COLORS["surface"], corner_radius=8
                )
                row.pack(fill="x", padx=4, pady=4)
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=9, pady=7)
                tanggal_obj = date.fromisoformat(session["tanggal"])
                jenis = session.get("jenis", "Kegiatan")
                ctk.CTkLabel(
                    info, text=f'{session["judul"]} · {session["mapel"]}',
                    text_color=COLORS["text"],
                    font=ctk.CTkFont(size=12, weight="bold")
                ).pack(anchor="w")
                ctk.CTkLabel(
                    info,
                    text=f'{jenis} · {Penjadwalan.HARI[tanggal_obj.weekday()]}, {tanggal_obj:%d-%m-%Y} · {session["mulai"]} · {session["durasi"]} menit',
                    text_color=COLORS["muted"], font=ctk.CTkFont(size=10)
                ).pack(anchor="w")
                done_var = ctk.BooleanVar(value=session.get("selesai", False))
                done_checkbox = ctk.CTkCheckBox(
                    row, text="Selesai", variable=done_var,
                    checkbox_width=18, checkbox_height=18,
                    text_color=COLORS["text"],
                    command=lambda current=session: complete_session(current)
                )
                done_checkbox.pack(side="right", padx=6)
                if session.get("selesai", False):
                    done_checkbox.configure(state="disabled")

        def complete_session(session):
            if not session.get("selesai", False):
                session["selesai"] = True
                self._save()
                refresh_schedule()

        def generate_schedule():
            if self.current_student.jadwal and not self._confirm(
                "Buat ulang jadwal?",
                "Jadwal tersimpan akan diganti dengan hasil baru. Status selesai pada sesi yang cocok akan dipertahankan."
            ):
                return
            try:
                selected_days = [i for i, var in enumerate(day_vars) if var.get()]
                start, end = start_entry.get().strip(), end_entry.get().strip()
                datetime.strptime(start, "%H:%M")
                datetime.strptime(end, "%H:%M")
                self.current_student.preferensi_jadwal = {
                    "hari": selected_days, "mulai": start, "selesai": end
                }
                jadwal_lama = {
                    (
                        sesi.get("judul"), sesi.get("mapel"), sesi.get("jenis"),
                        sesi.get("tanggal"), sesi.get("mulai"), sesi.get("durasi")
                    ): sesi.get("selesai", False)
                    for sesi in self.current_student.jadwal
                }
                jadwal_baru = Penjadwalan.buat_jadwal(
                    self.current_student.item_aktif(), selected_days, start, end
                )
                for sesi in jadwal_baru:
                    kunci = (
                        sesi.get("judul"), sesi.get("mapel"), sesi.get("jenis"),
                        sesi.get("tanggal"), sesi.get("mulai"), sesi.get("durasi")
                    )
                    sesi["selesai"] = jadwal_lama.get(kunci, False)
                self.current_student.jadwal = jadwal_baru
                self._save()
                refresh_schedule()
                if not jadwal_baru:
                    self._notify(
                        "Jadwal belum terbentuk. Periksa kegiatan aktif, hari, waktu luang, dan tenggat.",
                        "warning", 3600
                    )
                else:
                    self._notify("Jadwal otomatis berhasil dibuat.")
            except ValueError as error:
                self._notify(str(error), "error", 3600)

        ctk.CTkLabel(
            panel,
            text="Membuat ulang jadwal akan mengganti jadwal tersimpan. Status selesai tetap dipertahankan untuk sesi yang cocok.",
            text_color=COLORS["warning"], font=ctk.CTkFont(size=10),
            wraplength=820, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 8))
        ctk.CTkButton(
            panel, text="Buat Jadwal Otomatis", command=generate_schedule,
            height=36, fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"], text_color=COLORS["text"]
        ).pack(fill="x", padx=14, pady=(0, 12))
        refresh_schedule()

    def _section_card(self, parent, title, description):
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["surface"], corner_radius=14,
            border_width=1, border_color=COLORS["border"]
        )
        # Cari baris kosong berikutnya berdasarkan widget yang benar-benar
        # memakai grid. Jumlah seluruh child bisa keliru jika ada widget
        # yang dibuat dengan pack atau ditempatkan pada baris khusus.
        used_rows = [
            int(widget.grid_info().get("row", 0))
            for widget in parent.grid_slaves()
        ]
        row_index = max(used_rows, default=-1) + 1
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
        from exceptions import NilaiTidakValidError

        self._page_header(
            "Nilai Akademik",
            "Catat nilai rapor semester 1 sampai 5 dan rencanakan target akademikmu."
        )

        form = self._section_card(
            self.content, "Input nilai rapor",
            "Pilih semester, masukkan mata pelajaran, lalu isi nilai rapor pada rentang 0 sampai 100. Nilai mapel yang sama pada semester tersebut akan diperbarui."
        )

        fields = ctk.CTkFrame(form, fg_color="transparent")
        fields.pack(fill="x", padx=18, pady=(0, 10))
        fields.grid_columnconfigure((0, 1), weight=1)

        semester_menu = ctk.CTkOptionMenu(
            fields, values=[f"Semester {i}" for i in range(1, 6)],
            fg_color=COLORS["surface_alt"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"], text_color=COLORS["text"]
        )
        semester_menu.set("Semester 1")
        semester_menu.grid(row=0, column=0, padx=(0, 7), pady=4, sticky="ew")

        subject = ctk.CTkEntry(
            fields, placeholder_text="Mata pelajaran, contoh: Matematika", height=38
        )
        subject.grid(row=0, column=1, padx=(7, 0), pady=4, sticky="ew")

        score = ctk.CTkEntry(fields, placeholder_text="Nilai rapor, contoh: 88", height=38)
        score.grid(row=1, column=0, padx=(0, 7), pady=4, sticky="ew")

        message = ctk.CTkLabel(form, text="", text_color=COLORS["danger"])
        message.pack(anchor="w", padx=18, pady=(0, 4))
        editing_score = {"semester": None, "mapel": None}

        summary = ctk.CTkFrame(self.content, fg_color="transparent")
        summary.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        summary.grid_columnconfigure((0, 1), weight=1)
        semester_card = self._card(
            summary, "Rerata semester", "Belum ada", "Rata-rata nilai pada semester terpilih"
        )
        semester_card.grid(row=0, column=0, sticky="ew", padx=(0, 7))
        overall_card = self._card(
            summary, "Rerata sementara", "Belum ada", "Rata-rata dari semester yang sudah terisi"
        )
        overall_card.grid(row=0, column=1, sticky="ew", padx=(7, 0))

        semester_summary = self._section_card(
            self.content, "Ringkasan lima semester",
            "Rerata setiap semester akan muncul di sini setelah kamu memasukkan nilai rapornya."
        )
        semester_summary_rows = ctk.CTkFrame(
            semester_summary, fg_color="transparent"
        )
        semester_summary_rows.pack(fill="x", padx=18, pady=(0, 12))

        target_panel = self._section_card(
            self.content, "Target rerata akhir",
            "Tentukan target rerata rapor sampai semester 5. FutureMate akan menghitung rerata yang perlu kamu capai pada semester tersisa."
        )
        target_row = ctk.CTkFrame(target_panel, fg_color="transparent")
        target_row.pack(fill="x", padx=18, pady=(0, 8))
        target_row.grid_columnconfigure((0, 1), weight=1)
        target_entry = ctk.CTkEntry(
            target_row, placeholder_text="Target rerata akhir, contoh: 88", height=38
        )
        target_entry.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        saved_target = self.current_student.nilai.target_akhir()
        if saved_target is not None:
            target_entry.insert(0, str(saved_target))
        target_status = ctk.CTkLabel(
            target_panel, text="", text_color=COLORS["primary"],
            wraplength=800, justify="left"
        )
        target_status.pack(anchor="w", padx=18, pady=(2, 14))

        history = self._section_card(
            self.content, "Nilai rapor per mata pelajaran",
            "Pilih semester pada bagian input untuk melihat daftar nilainya. Kamu dapat memperbarui atau menghapus nilai."
        )
        rows = ctk.CTkFrame(history, fg_color="transparent")
        rows.pack(fill="x", padx=18, pady=(0, 14))

        def update_card_value(card, value):
            card.winfo_children()[1].winfo_children()[1].configure(text=value)

        def refresh():
            for child in rows.winfo_children():
                child.destroy()

            murid = self.current_student
            semester = int(semester_menu.get().split()[-1])
            daftar = murid.nilai.data_semester(semester)
            rata_sem = murid.nilai.rata_semester(semester)
            rata_total = murid.nilai.rata_akhir()

            update_card_value(
                semester_card, f"{rata_sem:.2f}" if rata_sem is not None else "Belum ada"
            )
            update_card_value(
                overall_card, f"{rata_total:.2f}" if murid.nilai.semester_terisi() else "Belum ada"
            )

            for child in semester_summary_rows.winfo_children():
                child.destroy()
            for nomor in range(1, 6):
                nilai_semester = murid.nilai.rata_semester(nomor)
                row = ctk.CTkFrame(
                    semester_summary_rows, fg_color=COLORS["surface_alt"], corner_radius=8
                )
                row.pack(fill="x", pady=3)
                ctk.CTkLabel(
                    row, text=f"Semester {nomor}", text_color=COLORS["text"]
                ).pack(side="left", padx=12, pady=8)
                ctk.CTkLabel(
                    row,
                    text=f"{nilai_semester:.2f}" if nilai_semester is not None else "Belum diisi",
                    text_color=COLORS["primary"] if nilai_semester is not None else COLORS["muted"]
                ).pack(side="right", padx=12, pady=8)

            if not daftar:
                ctk.CTkLabel(
                    rows, text=f"Belum ada nilai rapor untuk Semester {semester}.",
                    text_color=COLORS["muted"]
                ).pack(anchor="w", pady=8)
            else:
                for mapel, nilai in sorted(daftar.items()):
                    line = ctk.CTkFrame(
                        rows, fg_color=COLORS["surface_alt"], corner_radius=9
                    )
                    line.pack(fill="x", pady=4)
                    ctk.CTkLabel(
                        line, text=mapel, text_color=COLORS["text"],
                        font=ctk.CTkFont(size=12, weight="bold")
                    ).pack(side="left", padx=12, pady=10)
                    ctk.CTkLabel(
                        line, text=f"{nilai:.2f}", text_color=COLORS["text"]
                    ).pack(side="right", padx=(8, 12))
                    ctk.CTkButton(
                        line, text="Hapus", width=58, height=27,
                        fg_color=COLORS["danger"],
                        command=lambda m=mapel, s=semester: remove_score(s, m)
                    ).pack(side="right", padx=4)
                    ctk.CTkButton(
                        line, text="Edit", width=52, height=27,
                        command=lambda m=mapel, v=nilai, s=semester: load_score(s, m, v)
                    ).pack(side="right", padx=4)

            target = murid.nilai.target_akhir()
            required = murid.nilai.kebutuhan_semester_berikutnya()
            filled = len(murid.nilai.semester_terisi())
            if target is None:
                target_status.configure(text="Kamu belum menetapkan target rerata akhir.")
            elif required is None:
                target_status.configure(
                    text=f"Rerata lima semester saat ini: {rata_total:.2f}. "
                         f"Target akhir: {target:.2f}."
                )
            elif required > 100:
                target_status.configure(
                    text=f"Target {target:.2f} membutuhkan rerata sekitar {required:.2f} "
                         f"pada setiap semester tersisa. Target ini berada di atas batas nilai 100."
                )
            elif required < 0:
                target_status.configure(
                    text=f"Target {target:.2f} sudah tercapai berdasarkan data saat ini. "
                         "Kamu tetap bisa menjaga nilai pada semester berikutnya."
                )
            else:
                target_status.configure(
                    text=f"Semester terisi: {filled}/5. Untuk mencapai target akhir {target:.2f}, "
                         f"kamu perlu meraih rerata sekitar {required:.2f} pada setiap semester tersisa."
                )

        def load_score(semester, mapel, nilai):
            editing_score["semester"] = semester
            editing_score["mapel"] = mapel
            semester_menu.set(f"Semester {semester}")
            semester_menu.configure(state="disabled")
            subject.delete(0, "end")
            subject.insert(0, mapel)
            score.delete(0, "end")
            score.insert(0, f"{nilai:g}")
            save_score_button.configure(text="Perbarui nilai rapor")
            cancel_edit_button.pack(fill="x", padx=18, pady=(0, 10))
            message.configure(
                text=f"Mode edit: {mapel}, Semester {semester}. Ubah data lalu pilih Perbarui.",
                text_color=COLORS["primary"]
            )
            subject.focus_set()

        def cancel_score_edit():
            editing_score.update(semester=None, mapel=None)
            semester_menu.configure(state="normal")
            subject.delete(0, "end")
            score.delete(0, "end")
            save_score_button.configure(text="Simpan nilai rapor")
            cancel_edit_button.pack_forget()
            message.configure(text="Mode edit dibatalkan.", text_color=COLORS["muted"])

        def remove_score(semester, mapel):
            if not self._confirm(
                "Hapus nilai rapor?",
                f"Nilai {mapel} pada Semester {semester} akan dihapus."
            ):
                return
            self.current_student.nilai.hapus_nilai_rapor(semester, mapel)
            self._save()
            refresh()
            self._notify("Nilai rapor berhasil dihapus.")

        def add_score():
            try:
                mapel = subject.get().strip()
                value = float(score.get().strip().replace(",", "."))
                semester = int(semester_menu.get().split()[-1])
                if editing_score["mapel"] is not None:
                    old_mapel = editing_score["mapel"]
                    old_semester = editing_score["semester"]
                    normalized_name = mapel.title()
                    existing = self.current_student.nilai.data_semester(old_semester)
                    if normalized_name != old_mapel and normalized_name in existing:
                        raise ValueError(
                            f"Nilai untuk {normalized_name} sudah ada pada Semester {old_semester}."
                        )
                    # Validasi nilai dan nama dilakukan sebelum data lama dihapus.
                    if not mapel:
                        raise ValueError("Nama mata pelajaran wajib diisi.")
                    if not 0 <= value <= 100:
                        raise NilaiTidakValidError("Nilai harus di antara 0 dan 100.")
                    nilai_model = self.current_student.nilai
                    if normalized_name != old_mapel:
                        nilai_model.hapus_nilai_rapor(old_semester, old_mapel)
                    nilai_model.tambah_nilai_rapor(old_semester, normalized_name, value)
                    saved_semester = old_semester
                    success_message = "Perubahan nilai rapor berhasil disimpan."
                else:
                    self.current_student.nilai.tambah_nilai_rapor(semester, mapel, value)
                    saved_semester = semester
                    success_message = "Nilai rapor berhasil disimpan."

                self._save()
                editing_score.update(semester=None, mapel=None)
                semester_menu.configure(state="normal")
                subject.delete(0, "end")
                score.delete(0, "end")
                save_score_button.configure(text="Simpan nilai rapor")
                cancel_edit_button.pack_forget()
                message.configure(text=success_message, text_color=COLORS["success"])
                semester_menu.set(f"Semester {saved_semester}")
                refresh()
                self._notify(success_message)
            except (ValueError, NilaiTidakValidError) as error:
                message.configure(text=str(error), text_color=COLORS["danger"])

        def save_target():
            try:
                raw = target_entry.get().strip().replace(",", ".")
                if not raw:
                    raise ValueError("Masukkan target rerata akhir terlebih dahulu.")
                self.current_student.nilai.set_target_akhir(float(raw))
                self._save()
                message.configure(text="")
                refresh()
                self._notify("Target rerata akhir berhasil disimpan.")
            except ValueError as error:
                target_status.configure(text=str(error), text_color=COLORS["danger"])

        semester_menu.configure(command=lambda _value: refresh())

        save_score_button = ctk.CTkButton(
            form, text="Simpan nilai rapor", command=add_score, height=40,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"]
        )
        save_score_button.pack(fill="x", padx=18, pady=(4, 6))
        cancel_edit_button = ctk.CTkButton(
            form, text="Batal edit", command=cancel_score_edit, height=32,
            fg_color=COLORS["surface"], hover_color=COLORS["border"],
            text_color=COLORS["text"]
        )

        ctk.CTkButton(
            target_row, text="Simpan target akhir", command=save_target, height=40,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"]
        ).grid(row=1, column=0, columnspan=2, sticky="ew")

        refresh()

    def _minat_bakat_page(self):
        import json
        import math
        from pathlib import Path
        from services.minat_bakat import (
            NAMA_TIPE, DESKRIPSI_TIPE, PERTANYAAN_PER_TIPE,
            SKALA_JAWABAN, hitung_profil, tipe_teratas, rekomendasikan
        )

        catalog_path = Path(__file__).resolve().parents[1] / "data" / "jurusan_minat.json"
        try:
            with catalog_path.open("r", encoding="utf-8") as file:
                katalog = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            self._message("Katalog tidak tersedia", str(error))
            katalog = []

        murid = self.current_student
        if not hasattr(self, "mb_view"):
            self.mb_view = "Beranda"
        if not hasattr(self, "mb_section"):
            self.mb_section = 0
        if not hasattr(self, "mb_selected_major"):
            self.mb_selected_major = None
        if not hasattr(self, "mb_history_index"):
            self.mb_history_index = 0

        types = ["R", "I", "A", "S", "E", "C"]
        groups = ["Semua bidang"] + list(dict.fromkeys(item["bidang"] for item in katalog))
        profile = murid.profil_minat if isinstance(murid.profil_minat, dict) else {}
        # Konversi profil lama (skor 2-10 dari dua pertanyaan per tipe)
        # ke skala baru 0-100 agar data akun lama tetap terbaca.
        if profile and murid.riasec_history:
            profile = murid.riasec_history[-1].get("skor", profile)
        elif profile and max(float(v) for v in profile.values()) <= 10:
            profile = {
                t: round(max(0.0, min(100.0, ((float(profile.get(t, 2)) / 2 - 1) / 4) * 100)), 1)
                for t in types
            }

        def go(view):
            self.mb_view = view
            self.show_page("Minat Bakat")

        def section_card(parent, title, description=""):
            card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=14,
                                border_width=1, border_color=COLORS["border"])
            card.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(card, text=title, text_color=COLORS["text"],
                         font=ctk.CTkFont(size=16, weight="bold")).pack(
                             anchor="w", padx=16, pady=(14, 3))
            if description:
                ctk.CTkLabel(card, text=description, text_color=COLORS["muted"],
                             font=ctk.CTkFont(size=11), wraplength=820,
                             justify="left").pack(anchor="w", padx=16, pady=(0, 12))
            return card

        def action_button(parent, label, command, **kwargs):
            return ctk.CTkButton(
                parent, text=label, command=command, height=34,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                text_color=COLORS["text"], **kwargs
            )

        def draw_radar(parent, scores, width=300, height=280):
            from tkinter import Canvas
            canvas = Canvas(parent, width=width, height=height,
                            bg=COLORS["surface"], highlightthickness=0)
            canvas.pack(padx=8, pady=8)
            cx, cy, radius = width / 2, height / 2, min(width, height) * 0.32
            angles = [-math.pi / 2 + i * math.pi / 3 for i in range(6)]
            for fraction in (0.25, 0.5, 0.75, 1.0):
                points = []
                for angle in angles:
                    points.extend([cx + radius * fraction * math.cos(angle),
                                   cy + radius * fraction * math.sin(angle)])
                canvas.create_polygon(points, outline=COLORS["border"], fill="", width=1)
            values = []
            for i, angle in enumerate(angles):
                x, y = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
                canvas.create_line(cx, cy, x, y, fill=COLORS["border"])
                canvas.create_text(cx + (radius + 19) * math.cos(angle),
                                   cy + (radius + 19) * math.sin(angle),
                                   text=types[i], fill=COLORS["text"],
                                   font=("Arial", 10, "bold"))
                value = max(0, min(100, float(scores.get(types[i], 0))))
                values.extend([cx + radius * value / 100 * math.cos(angle),
                               cy + radius * value / 100 * math.sin(angle)])
            canvas.create_polygon(values, fill=COLORS["primary"], stipple="gray25",
                                  outline=COLORS["primary_hover"], width=2)
            return canvas

        def score_bars(parent, scores):
            for tipe in types:
                row = ctk.CTkFrame(parent, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=4)
                ctk.CTkLabel(row, text=f"{tipe} · {NAMA_TIPE[tipe]}",
                             text_color=COLORS["text"], width=180,
                             anchor="w").pack(side="left")
                value = max(0, min(100, float(scores.get(tipe, 0))))
                bar = ctk.CTkProgressBar(row, height=10,
                                         progress_color=COLORS["primary"])
                bar.pack(side="left", fill="x", expand=True, padx=8)
                self._animate_progress(bar, value / 100)
                ctk.CTkLabel(row, text=f"{value:.1f}", width=48,
                             text_color=COLORS["muted"]).pack(side="right")

        def show_major_card(parent, major, match=None):
            card = ctk.CTkFrame(
                parent, fg_color=COLORS["surface_alt"], corner_radius=10,
                border_width=1, border_color=COLORS["border"]
            )
            card.pack(fill="x", padx=8, pady=5)
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=12, pady=10)
            ctk.CTkLabel(info, text=major["nama"], text_color=COLORS["text"],
                         font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
            subtitle = major["bidang"]
            if match is not None:
                subtitle += f" · Kecocokan {match:.1f}%"
            ctk.CTkLabel(info, text=subtitle, text_color=COLORS["muted"],
                         font=ctk.CTkFont(size=10)).pack(anchor="w", pady=(2, 0))
            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.pack(side="right", padx=8)
            ctk.CTkButton(actions, text="Detail", width=65, height=29,
                          command=lambda item=major: open_major(item)).pack(side="left", padx=3)
            fav_label = "Tersimpan" if any(x.get("nama") == major["nama"] for x in murid.favorite_majors) else "☆ Favorit"
            favorite_button = ctk.CTkButton(
                actions, text=fav_label, width=85, height=29,
                fg_color=COLORS["surface"], text_color=COLORS["text"],
                command=lambda item=major, target=None: toggle_favorite(item, match, target)
            )
            favorite_button.configure(
                command=lambda item=major, target=favorite_button: toggle_favorite(item, match, target)
            )
            favorite_button.pack(side="left", padx=3)

            hover_state = {"pending": None}

            def update_card_hover(_event=None):
                if hover_state["pending"] is not None:
                    try:
                        card.after_cancel(hover_state["pending"])
                    except Exception:
                        pass

                def apply_hover():
                    try:
                        if not card.winfo_exists():
                            return
                        pointer_x, pointer_y = card.winfo_pointerxy()
                        inside = (
                            card.winfo_rootx() <= pointer_x <= card.winfo_rootx() + card.winfo_width()
                            and card.winfo_rooty() <= pointer_y <= card.winfo_rooty() + card.winfo_height()
                        )
                        card.configure(
                            border_color=COLORS["primary"] if inside else COLORS["border"]
                        )
                    except Exception:
                        return

                hover_state["pending"] = card.after(45, apply_hover)

            def bind_hover(widget):
                widget.bind("<Enter>", update_card_hover, add="+")
                widget.bind("<Leave>", update_card_hover, add="+")
                for child in widget.winfo_children():
                    bind_hover(child)

            bind_hover(card)

        def open_major(major):
            self.mb_selected_major = major["nama"]
            go("Detail Jurusan")

        def toggle_favorite(major, match=None, button=None):
            saved = next((x for x in murid.favorite_majors if x.get("nama") == major["nama"]), None)
            if saved:
                murid.favorite_majors.remove(saved)
                is_saved = False
            else:
                murid.favorite_majors.append({
                    "nama": major["nama"], "bidang": major["bidang"],
                    "kecocokan": match, "tanggal": __import__("datetime").datetime.now().isoformat(timespec="seconds")
                })
                is_saved = True
            self._save()
            if button is not None and button.winfo_exists():
                if self.mb_view == "Detail Jurusan":
                    button.configure(
                        text="★ Tersimpan di Favorit" if is_saved else "☆ Simpan ke Favorit"
                    )
                else:
                    button.configure(text="Tersimpan" if is_saved else "☆ Favorit")
            self._notify("Jurusan ditambahkan ke favorit." if is_saved else "Jurusan dihapus dari favorit.")

        self._page_header("Eksplorasi Minat RIASEC", "Kenali aktivitas yang menarik bagimu dan jelajahi pilihan program studi.")
        nav = ctk.CTkFrame(self.content, fg_color=COLORS["surface"], corner_radius=12)
        nav.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        nav_items = [
            ("Beranda", "Beranda"), ("Tes RIASEC", "Tes RIASEC"),
            ("Hasil Tes", "Hasil Tes"), ("Katalog Jurusan", "Katalog Jurusan"),
            ("Favorit", "Favorit"), ("Riwayat Tes", "Riwayat Tes")
        ]
        for label, view in nav_items:
            ctk.CTkButton(
                nav, text=label, height=34, corner_radius=8,
                fg_color=COLORS["primary"] if self.mb_view == view else "transparent",
                hover_color=COLORS["surface_alt"],
                text_color=COLORS["text"], command=lambda v=view: go(v)
            ).pack(side="left", padx=4, pady=7)

        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=3, column=0, sticky="ew")
        body.grid_columnconfigure(0, weight=1)

        if self.mb_view == "Beranda":
            card = section_card(body, "Profil minatmu",
                                "Kerjakan tes untuk mengeksplorasi enam dimensi minat RIASEC. Hasilnya menjadi bahan refleksi awal, bukan ukuran bakat atau kemampuan.")
            if murid.riasec_history:
                latest = murid.riasec_history[-1]
                ctk.CTkLabel(card, text="Tipe minat teratas: " + " · ".join(
                    f"{t} ({NAMA_TIPE[t]})" for t in latest["tiga_teratas"]),
                    text_color=COLORS["primary"], font=ctk.CTkFont(size=14, weight="bold")
                ).pack(anchor="w", padx=16, pady=4)
                ctk.CTkLabel(card, text=f"Tes terakhir: {latest['tanggal'][:10]}",
                             text_color=COLORS["muted"]).pack(anchor="w", padx=16, pady=(0, 12))
            else:
                action_button(card, "Mulai Tes RIASEC", lambda: go("Tes RIASEC")).pack(
                    anchor="w", padx=16, pady=(0, 14))
            limits = section_card(
                body, "Batas penggunaan tes",
                "Tes ini disusun untuk eksplorasi minat berdasarkan kerangka RIASEC. "
                "Instrumen belum melalui validasi psikometri. Hasil bukan ukuran bakat "
                "atau kemampuan, diagnosis, maupun penentu jurusan dan karier. "
                "Gunakan sebagai bahan refleksi dan diskusikan dengan guru BK."
            )
            ctk.CTkLabel(
                limits,
                text="Landasan konsep: teori Holland RIASEC, O*NET Interest Profiler, "
                     "dan Profiler Minat Karier Kemnaker. Butir FutureMate disusun mandiri.",
                text_color=COLORS["muted"], wraplength=800, justify="left"
            ).pack(anchor="w", padx=16, pady=(0, 12))
            access = section_card(body, "Jelajahi Minat RIASEC",
                                  "Pilih fitur yang ingin kamu gunakan.")
            for label, view in nav_items[1:]:
                action_button(access, label, lambda v=view: go(v), width=190).pack(
                    side="left", padx=6, pady=(0, 14))
            if profile:
                recommendations = rekomendasikan(profile, katalog, 3)
                rec = section_card(body, "Rekomendasi jurusan teratas",
                                   "Tiga rekomendasi teratas berdasarkan hasil tes terbarumu.")
                for major, match in recommendations:
                    show_major_card(rec, major, match)
                action_button(rec, "Lihat 10 rekomendasi", lambda: go("Hasil Tes")).pack(
                    anchor="e", padx=14, pady=12)
            activity = section_card(body, "Aktivitas terbaru")
            ctk.CTkLabel(activity,
                         text=f"{len(murid.riasec_history)} tes tersimpan · {len(murid.favorite_majors)} jurusan favorit",
                         text_color=COLORS["muted"]).pack(anchor="w", padx=16, pady=(0, 10))
            action_button(activity, "Ulangi tes", lambda: go("Tes RIASEC")).pack(
                anchor="w", padx=16, pady=(0, 14))

        elif self.mb_view == "Tes RIASEC":
            section = self.mb_section
            tipe = types[section]
            answered = murid.riasec_answers
            answered_count = sum(str(i) in answered for i in range(60))
            card = section_card(body, "Tes Minat RIASEC",
                "Seberapa tertarik kamu melakukan setiap aktivitas? Jawaban tersimpan otomatis saat kamu memilih angka.")
            ctk.CTkLabel(card, text=f"Bagian {section + 1} dari 6 · {tipe} · {NAMA_TIPE[tipe]}",
                         text_color=COLORS["primary"], font=ctk.CTkFont(size=15, weight="bold")
                         ).pack(anchor="w", padx=16)
            ctk.CTkLabel(card, text=DESKRIPSI_TIPE[tipe], text_color=COLORS["muted"]
                         ).pack(anchor="w", padx=16, pady=(3, 8))
            ctk.CTkLabel(
                card,
                text="Tes eksplorasi minat. Instrumen belum tervalidasi secara psikometri. "
                     "Jawaban menunjukkan ketertarikan pada aktivitas, bukan tingkat kemampuan.",
                text_color=COLORS["warning"], wraplength=800, justify="left"
            ).pack(anchor="w", padx=16, pady=(0, 8))
            progress = ctk.CTkProgressBar(card, progress_color=COLORS["primary"])
            progress.pack(fill="x", padx=16, pady=5)
            self._animate_progress(progress, answered_count / 60)
            answered_label = ctk.CTkLabel(
                card, text=f"{answered_count} dari 60 pertanyaan terjawab",
                text_color=COLORS["muted"]
            )
            answered_label.pack(anchor="w", padx=16, pady=(0, 10))
            scroll = ctk.CTkScrollableFrame(card, fg_color="transparent", height=490)
            scroll.pack(fill="x", padx=10, pady=(0, 10))
            for idx, question in enumerate(PERTANYAAN_PER_TIPE[tipe]):
                question_index = section * 10 + idx
                block = ctk.CTkFrame(scroll, fg_color=COLORS["surface_alt"], corner_radius=9)
                block.pack(fill="x", padx=4, pady=5)
                ctk.CTkLabel(block, text=f"{idx + 1}. {question}", text_color=COLORS["text"],
                             wraplength=780, justify="left").pack(anchor="w", padx=12, pady=(10, 6))
                choice = ctk.CTkSegmentedButton(
                    block, values=["1", "2", "3", "4", "5"],
                    selected_color=COLORS["primary"],
                    selected_hover_color=COLORS["primary_hover"],
                    unselected_color=COLORS["surface"], text_color=COLORS["text"]
                )
                current = answered.get(str(question_index))
                if current is not None:
                    choice.set(str(current))
                choice.pack(anchor="e", padx=10, pady=(0, 9))
                choice.configure(command=lambda value, i=question_index: save_answer(i, value))
            def save_answer(index, value):
                murid.riasec_answers[str(index)] = int(value)
                self._animate_progress(progress, len(murid.riasec_answers) / 60)
                answered_label.configure(
                    text=f"{len(murid.riasec_answers)} dari 60 pertanyaan terjawab · Tersimpan",
                    text_color=COLORS["success"]
                )
                self._save()
            controls = ctk.CTkFrame(card, fg_color="transparent")
            controls.pack(fill="x", padx=14, pady=(0, 14))
            ctk.CTkButton(controls, text="Sebelumnya", width=110,
                          state="normal" if section > 0 else "disabled",
                          command=lambda: change_section(-1)).pack(side="left")
            ctk.CTkButton(controls, text="Berikutnya", width=110,
                          fg_color=COLORS["primary"], text_color=COLORS["text"],
                          command=lambda: change_section(1)).pack(side="right")
            ctk.CTkLabel(card, text="Skala: 1 Sangat tidak tertarik · 2 Tidak tertarik · 3 Netral · 4 Tertarik · 5 Sangat tertarik",
                         text_color=COLORS["muted"], font=ctk.CTkFont(size=10),
                         wraplength=800).pack(anchor="w", padx=16, pady=(0, 12))
            def change_section(offset):
                self.mb_section = max(0, min(5, self.mb_section + offset))
                self.show_page("Minat Bakat")
            section_nav = ctk.CTkFrame(body, fg_color="transparent")
            section_nav.pack(fill="x", pady=(0, 10))
            for i, t in enumerate(types):
                section_answered = sum(
                    str(question_index) in answered
                    for question_index in range(i * 10, (i + 1) * 10)
                )
                section_label = (
                    f"{t} ✓" if section_answered == 10
                    else f"{t} {section_answered}/10" if section_answered
                    else t
                )
                section_color = (
                    COLORS["primary"] if i == section
                    else COLORS["primary_soft"] if section_answered == 10
                    else COLORS["surface"]
                )
                ctk.CTkButton(
                    section_nav, text=section_label, width=66, height=30,
                    fg_color=section_color, text_color=COLORS["text"],
                    command=lambda n=i: set_section(n)
                ).pack(side="left", padx=4)
            def set_section(index):
                self.mb_section = index
                self.show_page("Minat Bakat")
            if answered_count == 60:
                action_button(body, "Selesaikan Tes", lambda: finish_test()).pack(anchor="e", pady=8)
            else:
                ctk.CTkLabel(body, text=f"Lengkapi {60 - answered_count} jawaban lagi untuk menyelesaikan tes.",
                             text_color=COLORS["muted"]).pack(anchor="e", pady=8)
            ctk.CTkLabel(body, text="Kamu dapat berpindah bagian meskipun belum menjawab semua pertanyaan.",
                         text_color=COLORS["muted"], font=ctk.CTkFont(size=10)).pack(anchor="w")

        elif self.mb_view == "Hasil Tes":
            if not murid.riasec_history:
                card = section_card(body, "Belum ada hasil tes",
                                    "Selesaikan 60 pertanyaan RIASEC untuk melihat profil dan rekomendasi jurusan.")
                action_button(card, "Mulai tes", lambda: go("Tes RIASEC")).pack(
                    anchor="w", padx=16, pady=(0, 14))
            else:
                latest = murid.riasec_history[-1]
                top = latest["tiga_teratas"]
                pair = ctk.CTkFrame(body, fg_color="transparent")
                pair.pack(fill="x", pady=(0, 12))
                pair.grid_columnconfigure((0, 1), weight=1)
                radar = ctk.CTkFrame(pair, fg_color=COLORS["surface"], corner_radius=12)
                radar.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
                ctk.CTkLabel(radar, text="Diagram profil RIASEC",
                             text_color=COLORS["text"], font=ctk.CTkFont(size=15, weight="bold")
                             ).pack(pady=(12, 0))
                draw_radar(radar, latest["skor"])
                desc = ctk.CTkFrame(pair, fg_color=COLORS["surface"], corner_radius=12)
                desc.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
                ctk.CTkLabel(desc, text="Tipe minat teratas",
                             text_color=COLORS["text"], font=ctk.CTkFont(size=15, weight="bold")
                             ).pack(anchor="w", padx=14, pady=(14, 8))
                for tipe in top:
                    ctk.CTkLabel(desc, text=f"{tipe} · {NAMA_TIPE[tipe]}",
                                 text_color=COLORS["primary"], font=ctk.CTkFont(size=14, weight="bold")
                                 ).pack(anchor="w", padx=14, pady=(5, 1))
                    ctk.CTkLabel(desc, text=DESKRIPSI_TIPE[tipe], text_color=COLORS["muted"],
                                 wraplength=340, justify="left").pack(anchor="w", padx=14, pady=(0, 5))
                scores = section_card(body, "Rincian enam skor RIASEC",
                                      f"Hasil tes tanggal {latest['tanggal'][:10]}.")
                score_bars(scores, latest["skor"])
                rec = section_card(body, "Sepuluh rekomendasi jurusan",
                                   "Skor kemiripan dihitung dengan bobot sama untuk keenam dimensi RIASEC. Nilai ini hanya heuristik untuk menjelajahi katalog, bukan peluang atau prediksi keberhasilan studi.")
                for saved in latest["rekomendasi"]:
                    major = next((x for x in katalog if x["nama"] == saved["nama"]), None)
                    if major:
                        show_major_card(rec, major, saved["kecocokan"])
                action_button(body, "Ulangi Tes RIASEC", lambda: start_new_test()).pack(
                    anchor="e", pady=8)

        elif self.mb_view == "Katalog Jurusan":
            card = section_card(body, "Katalog 100 jurusan",
                                "Cari program studi dari sembilan kelompok bidang. Jika belum tes, kamu tetap dapat melihat profil RIASEC jurusan.")
            controls = ctk.CTkFrame(card, fg_color="transparent")
            controls.pack(fill="x", padx=12, pady=(0, 8))
            search = ctk.CTkEntry(controls, placeholder_text="Cari nama jurusan...", height=36)
            search.pack(side="left", fill="x", expand=True, padx=(0, 6))
            group_menu = ctk.CTkOptionMenu(controls, values=groups,
                                           fg_color=COLORS["surface_alt"],
                                           button_color=COLORS["primary"],
                                           text_color=COLORS["text"])
            group_menu.pack(side="left", padx=6)
            sort_menu = ctk.CTkOptionMenu(controls, values=["Nama A-Z", "Kecocokan tertinggi"],
                                          fg_color=COLORS["surface_alt"],
                                          button_color=COLORS["primary"],
                                          text_color=COLORS["text"])
            sort_menu.pack(side="left", padx=(6, 0))
            listing = ctk.CTkFrame(card, fg_color="transparent")
            listing.pack(fill="x", padx=8, pady=(0, 12))
            def refresh_catalog(*_):
                for child in listing.winfo_children():
                    child.destroy()
                query = search.get().strip().lower()
                chosen_group = group_menu.get()
                filtered = [x for x in katalog if query in x["nama"].lower()
                            and (chosen_group == "Semua bidang" or x["bidang"] == chosen_group)]
                if profile and sort_menu.get() == "Kecocokan tertinggi":
                    filtered.sort(key=lambda x: -__import__("services.minat_bakat", fromlist=["skor_kecocokan"]).skor_kecocokan(profile, x["riasec"]))
                else:
                    filtered.sort(key=lambda x: x["nama"].lower())
                ctk.CTkLabel(listing, text=f"{len(filtered)} jurusan ditemukan",
                             text_color=COLORS["muted"]).pack(anchor="w", pady=5)
                for major in filtered:
                    match = None
                    if profile:
                        match = __import__("services.minat_bakat", fromlist=["skor_kecocokan"]).skor_kecocokan(profile, major["riasec"])
                    show_major_card(listing, major, match)

            pending_search = {"after_id": None}

            def schedule_catalog_refresh(_event=None):
                if pending_search["after_id"] is not None:
                    try:
                        self.after_cancel(pending_search["after_id"])
                    except Exception:
                        pass
                pending_search["after_id"] = self.after(
                    140, lambda: (
                        refresh_catalog(),
                        pending_search.update(after_id=None)
                    )
                )

            search.bind("<KeyRelease>", schedule_catalog_refresh)
            group_menu.configure(command=refresh_catalog)
            sort_menu.configure(command=refresh_catalog)
            refresh_catalog()

        elif self.mb_view == "Detail Jurusan":
            major = next((x for x in katalog if x["nama"] == self.mb_selected_major), None)
            if not major:
                section_card(body, "Jurusan tidak ditemukan")
            else:
                identity = section_card(body, major["nama"], major["bidang"])
                ctk.CTkLabel(identity, text=major["deskripsi"], text_color=COLORS["text"],
                             wraplength=820, justify="left").pack(anchor="w", padx=16, pady=(0, 12))
                pair = ctk.CTkFrame(body, fg_color="transparent")
                pair.pack(fill="x", pady=(0, 12))
                pair.grid_columnconfigure((0, 1), weight=1)
                study = section_card(pair, "Gambaran perkuliahan", major["mata_kuliah"])
                career = section_card(pair, "Prospek karier", "Contoh bidang pekerjaan yang relevan.")
                for item in major["karier"]:
                    ctk.CTkLabel(career, text=f"• {item}", text_color=COLORS["muted"]).pack(
                        anchor="w", padx=16, pady=2)
                riasec = section_card(body, "Profil RIASEC jurusan",
                                      "Skor jurusan dipetakan menggunakan lima aspek: materi kuliah, praktikum/proyek, keterampilan, bidang pekerjaan, dan aktivitas umum.")
                draw_radar(riasec, major["riasec"])
                score_bars(riasec, major["riasec"])
                if profile:
                    from services.minat_bakat import skor_kecocokan
                    match = skor_kecocokan(profile, major["riasec"])
                    ctk.CTkLabel(riasec, text=f"Kecocokan dengan profil terakhirmu: {match:.1f}%",
                                 text_color=COLORS["primary"],
                                 font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=8)
                    reasons = sorted(types, key=lambda t: abs(profile.get(t, 0) - major["riasec"].get(t, 0)))
                    ctk.CTkLabel(riasec, text="Dimensi yang paling mendekati profilmu: " +
                                 ", ".join(f"{t} ({NAMA_TIPE[t]})" for t in reasons[:3]),
                                 text_color=COLORS["muted"], wraplength=800).pack(anchor="w", padx=16, pady=(0, 10))
                else:
                    ctk.CTkLabel(riasec, text="Kerjakan Tes RIASEC untuk melihat persentase kecocokan pribadimu.",
                                 text_color=COLORS["muted"]).pack(anchor="w", padx=16, pady=8)
                row = ctk.CTkFrame(body, fg_color="transparent")
                row.pack(fill="x", pady=8)
                match = None
                if profile:
                    from services.minat_bakat import skor_kecocokan
                    match = skor_kecocokan(profile, major["riasec"])
                already_favorite = any(
                    item.get("nama") == major["nama"] for item in murid.favorite_majors
                )
                favorite_button = action_button(
                    row,
                    "★ Tersimpan di Favorit" if already_favorite else "☆ Simpan ke Favorit",
                    lambda target=None: toggle_favorite(major, match, favorite_button)
                )
                favorite_button.pack(side="left")
                ctk.CTkButton(row, text="Kembali ke katalog", command=lambda: go("Katalog Jurusan")
                              ).pack(side="left", padx=8)

        elif self.mb_view == "Favorit":
            card = section_card(body, "Jurusan favorit",
                                "Persentase kecocokan disimpan sebagai snapshot dan tidak berubah setelah tes baru.")
            if not murid.favorite_majors:
                ctk.CTkLabel(card, text="Belum ada jurusan favorit.",
                             text_color=COLORS["muted"]).pack(anchor="w", padx=16, pady=(0, 12))
            for saved in list(murid.favorite_majors):
                major = next((x for x in katalog if x["nama"] == saved["nama"]), None)
                line = ctk.CTkFrame(card, fg_color=COLORS["surface_alt"], corner_radius=9)
                line.pack(fill="x", padx=8, pady=4)
                info = ctk.CTkFrame(line, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=10, pady=9)
                ctk.CTkLabel(info, text=saved["nama"], text_color=COLORS["text"],
                             font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
                detail = saved["bidang"]
                if saved.get("kecocokan") is not None:
                    detail += f" · Snapshot kecocokan {saved['kecocokan']:.1f}%"
                ctk.CTkLabel(info, text=detail + f" · {saved['tanggal'][:10]}",
                             text_color=COLORS["muted"], font=ctk.CTkFont(size=10)).pack(anchor="w")
                if major:
                    ctk.CTkButton(line, text="Detail", width=60, height=28,
                                  command=lambda m=major: open_major(m)).pack(side="right", padx=4)
                ctk.CTkButton(line, text="Hapus", width=60, height=28,
                              fg_color=COLORS["danger"],
                              command=lambda n=saved["nama"]: remove_favorite(n)).pack(side="right", padx=4)
            def remove_favorite(name):
                if not self._confirm(
                    "Hapus dari favorit?",
                    f"Jurusan {name} akan dihapus dari daftar favorit."
                ):
                    return
                murid.favorite_majors = [x for x in murid.favorite_majors if x["nama"] != name]
                self._save()
                self.show_page("Minat Bakat")
                self._notify("Jurusan dihapus dari favorit.")

        elif self.mb_view == "Riwayat Tes":
            card = section_card(body, "Riwayat pengerjaan tes",
                                "Setiap tes tersimpan terpisah. Membuka riwayat tidak mengubah profil aktif.")
            if not murid.riasec_history:
                ctk.CTkLabel(card, text="Belum ada riwayat tes.",
                             text_color=COLORS["muted"]).pack(anchor="w", padx=16, pady=(0, 12))
            for index, record in reversed(list(enumerate(murid.riasec_history))):
                line = ctk.CTkFrame(card, fg_color=COLORS["surface_alt"], corner_radius=9)
                line.pack(fill="x", padx=8, pady=4)
                info = ctk.CTkFrame(line, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=10, pady=9)
                ctk.CTkLabel(info, text=f"Tes {index + 1} · {record['tanggal'][:10]}",
                             text_color=COLORS["text"], font=ctk.CTkFont(size=12, weight="bold")
                             ).pack(anchor="w")
                ctk.CTkLabel(info, text="Tipe utama: " + " · ".join(record["tiga_teratas"]),
                             text_color=COLORS["muted"]).pack(anchor="w")
                ctk.CTkButton(line, text="Lihat hasil", width=90, height=29,
                              command=lambda i=index: view_history(i)).pack(side="right", padx=8)
            if murid.riasec_history and self.mb_history_index is not None:
                index = self.mb_history_index
                if 0 <= index < len(murid.riasec_history):
                    record = murid.riasec_history[index]
                    detail = section_card(body, f"Detail riwayat · {record['tanggal'][:10]}")
                    draw_radar(detail, record["skor"])
                    score_bars(detail, record["skor"])
                    ctk.CTkLabel(detail, text="Rekomendasi saat tes: " +
                                 ", ".join(x["nama"] for x in record["rekomendasi"]),
                                 text_color=COLORS["muted"], wraplength=800,
                                 justify="left").pack(anchor="w", padx=16, pady=(0, 12))
            def view_history(index):
                self.mb_history_index = index
                self.show_page("Minat Bakat")

        def finish_test():
            if len(murid.riasec_answers) != 60 or any(str(i) not in murid.riasec_answers for i in range(60)):
                self._message("Jawaban belum lengkap", "Jawab seluruh 60 pertanyaan sebelum menyelesaikan tes.")
                return
            answers = [murid.riasec_answers[str(i)] for i in range(60)]
            from services.minat_bakat import buat_riwayat
            record = buat_riwayat(answers, katalog)
            murid.riasec_history.append(record)
            murid.profil_minat = record["skor"]
            murid.riasec_answers = {}
            self.mb_history_index = len(murid.riasec_history) - 1
            self.mb_view = "Hasil Tes"
            self._save()
            self.show_page("Minat Bakat")
            self._notify("Hasil tes RIASEC berhasil disimpan.")

        def start_new_test():
            if murid.riasec_answers and not self._confirm(
                "Mulai tes baru?",
                "Jawaban tes yang sedang berjalan akan dihapus. Hasil tes yang sudah tersimpan tetap aman."
            ):
                return
            murid.riasec_answers = {}
            self.mb_section = 0
            self._save()
            go("Tes RIASEC")

    def _portofolio_page(self):
        from models.portofolio import Portofolio, Prestasi
        self._page_header(
            "Portofolio",
            "Dokumentasikan prestasi dan pengalaman yang mendukung rencana masa depanmu."
        )
        form = self._section_card(
            self.content, "Tambah pencapaian",
            "Catat kegiatan, proyek, sertifikat, atau prestasi. Tingkat pencapaian menentukan poin portofolio."
        )
        # Susun semua komponen secara vertikal agar tinggi kartu mengikuti
        # isi form dan tidak terpotong pada resolusi layar laptop.
        fields = ctk.CTkFrame(form, fg_color="transparent")
        fields.pack(fill="x", padx=18, pady=(0, 14))

        title = ctk.CTkEntry(
            fields, placeholder_text="Nama prestasi atau kegiatan", height=38
        )
        title.pack(fill="x", pady=4)

        category = ctk.CTkEntry(
            fields, placeholder_text="Kategori, contoh: Akademik", height=38
        )
        category.pack(fill="x", pady=4)

        level = ctk.CTkOptionMenu(
            fields, values=Portofolio.TINGKAT, fg_color=COLORS["surface_alt"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"], height=38
        )
        level.pack(fill="x", pady=4)

        year = ctk.CTkEntry(
            fields, placeholder_text="Tahun, contoh: 2026", height=38
        )
        year.pack(fill="x", pady=4)

        add_button = ctk.CTkButton(
            fields, text="Tambahkan pencapaian",
            command=lambda: add_record(), height=44,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        add_button.pack(fill="x", pady=(8, 0))

        summary = ctk.CTkFrame(self.content, fg_color="transparent")
        summary.grid(row=3, column=0, sticky="ew", pady=(0, 14))
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
            if not self._confirm(
                "Hapus pencapaian?",
                f"Catatan '{record.judul}' akan dihapus dari portofolio."
            ):
                return
            self.current_student.portofolio.hapus(record)
            self._save()
            refresh()
            self._notify("Pencapaian berhasil dihapus.")

        portfolio_feedback = ctk.CTkLabel(
            fields, text="", text_color=COLORS["danger"],
            font=ctk.CTkFont(size=10), wraplength=800, justify="left"
        )
        portfolio_feedback.pack(anchor="w", pady=(5, 0))

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
                portfolio_feedback.configure(text="")
                refresh()
                self._notify("Pencapaian berhasil ditambahkan.")
            except ValueError as error:
                portfolio_feedback.configure(text=str(error), text_color=COLORS["danger"])

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
