"""Pengguna (abstract) -> Murid, Guru, Admin."""
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date

from models.item import Item
from models.nilai import NilaiAkademik
from models.portofolio import Portofolio
from models.target import Target


class Pengguna(ABC):
    def __init__(self, nama):
        self.nama = nama

    @abstractmethod
    def peran(self):
        ...

    @abstractmethod
    def hak_akses(self):
        ...


class Murid(Pengguna):
    def __init__(self, nama, kelas):
        super().__init__(nama)
        self.kelas = kelas
        self.nilai = NilaiAkademik()
        self.portofolio = Portofolio()
        self.items = []
        self.targets = []
        self.profil_minat = {}
        self.riasec_history = []
        self.riasec_answers = {}
        self.favorite_majors = []
        self.jadwal = []
        self.preferensi_jadwal = {
            "hari": [0, 1, 2, 3, 4],
            "mulai": "16:00",
            "selesai": "18:00",
        }

    def peran(self):
        return "Murid"

    def hak_akses(self):
        return ["kelola tugas", "input nilai", "kelola target", "tes minat", "portofolio"]

    def tambah_item(self, item):
        self.items.append(item)

    def tambah_target(self, target):
        self.targets.append(target)

    def item_aktif(self, hari_ini=None):
        aktif = [i for i in self.items if not i.selesai]
        return sorted(aktif, key=lambda i: i.skor_prioritas(hari_ini), reverse=True)

    def hari_padat(self, batas=3, hari_ini=None):
        """Hari mendatang dengan >= batas deadline sekaligus."""
        hari_ini = hari_ini or date.today()
        per_hari = defaultdict(list)
        for i in self.item_aktif(hari_ini):
            if i.deadline >= hari_ini:
                per_hari[i.deadline].append(i)
        return {h: v for h, v in sorted(per_hari.items()) if len(v) >= batas}

    def to_dict(self):
        return {
            "nama": self.nama, "kelas": self.kelas, "nilai": self.nilai.to_dict(),
            "items": [i.to_dict() for i in self.items],
            "targets": [t.to_dict() for t in self.targets],
            "portofolio": self.portofolio.to_dict(), "profil_minat": self.profil_minat,
            "riasec_history": self.riasec_history,
            "riasec_answers": self.riasec_answers,
            "favorite_majors": self.favorite_majors,
            "jadwal": self.jadwal,
            "preferensi_jadwal": self.preferensi_jadwal,
        }

    @classmethod
    def dari_dict(cls, d):
        m = cls(d["nama"], d["kelas"])
        m.nilai = NilaiAkademik.dari_dict(d["nilai"])
        m.items = [Item.dari_dict(x) for x in d["items"]]
        m.targets = [Target.dari_dict(x) for x in d["targets"]]
        m.portofolio = Portofolio.dari_dict(d["portofolio"])
        m.profil_minat = d.get("profil_minat", {})
        m.riasec_history = d.get("riasec_history", [])
        m.riasec_answers = d.get("riasec_answers", {})
        m.favorite_majors = d.get("favorite_majors", [])
        m.jadwal = d.get("jadwal", [])
        m.preferensi_jadwal = d.get("preferensi_jadwal", {
            "hari": [0, 1, 2, 3, 4], "mulai": "16:00", "selesai": "18:00"
        })
        return m


class Guru(Pengguna):
    def peran(self):
        return "Guru"

    def hak_akses(self):
        return ["lihat ringkasan kesiapan semua murid"]


class Admin(Pengguna):
    def peran(self):
        return "Admin"

    def hak_akses(self):
        return ["kelola katalog jurusan", "kelola data murid"]
