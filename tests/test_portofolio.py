import unittest

from models.portofolio import (
    PortofolioAkademik,
    PrestasiAkademik,
    TINGKAT_OPSI,
    JUARA_OPSI,
    PENYELENGGARA_OPSI,
    JENJANG_OPSI,
    KEPESERTAAN_OPSI,
)


class PortofolioAkademikTests(unittest.TestCase):
    def setUp(self):
        self.portofolio = PortofolioAkademik()

    def buat_prestasi(self, judul="OSN Matematika", tingkat="Nasional",
                      juara="Juara 1", **kwargs):
        kwargs.setdefault("tahun", 2026)
        return PrestasiAkademik(judul, tingkat, juara, **kwargs)

    def test_semua_opsi_form_tersedia(self):
        self.assertEqual(
            ["Internasional", "Nasional", "Provinsi", "Kabupaten / Kota"],
            TINGKAT_OPSI,
        )
        self.assertIn("Juara 1", JUARA_OPSI)
        self.assertIn("Peserta / Panitia", JUARA_OPSI)
        self.assertEqual(3, len(PENYELENGGARA_OPSI))
        self.assertEqual(["Berjenjang", "Non-Berjenjang"], JENJANG_OPSI)
        self.assertEqual(["Individual", "Beregu"], KEPESERTAAN_OPSI)

    def test_skor_dasar_sesuai_matriks(self):
        expected = {
            ("Internasional", "Juara 1"): 100,
            ("Nasional", "Juara 2"): 65,
            ("Provinsi", "Juara 3"): 30,
            ("Kabupaten / Kota", "Juara Harapan / Finalis"): 10,
        }
        for (tingkat, juara), skor in expected.items():
            with self.subTest(tingkat=tingkat, juara=juara):
                self.assertEqual(skor, self.buat_prestasi(
                    tingkat=tingkat, juara=juara
                ).skor_dasar)

    def test_perhitungan_poin_individual(self):
        prestasi = self.buat_prestasi(
            penyelenggara="PTN / PTS / Induk Organisasi Resmi",
            jenis_kepesertaan="Individual",
            jenjang_lomba="Non-Berjenjang",
        )
        self.assertAlmostEqual(54.19, prestasi.poin)

    def test_perhitungan_poin_beregu_default(self):
        prestasi = self.buat_prestasi(
            jenis_kepesertaan="Beregu",
            penyelenggara="Kementerian / Lembaga Negara",
        )
        self.assertAlmostEqual(60.0, prestasi.poin)
        self.assertEqual(0.80, prestasi.faktor_kepesertaan)

    def test_perhitungan_poin_beregu_custom(self):
        prestasi = self.buat_prestasi(
            jenis_kepesertaan="Beregu", bobot_beregu=0.75
        )
        self.assertAlmostEqual(56.25, prestasi.poin)

    def test_peserta_tidak_mendapat_poin(self):
        prestasi = self.buat_prestasi(juara="Peserta / Panitia")
        self.assertEqual(0, prestasi.skor_dasar)
        self.assertEqual(0.0, prestasi.poin)

    def test_tambah_prestasi_memperbarui_jumlah_dan_poin(self):
        p1 = self.buat_prestasi()
        p2 = self.buat_prestasi(
            "Lomba Sains", "Provinsi", "Juara 2",
            penyelenggara="PTN / PTS / Induk Organisasi Resmi",
        )
        self.portofolio.tambah(p1)
        self.portofolio.tambah(p2)
        self.assertEqual(2, self.portofolio.jumlah())
        self.assertAlmostEqual(109.0, self.portofolio.total_poin(hanya_terbaik=False))
        self.assertEqual([p1, p2], self.portofolio.daftar())

    def test_tipe_data_tambah_harus_prestasi_akademik(self):
        with self.assertRaises(TypeError):
            self.portofolio.tambah("bukan prestasi")

    def test_hapus_prestasi(self):
        p1 = self.buat_prestasi()
        p2 = self.buat_prestasi("Lomba Provinsi", "Provinsi", "Juara 2")
        self.portofolio.tambah(p1)
        self.portofolio.tambah(p2)
        self.assertTrue(self.portofolio.hapus(p1))
        self.assertEqual([p2], self.portofolio.daftar())

    def test_hapus_data_yang_tidak_ada(self):
        self.assertFalse(self.portofolio.hapus(self.buat_prestasi()))
        self.assertEqual(0, self.portofolio.jumlah())

    def test_daftar_terbaik_mengambil_tiga_poin_tertinggi(self):
        for tingkat in ("Kabupaten / Kota", "Provinsi", "Nasional", "Internasional"):
            self.portofolio.tambah(self.buat_prestasi(
                judul=tingkat, tingkat=tingkat
            ))
        terbaik = self.portofolio.daftar_terbaik()
        self.assertEqual(3, len(terbaik))
        self.assertEqual("Internasional", terbaik[0].tingkat)

    def test_total_poin_default_hanya_tiga_terbaik(self):
        for tingkat in ("Kabupaten / Kota", "Provinsi", "Nasional", "Internasional"):
            self.portofolio.tambah(self.buat_prestasi(
                judul=tingkat, tingkat=tingkat
            ))
        self.assertEqual(225.0, self.portofolio.total_poin())
        self.assertEqual(250.0, self.portofolio.total_poin(hanya_terbaik=False))

    def test_rata_rata_poin_dan_portofolio_kosong(self):
        self.assertEqual(0.0, self.portofolio.rata_rata_poin())
        self.portofolio.tambah(self.buat_prestasi())
        self.assertEqual(75.0, self.portofolio.rata_rata_poin())

    def test_hitung_nilai_akhir_seleksi(self):
        self.portofolio.tambah(self.buat_prestasi())
        self.assertEqual(
            81.0,
            self.portofolio.hitung_nilai_akhir_seleksi(nilai_rapor=85.0),
        )

    def test_bobot_beregu_di_batas_valid(self):
        for bobot in (0.75, 0.80, 0.85):
            with self.subTest(bobot=bobot):
                prestasi = self.buat_prestasi(
                    jenis_kepesertaan="Beregu", bobot_beregu=bobot
                )
                self.assertEqual(bobot, prestasi.faktor_kepesertaan)

    def test_bobot_beregu_di_luar_rentang_ditolak(self):
        for bobot in (0.74, 0.86):
            with self.subTest(bobot=bobot):
                with self.assertRaises(ValueError):
                    self.buat_prestasi(
                        jenis_kepesertaan="Beregu", bobot_beregu=bobot
                    )

    def test_bobot_beregu_tidak_berlaku_untuk_individual(self):
        with self.assertRaises(ValueError):
            self.buat_prestasi(bobot_beregu=0.80)

    def test_validasi_judul_tahun_dan_opsi(self):
        with self.assertRaises(ValueError):
            self.buat_prestasi(judul="  ")
        with self.assertRaises(ValueError):
            self.buat_prestasi(tahun=1800)
        with self.assertRaises(ValueError):
            self.buat_prestasi(tingkat="Sekolah")

    def test_validasi_bobot_nilai_akhir(self):
        with self.assertRaises(ValueError):
            self.portofolio.hitung_nilai_akhir_seleksi(101)
        with self.assertRaises(ValueError):
            self.portofolio.hitung_nilai_akhir_seleksi(80, 0.5, 0.4)

    def test_serialisasi_dan_deserialisasi(self):
        prestasi = self.buat_prestasi(
            jenis_kepesertaan="Beregu", bobot_beregu=0.75,
            catatan="Final nasional"
        )
        self.portofolio.tambah(prestasi)
        hasil = PortofolioAkademik.dari_dict(self.portofolio.to_dict())
        self.assertEqual(1, hasil.jumlah())
        self.assertEqual(prestasi, hasil.daftar()[0])
        self.assertEqual(prestasi.poin, hasil.daftar()[0].poin)

    def test_migrasi_data_lama_tanpa_menghilangkan_catatan(self):
        data_lama = [{
            "judul": "Juara kelas", "kategori": "Akademik",
            "tingkat": "Sekolah", "tahun": 2025,
        }]
        hasil = PortofolioAkademik.dari_dict(data_lama)
        record = hasil.daftar()[0]
        self.assertTrue(record.data_lama)
        self.assertEqual("Peserta / Panitia", record.juara)
        self.assertEqual(0, record.poin)
        self.assertIn("Akademik", record.catatan)

    def test_rincian_poin_memuat_semua_faktor(self):
        prestasi = self.buat_prestasi(
            penyelenggara="PTN / PTS / Induk Organisasi Resmi",
            jenis_kepesertaan="Beregu", bobot_beregu=0.75,
            jenjang_lomba="Non-Berjenjang",
        )
        rincian = prestasi.rincian_poin()
        for key in (
            "skor_dasar", "faktor_penyelenggara", "faktor_kepesertaan",
            "faktor_jenjang", "faktor_pengali_total", "poin_akhir",
        ):
            self.assertIn(key, rincian)
        self.assertAlmostEqual(40.64, rincian["poin_akhir"])


if __name__ == "__main__":
    unittest.main()
