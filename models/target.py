"""Target masa depan (abstract): Jurusan, Beasiswa, Lomba.
Strategy sederhana: tiap jenis punya cara cek_syarat() sendiri."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from exceptions import DataTidakValidError


@dataclass
class Syarat:
    deskripsi: str
    terpenuhi: bool
    selisih: float = 0.0


def _cek_min(label, minimal, aktual):
    if aktual is None:
        return Syarat(f"{label} minimal {minimal:g} (kamu: belum ada nilai)", False, float(minimal))
    selisih = max(0.0, minimal - aktual)
    return Syarat(f"{label} minimal {minimal:g} (kamu: {aktual:.1f})", selisih == 0, selisih)


class Target(ABC):
    def __init__(self, nama, deadline=None):
        self.nama = nama
        self.deadline = deadline

    @abstractmethod
    def jenis(self):
        ...

    @abstractmethod
    def cek_syarat(self, murid):
        """Mengembalikan list[Syarat]."""

    def kecocokan(self, murid):
        """Fraksi syarat yang terpenuhi (0.0 - 1.0)."""
        syarat = self.cek_syarat(murid)
        return sum(s.terpenuhi for s in syarat) / len(syarat) if syarat else 1.0

    def to_dict(self):
        return {"tipe": self.jenis(), "nama": self.nama,
                "deadline": self.deadline.isoformat() if self.deadline else None}

    @staticmethod
    def dari_dict(d):
        kelas = _REGISTRI.get(d.get("tipe"))
        if kelas is None:
            raise DataTidakValidError(f"Jenis target tidak dikenal: {d.get('tipe')}")
        return kelas._bangun(d)


def _tgl(d):
    return date.fromisoformat(d["deadline"]) if d.get("deadline") else None


class Jurusan(Target):
    def __init__(self, nama, kampus, rata_min, syarat_mapel, riasec):
        super().__init__(f"{nama} - {kampus}")
        self.nama_jurusan, self.kampus = nama, kampus
        self.rata_min, self.syarat_mapel, self.riasec = rata_min, syarat_mapel, riasec

    def jenis(self):
        return "Jurusan"

    def cek_syarat(self, murid):
        hasil = [_cek_min("Rata-rata", self.rata_min, murid.nilai.rata_rata() or None)]
        for mapel, minimal in self.syarat_mapel.items():
            hasil.append(_cek_min(mapel, minimal, murid.nilai.rata_mapel(mapel)))
        return hasil

    def to_dict(self):
        return {**super().to_dict(), "nama_jurusan": self.nama_jurusan, "kampus": self.kampus,
                "rata_min": self.rata_min, "syarat_mapel": self.syarat_mapel, "riasec": self.riasec}

    @classmethod
    def _bangun(cls, d):
        return cls(d["nama_jurusan"], d["kampus"], d["rata_min"], d["syarat_mapel"], d["riasec"])


class Beasiswa(Target):
    def __init__(self, nama, deadline, rata_min, min_prestasi):
        super().__init__(nama, deadline)
        self.rata_min, self.min_prestasi = rata_min, min_prestasi

    def jenis(self):
        return "Beasiswa"

    def cek_syarat(self, murid):
        jml = murid.portofolio.jumlah()
        return [
            _cek_min("Rata-rata", self.rata_min, murid.nilai.rata_rata() or None),
            Syarat(f"Prestasi minimal {self.min_prestasi} (kamu: {jml})",
                   jml >= self.min_prestasi, max(0, self.min_prestasi - jml)),
        ]

    def to_dict(self):
        return {**super().to_dict(), "rata_min": self.rata_min, "min_prestasi": self.min_prestasi}

    @classmethod
    def _bangun(cls, d):
        return cls(d["nama"], _tgl(d), d["rata_min"], d["min_prestasi"])


class Lomba(Target):
    def __init__(self, nama, deadline, mapel, nilai_min):
        super().__init__(nama, deadline)
        self.mapel, self.nilai_min = mapel, nilai_min

    def jenis(self):
        return "Lomba"

    def cek_syarat(self, murid):
        return [_cek_min(self.mapel, self.nilai_min, murid.nilai.rata_mapel(self.mapel))]

    def to_dict(self):
        return {**super().to_dict(), "mapel": self.mapel, "nilai_min": self.nilai_min}

    @classmethod
    def _bangun(cls, d):
        return cls(d["nama"], _tgl(d), d["mapel"], d["nilai_min"])


_REGISTRI = {"Jurusan": Jurusan, "Beasiswa": Beasiswa, "Lomba": Lomba}
