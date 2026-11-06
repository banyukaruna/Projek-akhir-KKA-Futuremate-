"""Model pencatatan nilai rapor per semester."""
from exceptions import NilaiTidakValidError


class NilaiAkademik:
    JUMLAH_SEMESTER = 5

    def __init__(self):
        # Riwayat nilai lama tetap disimpan untuk kompatibilitas.
        self.__data = {}
        # Format rapor: {semester: {mata_pelajaran: nilai}}
        self.__rapor = {}
        self.__target_akhir = None

    def tambah(self, mapel, nilai):
        """Menyimpan riwayat nilai lama."""
        nilai = float(nilai)
        if not 0 <= nilai <= 100:
            raise NilaiTidakValidError("Nilai harus di antara 0 dan 100.")
        nama = mapel.strip().title()
        if not nama:
            raise ValueError("Nama mata pelajaran wajib diisi.")
        self.__data.setdefault(nama, []).append(nilai)

    def daftar_mapel(self):
        nama = set(self.__data)
        for daftar in self.__rapor.values():
            nama.update(daftar)
        return sorted(nama)

    def rata_mapel(self, mapel):
        nilai = self.__data.get(mapel.strip().title())
        return sum(nilai) / len(nilai) if nilai else None

    def rata_rata(self):
        """Rata-rata rapor jika tersedia, atau rata-rata data lama."""
        if self.__rapor:
            return self.rata_akhir()
        rata = [self.rata_mapel(m) for m in self.__data]
        return sum(rata) / len(rata) if rata else 0.0

    def tren(self, mapel):
        nilai = self.__data.get(mapel.strip().title(), [])
        if len(nilai) < 2:
            return "belum cukup data"
        selisih = nilai[-1] - sum(nilai[:-1]) / len(nilai[:-1])
        if selisih > 2:
            return "naik"
        if selisih < -2:
            return "turun"
        return "stabil"

    def data_semester(self, semester):
        return dict(self.__rapor.get(int(semester), {}))

    def tambah_nilai_rapor(self, semester, mapel, nilai):
        semester = int(semester)
        nilai = float(nilai)
        nama = mapel.strip().title()
        if semester < 1 or semester > self.JUMLAH_SEMESTER:
            raise ValueError("Semester harus berada pada rentang 1 sampai 5.")
        if not nama:
            raise ValueError("Nama mata pelajaran wajib diisi.")
        if not 0 <= nilai <= 100:
            raise NilaiTidakValidError("Nilai harus di antara 0 dan 100.")
        self.__rapor.setdefault(semester, {})[nama] = nilai

    def hapus_nilai_rapor(self, semester, mapel):
        semester = int(semester)
        nama = mapel.strip().title()
        daftar = self.__rapor.get(semester, {})
        if nama in daftar:
            del daftar[nama]
        if not daftar:
            self.__rapor.pop(semester, None)

    def rata_semester(self, semester):
        daftar = self.__rapor.get(int(semester), {})
        return sum(daftar.values()) / len(daftar) if daftar else None

    def semester_terisi(self):
        return sorted(
            semester for semester, daftar in self.__rapor.items() if daftar
        )

    def rata_akhir(self):
        """Rata-rata dari rerata semester yang sudah memiliki data."""
        rata = [
            self.rata_semester(semester)
            for semester in self.semester_terisi()
        ]
        return sum(rata) / len(rata) if rata else 0.0

    def set_target_akhir(self, target):
        target = float(target)
        if not 0 <= target <= 100:
            raise ValueError("Target harus berada pada rentang 0 sampai 100.")
        self.__target_akhir = target

    def target_akhir(self):
        return self.__target_akhir

    def kebutuhan_semester_berikutnya(self):
        """Rerata rata-rata yang dibutuhkan pada setiap semester tersisa."""
        if self.__target_akhir is None:
            return None
        terisi = self.semester_terisi()
        if not terisi:
            return self.__target_akhir
        jumlah_sisa = self.JUMLAH_SEMESTER - len(terisi)
        if jumlah_sisa <= 0:
            return None
        jumlah_rerata = sum(self.rata_semester(s) for s in terisi)
        return (self.__target_akhir * self.JUMLAH_SEMESTER - jumlah_rerata) / jumlah_sisa

    def to_dict(self):
        return {
            "_format": 2,
            "riwayat_lama": {m: list(v) for m, v in self.__data.items()},
            "rapor": {
                str(s): dict(daftar) for s, daftar in self.__rapor.items()
            },
            "target_akhir": self.__target_akhir,
        }

    @classmethod
    def dari_dict(cls, data):
        obj = cls()
        if data.get("_format") == 2:
            obj.__data = {
                m: [float(n) for n in daftar]
                for m, daftar in data.get("riwayat_lama", {}).items()
            }
            obj.__rapor = {
                int(s): {m: float(n) for m, n in daftar.items()}
                for s, daftar in data.get("rapor", {}).items()
            }
            target = data.get("target_akhir")
            obj.__target_akhir = float(target) if target is not None else None
        else:
            # Data dari versi lama tidak dihapus atau dianggap sebagai nilai rapor.
            obj.__data = {
                m: [float(n) for n in daftar]
                for m, daftar in data.items()
            }
        return obj
