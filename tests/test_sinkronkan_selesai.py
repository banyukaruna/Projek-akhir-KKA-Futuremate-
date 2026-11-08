"""Unit test logika sinkronisasi status selesai (tanpa window GUI).

FutureMateApp._sinkronkan_status_selesai adalah staticmethod, sehingga dapat
dipanggil langsung melalui kelas tanpa memerlukan instance Tkinter.
"""
import unittest
from datetime import date

from models.item import Tugas, PersiapanUjian, SesiBelajar
from gui.app import FutureMateApp


def _buat_item(judul, mapel, jenis="Sesi Belajar", durasi=60, selesai=False):
    if jenis == "Tugas":
        item = Tugas(judul, mapel, date(2026, 11, 10), "Sedang", durasi)
    elif jenis == "Persiapan Ujian":
        item = PersiapanUjian(judul, mapel, date(2026, 11, 10), durasi)
    else:
        item = SesiBelajar(judul, mapel, date(2026, 11, 10), durasi)
    if selesai:
        item.tandai_selesai()
    return item


class TestSinkronkanSelesai(unittest.TestCase):
    def _sinkron(self, items, jadwal):
        FutureMateApp._sinkronkan_status_selesai(items, jadwal)

    def item_selesai_mandiri_semua_sesi(self):
        """Item diceklis -> semua sesi jadwalnya jadi selesai."""
        item = _buat_item("Membaca", "Bahasa Indonesia")
        jadwal = [
            {"judul": "Membaca", "mapel": "Bahasa Indonesia", "jenis": "Sesi Belajar", "selesai": False},
            {"judul": "Membaca", "mapel": "Bahasa Indonesia", "jenis": "Sesi Belajar", "selesai": False},
        ]
        self._sinkron([item], jadwal)
        self.assertTrue(item.selesai)
        self.assertTrue(all(s["selesai"] for s in jadwal))

    def semua_sesi_selesai_maka_item_selesai(self):
        """Semua sesi selesai -> item jadi selesai (multi-c checklist)."""
        item = _buat_item("Fisika", "Fisika", durasi=120)  # 2 sesi 60 menit
        jadwal = [
            {"judul": "Fisika", "mapel": "Fisika", "jenis": "Sesi Belajar", "selesai": True},
            {"judul": "Fisika", "mapel": "Fisika", "jenis": "Sesi Belajar", "selesai": True},
        ]
        self._sinkron([item], jadwal)
        self.assertTrue(item.selesai)

    def sebagian_sesi_selesai_item_belum_selesai(self):
        """Hanya sebagian selesai -> item belum dianggap selesai."""
        item = _buat_item("Kimia", "Kimia", durasi=120)
        jadwal = [
            {"judul": "Kimia", "mapel": "Kimia", "jenis": "Sesi Belajar", "selesai": True},
            {"judul": "Kimia", "mapel": "Kimia", "jenis": "Sesi Belajar", "selesai": False},
        ]
        self._sinkron([item], jadwal)
        self.assertFalse(item.selesai)
        self.assertEqual(sum(1 for s in jadwal if s["selesai"]), 1)

    def item_tanpa_sesi_tidak_diubah(self):
        """Item yang tidak punya sesi jadwal tetap statusnya."""
        item = _buat_item("Matematika", "Matematika")
        self._sinkron([item], [])
        self.assertFalse(item.selesai)

    def jenis_berbeda_tidak_dicampur(self):
        """Kunci sinkronisasi memakai (judul, mapel, jenis)."""
        tugas = _buat_item("Laporan", "Agama", "Tugas")
        ujian = _buat_item("Laporan", "Agama", "Persiapan Ujian")
        jadwal = [
            {"judul": "Laporan", "mapel": "Agama", "jenis": "Tugas", "selesai": True},
        ]
        self._sinkron([tugas, ujian], jadwal)
        self.assertTrue(tugas.selesai)
        self.assertFalse(ujian.selesai)

    def ujian_dan_sesi_pisah(self):
        """Persiapan Ujian dan Sesi Belajar dengan judul/mapel sama dipisah."""
        ujian = _buat_item("UAS", "Matematika", "Persiapan Ujian")
        sesi = _buat_item("UAS", "Matematika", "Sesi Belajar")
        jadwal = [
            {"judul": "UAS", "mapel": "Matematika", "jenis": "Persiapan Ujian", "selesai": True},
        ]
        self._sinkron([ujian, sesi], jadwal)
        self.assertTrue(ujian.selesai)
        self.assertFalse(sesi.selesai)


if __name__ == "__main__":
    unittest.main()
