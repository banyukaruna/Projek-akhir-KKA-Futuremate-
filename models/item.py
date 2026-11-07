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
    def __init__(self, judul, mapel, deadline, durasi_menit=60):
        durasi_menit = int(durasi_menit)
        if not 15 <= durasi_menit <= 480:
            raise ValueError("Durasi kegiatan harus 15 sampai 480 menit.")
        self.judul = judul
        self.mapel = mapel
        self.deadline = deadline
        self.durasi_menit = durasi_menit
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
            "durasi_menit": self.durasi_menit,
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
    BOBOT_KESULITAN = {"Mudah": 1, "Sedang": 3, "Sulit": 5}

    def __init__(self, judul, mapel, deadline, kesulitan="Sedang", durasi_menit=60):
        super().__init__(judul, mapel, deadline, durasi_menit)
        if isinstance(kesulitan, int):
            if not 1 <= kesulitan <= 5:
                raise ValueError("Kesulitan harus Mudah, Sedang, atau Sulit.")
            kesulitan = (
                "Mudah" if kesulitan <= 2
                else "Sedang" if kesulitan == 3
                else "Sulit"
            )
        if isinstance(kesulitan, str):
            kesulitan = kesulitan.strip().capitalize()
        if kesulitan not in self.BOBOT_KESULITAN:
            raise ValueError("Kesulitan harus Mudah, Sedang, atau Sulit.")
        self.kesulitan = kesulitan

    def jenis(self):
        return "Tugas"

    def skor_prioritas(self, hari_ini=None):
        bobot = self.BOBOT_KESULITAN[self.kesulitan]
        return self._urgensi(hari_ini) + bobot

    def to_dict(self):
        return {**super().to_dict(), "kesulitan": self.kesulitan}

    @classmethod
    def _bangun(cls, d):
        return cls(
            d["judul"], d["mapel"], date.fromisoformat(d["deadline"]),
            d.get("kesulitan", 3), d.get("durasi_menit", 60)
        )


class Ujian(Item):
    BONUS = 4  # ujian selalu dianggap penting

    def __init__(self, judul, mapel, deadline, durasi_menit=60):
        super().__init__(judul, mapel, deadline, durasi_menit)

    def jenis(self):
        return "Ujian"

    def skor_prioritas(self, hari_ini=None):
        return self._urgensi(hari_ini) + self.BONUS

    @classmethod
    def _bangun(cls, d):
        return cls(
            d["judul"], d["mapel"], date.fromisoformat(d["deadline"]),
            d.get("durasi_menit", 60)
        )


class SesiBelajar(Item):
    def __init__(self, judul, mapel, deadline, durasi_menit=60):
        super().__init__(judul, mapel, deadline, durasi_menit)

    def jenis(self):
        return "Sesi"

    def skor_prioritas(self, hari_ini=None):
        return self._urgensi(hari_ini) + min(self.durasi_menit // 60, 2)

    @classmethod
    def _bangun(cls, d):
        return cls(
            d["judul"], d["mapel"], date.fromisoformat(d["deadline"]),
            d.get("durasi_menit", 60)
        )


_REGISTRI = {"Tugas": Tugas, "Ujian": Ujian, "Sesi": SesiBelajar}
