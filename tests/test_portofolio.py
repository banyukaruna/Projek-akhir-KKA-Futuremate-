import unittest

from models.portofolio import (
    PortofolioAkademik, PrestasiAkademik,
    TINGKAT_OPSI, JUARA_OPSI, PENYELENGGARA_OPSI, JENJANG_OPSI, KEPESERTAAN_OPSI,
    SKOR_DASAR_MATRIX, FAKTOR_PENYELENGGARA, FAKTOR_KEPESERTAAN, FAKTOR_JENJANG,
)


class PortofolioAkademikTests(unittest.TestCase):
    def setUp(self):
        self.portofolio = PortofolioAkademik()

    def test_tingkat_opsi_tersedia(self):
        self.assertEqual(
            ["Internasional", "Nasional", "Provinsi", "Kabupaten / Kota"],
            TINGKAT_OPSI,
        )

    def test_juara_opsi_tersedia(self):
        self.assertEqual(
            ["Juara 1", "Juara 2", "Juara 3", "Juara Harapan / Finalis", "Peserta / Panitia"],
            JUARA_OPSI,
        )

    def test_tambah_prestasi_memperbarui_jumlah_dan_poin(self):
        p1 = PrestasiAkademik(
            "OSN Matematika", "Nasional", "Juara 1",
            penyelenggara="Kementerian / Lembaga Negara",
            jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang", tahun=2026,
        )
        p2 = PrestasiAkademik(
            "Lomba Sains", "Provinsi", "Juara 2",
            penyelenggara="PTN / PTS / Induk Organisasi Resmi",
            jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang", tahun=2026,
        )

        self.portofolio.tambah(p1)
        self.portofolio.tambah(p2)

        self.assertEqual(2, self.portofolio.jumlah())
        self.assertAlmostEqual(109.0, self.portofolio.total_poin(hanya_terbaik=False))
        self.assertEqual([p1, p2], self.portofolio.daftar())

    def test_skor_dasar_nol_untuk_peserta(self):
        prestasi = PrestasiAkademik(
            "Lomba", "Kabupaten / Kota", "Peserta / Panitia",
            penyelenggara="Kementerian / Lembaga Negara",
            jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang", tahun=2026,
        )
        self.assertEqual(0, prestasi.skor_dasar)
        self.assertEqual(0.0, prestasi.poin)

    def test_hapus_prestasi(self):
        p1 = PrestasiAkademik(
            "OSN", "Nasional", "Juara 1",
            penyelenggara="Kementerian / Lembaga Negara",
            jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang", tahun=2026,
        )
        p2 = PrestasiAkademik(
            "Lomba", "Provinsi", "Juara 2",
            penyelenggara="PTN / PTS / Induk Organisasi Resmi",
            jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang", tahun=2026,
        )
        self.portofolio.tambah(p1)
        self.portofolio.tambah(p2)

        berhasil = self.portofolio.hapus(p1)

        self.assertTrue(berhasil)
        self.assertEqual(1, self.portofolio.jumlah())
        self.assertEqual([p2], self.portofolio.daftar())

    def test_hapus_data_yang_tidak_ada_tidak_mengubah_portofolio(self):
        pencapaian = PrestasiAkademik(
            "Juara kelas", "Nasional", "Juara 1",
            penyelenggara="Kementerian / Lembaga Negara",
            jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang", tahun=2026,
        )

        berhasil = self.portofolio.hapus(pencapaian)

        self.assertFalse(berhasil)
        self.assertEqual(0, self.portofolio.jumlah())
        self.assertEqual(0, self.portofolio.total_poin())

    def test_daftar_terambil_default_3(self):
        for i in range(5):
            self.portofolio.tambah(PrestasiAkademik(
                f"Lomba {i}", "Provinsi", "Juara 3",
                penyelenggara="Kementerian / Lembaga Negara",
                jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang", tahun=2026,
            ))
        terbaik = self.portofolio.daftar_terbaik(limit=3)
        self.assertEqual(3, len(terbaik))

    def test_total_poin_hanya_terbaik_default(self):
        for i in range(5):
            self.portofolio.tambah(PrestasiAkademik(
                f"Lomba {i}", "Nasional", "Juara 1",
                penyelenggara="Kementerian / Lembaga Negara",
                jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang", tahun=2026,
            ))
        total_semua = self.portofolio.total_poin(hanya_terbaik=False)
        total_terbaik = self.portofolio.total_poin(hanya_terbaik=True)
        self.assertGreater(total_semua, total_terbaik)
        self.assertEqual(total_terbaik, self.portofolio.total_poin())

    def test_hitung_nilai_akhir_seleksi(self):
        self.portofolio.tambah(PrestasiAkademik(
            "OSN", "Nasional", "Juara 1",
            penyelenggara="Kementerian / Lembaga Negara",
            jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang", tahun=2026,
        ))
        nilai_akhir = self.portofolio.hitung_nilai_akhir_seleksi(nilai_rapor=85.0)
        self.assertAlmostEqual(81.0, nilai_akhir)

    def test_bobot_beregu_di_rentang_valid(self):
        prestasi = PrestasiAkademik(
            "Lomba Tim", "Provinsi", "Juara 1",
            penyelenggara="Kementerian / Lembaga Negara",
            jenis_kepesertaan="Beregu", bobot_beregu=0.80,
            jenjang_lomba="Berjenjang", tahun=2026,
        )
        self.assertEqual(0.80, prestasi.faktor_kepesertaan)

    def test_bobot_beregu_luar_rentang_ditolak(self):
        with self.assertRaises(ValueError):
            PrestasiAkademik(
                "Lomba Tim", "Provinsi", "Juara 1",
                penyelenggara="Kementerian / Lembaga Negara",
                jenis_kepesertaan="Beregu", bobot_beregu=0.90,
                jenjang_lomba="Berjenjang", tahun=2026,
            )
    def test_serialisasi_dan_deserialisasi(self):
        self.portofolio.tambah(PrestasiAkademik(
            "OSN Matematika", "Nasional", "Juara 1",
            penyelenggara="Kementerian / Lembaga Negara",
            jenis_kepesertaan="Individual", jenjang_lomba="Berjenjang",
            tahun=2026, catatan="Lomba tahun ini",
        ))
        data = self.portofolio.to_dict()
        hasil = PortofolioAkademik.dari_dict(data)
        self.assertEqual(1, hasil.jumlah())
        self.assertEqual("OSN Matematika", hasil.daftar()[0].judul)
        self.assertEqual("Nasional", hasil.daftar()[0].tingkat)
        self.assertEqual("Juara 1", hasil.daftar()[0].juara)
        self.assertEqual("Kementerian / Lembaga Negara", hasil.daftar()[0].penyelenggara)

    def test_rincian_poin_lengkap(self):
        prestasi = PrestasiAkademik(
            "OSN Matematika", "Nasional", "Juara 1",
            penyelenggara="PTN / PTS / Induk Organisasi Resmi",
            jenis_kepesertaan="Beregu", bobot_beregu=0.75,
            jenjang_lomba="Non-Berjenjang", tahun=2026,
        )
        r = prestasi.rincian_poin()
        kunci = {"skor_dasar", "faktor_penyelenggara", "faktor_kepesertaan",
                 "faktor_jenjang", "faktor_pengali_total", "poin_akhir"}
        self.assertTrue(kunci.issubset(set(r.keys())))
        self.assertAlmostEqual(40.45, r["poin_akhir"])


if __name__ == "__main__":
    unittest.main()
