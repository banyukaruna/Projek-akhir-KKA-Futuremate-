"""Item (abstract) dan turunannya: Tugas, Ujian, SesiBelajar.
Polimorfisme: tiap jenis menghitung skor prioritas dengan caranya sendiri."""
from abc import ABC, abstractmethod
from datetime import date
from enum import Enum

from exceptions import DataTidakValidError


class LevelPrioritas(Enum):
    RENDAH = "Rendah"
    SEDANG = "Sedang"
    TINGGI = "Tinggi"
    MENDESAK = "Mendesak"


class Item(ABC):
    def __init__(self, judul, mapel, deadline):
        self.judul = judul
        self.mapel = mapel
        self.deadline = deadline
        self.__tanggal_selesai = None  # enkapsulasi: hanya diubah lewat tandai_selesai()

    @property
    def selesai(self):
        return self.__tanggal_selesai is not None

    def tandai_selesai(self, tanggal=None):
        self.__tanggal_selesai = tanggal or date.today()

    def tepat_waktu(self):
        return self.selesai and self.__tanggal_selesai <= self.deadline

    def sisa_hari(self, hari_ini=None):
        return (self.deadline - (hari_ini or date.today())).days

    def _urgensi(self, hari_ini=None):
        """0 (masih lama) sampai 10 (hari ini atau terlambat)."""
        return max(0, 10 - max(self.sisa_hari(hari_ini), 0))

    @abstractmethod
    def jenis(self):
        ...

    @abstractmethod
    def skor_prioritas(self, hari_ini=None):
        ...

    def prioritas(self, hari_ini=None):
        skor = self.skor_prioritas(hari_ini)
        if skor >= 13:
            return LevelPrioritas.MENDESAK
        if skor >= 9:
            return LevelPrioritas.TINGGI
        if skor >= 5:
            return LevelPrioritas.SEDANG
        return LevelPrioritas.RENDAH

    def to_dict(self):
        return {
            "tipe": self.jenis(), "judul": self.judul, "mapel": self.mapel,
            "deadline": self.deadline.isoformat(),
            "tanggal_selesai": self.__tanggal_selesai.isoformat() if self.selesai else None,
        }

    @staticmethod
    def dari_dict(d):
        kelas = _REGISTRI.get(d.get("tipe"))
        if kelas is None:
            raise DataTidakValidError(f"Jenis item tidak dikenal: {d.get('tipe')}")
        obj = kelas._bangun(d)
        if d.get("tanggal_selesai"):
            obj.tandai_selesai(date.fromisoformat(d["tanggal_selesai"]))
        return obj


class Tugas(Item):
    def __init__(self, judul, mapel, deadline, kesulitan=3):
        super().__init__(judul, mapel, deadline)
        if not 1 <= kesulitan <= 5:
            raise ValueError("kesulitan harus 1-5")
        self.kesulitan = kesulitan

    def jenis(self):
        return "Tugas"

    def skor_prioritas(self, hari_ini=None):
        return self._urgensi(hari_ini) + self.kesulitan

    def to_dict(self):
        return {**super().to_dict(), "kesulitan": self.kesulitan}

    @classmethod
    def _bangun(cls, d):
        return cls(d["judul"], d["mapel"], date.fromisoformat(d["deadline"]), d["kesulitan"])


class Ujian(Item):
    BONUS = 4  # ujian selalu dianggap penting

    def jenis(self):
        return "Ujian"

    def skor_prioritas(self, hari_ini=None):
        return self._urgensi(hari_ini) + self.BONUS

    @classmethod
    def _bangun(cls, d):
        return cls(d["judul"], d["mapel"], date.fromisoformat(d["deadline"]))


class SesiBelajar(Item):
    def __init__(self, judul, mapel, deadline, durasi_menit=60):
        super().__init__(judul, mapel, deadline)
        self.durasi_menit = durasi_menit

    def jenis(self):
        return "Sesi"

    def skor_prioritas(self, hari_ini=None):
        return self._urgensi(hari_ini) + min(self.durasi_menit // 60, 2)

    def to_dict(self):
        return {**super().to_dict(), "durasi_menit": self.durasi_menit}

    @classmethod
    def _bangun(cls, d):
        return cls(d["judul"], d["mapel"], date.fromisoformat(d["deadline"]), d["durasi_menit"])


_REGISTRI = {"Tugas": Tugas, "Ujian": Ujian, "Sesi": SesiBelajar}
