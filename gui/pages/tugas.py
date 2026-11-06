"""Halaman untuk mengelola tugas, ujian, dan sesi belajar."""
from datetime import date
import customtkinter as ctk

from models.item import Tugas, Ujian, SesiBelajar


class TugasPage(ctk.CTkFrame):
    def __init__(self, master, murid, on_change, colors):
        super().__init__(master, fg_color="transparent")
        self.murid = murid
        self.on_change = on_change
        self.colors = colors
        self._build()
        self._refresh_list()

    def _label(self, parent, text, **kwargs):
        return ctk.CTkLabel(parent, text=text, text_color=self.colors["text"], **kwargs)

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._label(self, "Tugas & Jadwal",
                    font=ctk.CTkFont(size=27, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            self, text="Catat tugas, ujian, dan sesi belajar agar tenggat waktumu terpantau.",
            text_color=self.colors["muted"], font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w", pady=(5, 18))

        form = ctk.CTkFrame(self, fg_color=self.colors["surface"], corner_radius=14)
        form.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        form.grid_columnconfigure((0, 1), weight=1)

        self.title_entry = ctk.CTkEntry(form, placeholder_text="Nama tugas atau kegiatan", height=38)
        self.title_entry.grid(row=0, column=0, padx=(16, 8), pady=(16, 8), sticky="ew")
        self.subject_entry = ctk.CTkEntry(form, placeholder_text="Mata pelajaran", height=38)
        self.subject_entry.grid(row=0, column=1, padx=(8, 16), pady=(16, 8), sticky="ew")

        self.date_entry = ctk.CTkEntry(form, placeholder_text="Tenggat: YYYY-MM-DD", height=38)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=0, padx=(16, 8), pady=8, sticky="ew")

        self.type_menu = ctk.CTkOptionMenu(
            form, values=["Tugas", "Ujian", "Sesi Belajar"],
            fg_color=self.colors["surface_alt"], button_color=self.colors["primary"],
            button_hover_color=self.colors["primary_hover"], text_color=self.colors["text"]
        )
        self.type_menu.grid(row=1, column=1, padx=(8, 16), pady=8, sticky="ew")

        self.difficulty_menu = ctk.CTkOptionMenu(
            form, values=["1", "2", "3", "4", "5"],
            fg_color=self.colors["surface_alt"], button_color=self.colors["primary"],
            button_hover_color=self.colors["primary_hover"], text_color=self.colors["text"]
        )
        self.difficulty_menu.set("3")
        self.difficulty_menu.grid(row=2, column=0, padx=(16, 8), pady=(8, 4), sticky="ew")

        ctk.CTkButton(
            form, text="Tambah kegiatan", height=38, command=self._add_item,
            fg_color=self.colors["primary"], hover_color=self.colors["primary_hover"],
            text_color="#071923"
        ).grid(row=2, column=1, padx=(8, 16), pady=(8, 4), sticky="ew")

        ctk.CTkLabel(
            form, text="Tingkat kesulitan berlaku untuk jenis Tugas. Gunakan tanggal YYYY-MM-DD.",
            text_color=self.colors["muted"], font=ctk.CTkFont(size=10)
        ).grid(row=3, column=0, columnspan=2, padx=16, pady=(4, 14), sticky="w")

        list_panel = ctk.CTkFrame(self, fg_color=self.colors["surface"], corner_radius=14)
        list_panel.grid(row=3, column=0, sticky="nsew")
        list_panel.grid_columnconfigure(0, weight=1)
        list_panel.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(list_panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(15, 8))
        self._label(header, "Daftar kegiatan", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        self.count_label = ctk.CTkLabel(header, text="", text_color=self.colors["muted"])
        self.count_label.pack(side="right")

        self.items_frame = ctk.CTkScrollableFrame(
            list_panel, fg_color="transparent", corner_radius=0
        )
        self.items_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

    def _show_message(self, message):
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title("FutureMate")
        dialog.geometry("380x150")
        dialog.transient(self.winfo_toplevel())
        ctk.CTkLabel(
            dialog, text=message, text_color=self.colors["text"],
            wraplength=320, justify="left"
        ).pack(padx=24, pady=24)
        ctk.CTkButton(
            dialog, text="Tutup", command=dialog.destroy,
            fg_color=self.colors["primary"], text_color="#071923"
        ).pack()

    def _add_item(self):
        title = self.title_entry.get().strip()
        subject = self.subject_entry.get().strip()
        raw_date = self.date_entry.get().strip()

        if not title or not subject or not raw_date:
            self._show_message("Nama kegiatan, mata pelajaran, dan tenggat wajib diisi.")
            return

        try:
            deadline = date.fromisoformat(raw_date)
            kind = self.type_menu.get()
            if kind == "Tugas":
                item = Tugas(title, subject, deadline, int(self.difficulty_menu.get()))
            elif kind == "Ujian":
                item = Ujian(title, subject, deadline)
            else:
                item = SesiBelajar(title, subject, deadline)
            self.murid.tambah_item(item)
            self.on_change()
            self.title_entry.delete(0, "end")
            self.subject_entry.delete(0, "end")
            self._refresh_list()
        except ValueError:
            self._show_message("Tanggal harus menggunakan format YYYY-MM-DD, misalnya 2026-11-20.")

    def _refresh_list(self):
        for child in self.items_frame.winfo_children():
            child.destroy()

        active = self.murid.item_aktif()
        completed = [item for item in self.murid.items if item.selesai]
        self.count_label.configure(text=f"{len(active)} aktif · {len(completed)} selesai")

        if not self.murid.items:
            ctk.CTkLabel(
                self.items_frame, text="Belum ada kegiatan. Tambahkan melalui formulir di atas.",
                text_color=self.colors["muted"]
            ).pack(anchor="w", padx=8, pady=12)
            return

        ordered = active + completed
        for item in ordered:
            row = ctk.CTkFrame(self.items_frame, fg_color=self.colors["surface_alt"], corner_radius=10)
            row.pack(fill="x", padx=4, pady=5)
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=12, pady=9)

            status = "Selesai" if item.selesai else item.prioritas().value
            self._label(
                info, f"{item.judul}  ·  {item.jenis()}",
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(anchor="w")
            ctk.CTkLabel(
                info, text=f"{item.mapel}  |  Tenggat {item.deadline:%d-%m-%Y}  |  {status}",
                text_color=self.colors["muted"], font=ctk.CTkFont(size=10)
            ).pack(anchor="w", pady=(3, 0))

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(side="right", padx=8)
            if not item.selesai:
                ctk.CTkButton(
                    actions, text="Selesai", width=72, height=30,
                    fg_color=self.colors["primary"], hover_color=self.colors["primary_hover"],
                    text_color="#071923",
                    command=lambda current=item: self._complete(current)
                ).pack(side="left", padx=3)
            ctk.CTkButton(
                actions, text="Hapus", width=62, height=30,
                fg_color=self.colors["danger"], hover_color="#c95d5d",
                command=lambda current=item: self._delete(current)
            ).pack(side="left", padx=3)

    def _complete(self, item):
        item.tandai_selesai()
        self.on_change()
        self._refresh_list()

    def _delete(self, item):
        self.murid.items.remove(item)
        self.on_change()
        self._refresh_list()
