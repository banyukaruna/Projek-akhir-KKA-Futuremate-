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

    def test_id_item_tetap_sama_setelah_serialisasi(self):
        item = Tugas("PR", "Matematika", self.DEADLINE, 3, 90)
        item_muat = Tugas._bangun(item.to_dict())
        self.assertEqual(item.id, item_muat.id)

    def test_sesi_manual_dipertahankan_dan_sisa_durasi_dijadwalkan(self):
        item = Tugas("PR", "Matematika", self.DEADLINE, 3, 120)
        manual = {
            "id": "manual-1", "item_id": item.id,
            "judul": item.judul, "mapel": item.mapel, "jenis": item.jenis(),
            "tanggal": self.HARI_INI.isoformat(), "mulai": "16:00",
            "durasi": 60, "manual": True, "selesai": False,
        }
        jadwal = Penjadwalan.buat_jadwal(
            [item], [0], "16:00", "20:00",
            hari_ini=self.HARI_INI, sesi_manual=[manual]
        )
        self.assertIn("manual-1", [sesi["id"] for sesi in jadwal])
        self.assertEqual(120, sum(sesi["durasi"] for sesi in jadwal))

    def test_sesi_selesai_tetap_dipertahankan(self):
        sesi = {
            "id": "selesai-1", "item_id": "item-lama",
            "judul": "PR", "mapel": "Matematika", "jenis": "Tugas",
            "tanggal": self.HARI_INI.isoformat(), "mulai": "16:00",
            "durasi": 60, "manual": False, "selesai": True,
        }
        jadwal = Penjadwalan.buat_jadwal(
            [], [0], "16:00", "20:00",
            hari_ini=self.HARI_INI, sesi_manual=[sesi]
        )
        self.assertEqual("selesai-1", jadwal[0]["id"])
        self.assertTrue(jadwal[0]["selesai"])

    def test_validasi_menolak_sesi_yang_bentrok(self):
        pertama = {"tanggal": "2024-01-01", "mulai": "16:00", "durasi": 60}
        kedua = {"tanggal": "2024-01-01", "mulai": "17:00", "durasi": 30}
        with self.assertRaisesRegex(ValueError, "bertabrakan"):
            Penjadwalan.validasi_bentrok(
                kedua, "2024-01-01", "16:30", 30, [pertama, kedua]
            )

    def test_durasi_di_luar_rentang_ditolak_untuk_semua_jenis(self):
        pembuat_item = [
            lambda: Tugas("PR", "Matematika", self.DEADLINE, 3, 500),
            lambda: Ujian("UTS", "Bahasa Indonesia", self.DEADLINE, 500),
            lambda: SesiBelajar("Belajar", "Fisika", self.DEADLINE, 500),
        ]
        for buat_item in pembuat_item:
            with self.subTest(pembuat_item=buat_item):
                with self.assertRaisesRegex(ValueError, "15 sampai 480"):
                    buat_item()


if __name__ == "__main__":
    unittest.main()
