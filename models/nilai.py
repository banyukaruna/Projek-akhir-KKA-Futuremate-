"""Modul nilai: menyimpan riwayat nilai per mapel, rata-rata, dan tren."""
from exceptions import NilaiTidakValidError


class NilaiAkademik:
    def __init__(self):
        self.__data = {}  # enkapsulasi: {mapel: [nilai, ...]}

    def tambah(self, mapel, nilai):
        if not 0 <= nilai <= 100:
            raise NilaiTidakValidError("Nilai harus di antara 0 dan 100.")
        self.__data.setdefault(mapel.strip().title(), []).append(float(nilai))

    def daftar_mapel(self):
        return sorted(self.__data)

    def rata_mapel(self, mapel):
        nilai = self.__data.get(mapel.strip().title())
        return sum(nilai) / len(nilai) if nilai else None

    def rata_rata(self):
        """Rata-rata dari rata-rata tiap mapel (0 jika belum ada data)."""
        rata = [self.rata_mapel(m) for m in self.__data]
        return sum(rata) / len(rata) if rata else 0.0

    def tren(self, mapel):
        """Bandingkan nilai terbaru dengan rata-rata nilai sebelumnya."""
        nilai = self.__data.get(mapel.strip().title(), [])
        if len(nilai) < 2:
            return "belum cukup data"
        selisih = nilai[-1] - sum(nilai[:-1]) / len(nilai[:-1])
        if selisih > 2:
            return "naik"
        if selisih < -2:
            return "turun"
        return "stabil"

    def to_dict(self):
        return {m: list(v) for m, v in self.__data.items()}

    @classmethod
    def dari_dict(cls, data):
        obj = cls()
        for mapel, daftar in data.items():
            for n in daftar:
                obj.tambah(mapel, n)
        return obj
