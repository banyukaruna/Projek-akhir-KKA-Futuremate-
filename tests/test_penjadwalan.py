import unittest
from datetime import date

from models.item import SesiBelajar, Tugas, Ujian
from services.penjadwalan import Penjadwalan


class PenjadwalanTests(unittest.TestCase):
    HARI_INI = date(2024, 1, 1)  # Senin
    DEADLINE = date(2024, 1, 7)

    def buat(self, item):
        return Penjadwalan.buat_jadwal(
            [item], [0], "16:00", "20:00", hari_ini=self.HARI_INI
        )

    def test_sesi_menggunakan_durasi_penuh_dibagi_maksimal_60_menit(self):
        item = SesiBelajar("Belajar Fisika", "Fisika", self.DEADLINE, 90)

        jadwal = self.buat(item)

        self.assertEqual([60, 30], [sesi["durasi"] for sesi in jadwal])
        self.assertEqual(90, sum(sesi["durasi"] for sesi in jadwal))

    def test_sesi_60_menit_dijadwalkan_sebagai_satu_sesi(self):
        item = SesiBelajar("Belajar Kimia", "Kimia", self.DEADLINE, 60)

        jadwal = self.buat(item)

        self.assertEqual([60], [sesi["durasi"] for sesi in jadwal])

    def test_tugas_dan_ujian_menggunakan_durasi_yang_diisi(self):
        tugas = Tugas("PR", "Matematika", self.DEADLINE, 3, 90)
        ujian = Ujian("UTS", "Bahasa Indonesia", self.DEADLINE, 120)

        jadwal_tugas = self.buat(tugas)
        jadwal_ujian = self.buat(ujian)

        self.assertEqual([60, 30], [sesi["durasi"] for sesi in jadwal_tugas])
        self.assertEqual([60, 60], [sesi["durasi"] for sesi in jadwal_ujian])

    def test_durasi_default_tugas_dan_ujian_tetap_60_menit(self):
        tugas = Tugas("PR", "Matematika", self.DEADLINE)
        ujian = Ujian("UTS", "Bahasa Indonesia", self.DEADLINE)

        self.assertEqual(60, tugas.durasi_menit)
        self.assertEqual(60, ujian.durasi_menit)

    def test_data_lama_tanpa_durasi_tetap_bisa_dimuat(self):
        data_tugas = {
            "tipe": "Tugas", "judul": "PR", "mapel": "Matematika",
            "deadline": self.DEADLINE.isoformat(), "kesulitan": 3,
            "tanggal_selesai": None,
        }
        data_ujian = {
            "tipe": "Ujian", "judul": "UTS", "mapel": "Bahasa Indonesia",
            "deadline": self.DEADLINE.isoformat(), "tanggal_selesai": None,
        }

        self.assertEqual(60, Tugas._bangun(data_tugas).durasi_menit)
        self.assertEqual(60, Ujian._bangun(data_ujian).durasi_menit)

    def test_durasi_di_luar_rentang_ditolak_untuk_semua_jenis(self):
        items = [
            Tugas("PR", "Matematika", self.DEADLINE, 3, 500),
            Ujian("UTS", "Bahasa Indonesia", self.DEADLINE, 500),
            SesiBelajar("Belajar", "Fisika", self.DEADLINE, 500),
        ]
        for item in items:
            with self.subTest(jenis=item.jenis()):
                with self.assertRaisesRegex(ValueError, "15 sampai 480"):
                    self.buat(item)


if __name__ == "__main__":
    unittest.main()
