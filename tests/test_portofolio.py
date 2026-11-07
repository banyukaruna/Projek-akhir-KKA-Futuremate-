import unittest

from models.portofolio import Portofolio, Prestasi


class PortofolioTests(unittest.TestCase):
    def setUp(self):
        self.portofolio = Portofolio()

    def test_tingkat_pencapaian_tersedia_untuk_dropdown(self):
        self.assertEqual(
            ["Sekolah", "Kota", "Provinsi", "Nasional", "Internasional"],
            Portofolio.TINGKAT,
        )

    def test_tambah_pencapaian_memperbarui_jumlah_dan_poin(self):
        sekolah = Prestasi("Juara kelas", "Akademik", "Sekolah", 2026)
        nasional = Prestasi("Lomba nasional", "Kompetisi", "Nasional", 2026)

        self.portofolio.tambah(sekolah)
        self.portofolio.tambah(nasional)

        self.assertEqual(2, self.portofolio.jumlah())
        self.assertEqual(5, self.portofolio.total_poin())
        self.assertEqual([sekolah, nasional], self.portofolio.daftar())

    def test_hapus_pencapaian_memperbarui_jumlah_dan_poin(self):
        sekolah = Prestasi("Juara kelas", "Akademik", "Sekolah", 2026)
        nasional = Prestasi("Lomba nasional", "Kompetisi", "Nasional", 2026)
        self.portofolio.tambah(sekolah)
        self.portofolio.tambah(nasional)

        berhasil = self.portofolio.hapus(sekolah)

        self.assertTrue(berhasil)
        self.assertEqual(1, self.portofolio.jumlah())
        self.assertEqual(4, self.portofolio.total_poin())
        self.assertEqual([nasional], self.portofolio.daftar())

    def test_hapus_data_yang_tidak_ada_tidak_mengubah_portofolio(self):
        pencapaian = Prestasi("Juara kelas", "Akademik", "Sekolah", 2026)

        berhasil = self.portofolio.hapus(pencapaian)

        self.assertFalse(berhasil)
        self.assertEqual(0, self.portofolio.jumlah())
        self.assertEqual(0, self.portofolio.total_poin())

    def test_data_portofolio_bisa_disimpan_dan_dimuat_kembali(self):
        self.portofolio.tambah(
            Prestasi("Proyek aplikasi", "Proyek", "Provinsi", 2026)
        )
        data = self.portofolio.to_dict()

        hasil_muat = Portofolio.dari_dict(data)

        self.assertEqual(1, hasil_muat.jumlah())
        self.assertEqual(3, hasil_muat.total_poin())
        self.assertEqual("Proyek aplikasi", hasil_muat.daftar()[0].judul)


if __name__ == "__main__":
    unittest.main()
