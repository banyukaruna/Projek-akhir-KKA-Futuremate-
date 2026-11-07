import unittest

from services.minat_bakat import (
    DESKRIPSI_TIPE,
    KETERANGAN_INSTRUMEN,
    NAMA_TIPE,
    PERTANYAAN,
    PERTANYAAN_PER_TIPE,
    SKALA_JAWABAN,
    URUTAN_TIPE,
    hitung_profil,
    rekomendasikan,
    skor_kecocokan,
    tipe_teratas,
)


class MinatBakatTests(unittest.TestCase):
    def test_enam_tipe_masing_masing_memiliki_sepuluh_pertanyaan(self):
        self.assertEqual(6, len(PERTANYAAN_PER_TIPE))
        for tipe in URUTAN_TIPE:
            with self.subTest(tipe=tipe):
                self.assertEqual(10, len(PERTANYAAN_PER_TIPE[tipe]))

    def test_total_enam_puluh_pertanyaan_dan_pemetaan_tipe_benar(self):
        self.assertEqual(60, len(PERTANYAAN))
        for index, tipe in enumerate(URUTAN_TIPE):
            bagian = PERTANYAAN[index * 10:(index + 1) * 10]
            self.assertTrue(all(pasangan[1] == tipe for pasangan in bagian))

    def test_pertanyaan_tidak_duplikat_dan_tidak_kosong(self):
        semua = [pertanyaan.strip() for pertanyaan, _ in PERTANYAAN]
        self.assertEqual(60, len(set(semua)))
        self.assertTrue(all(semua))

    def test_skala_jawaban_lengkap(self):
        self.assertEqual([1, 2, 3, 4, 5], list(SKALA_JAWABAN))
        self.assertEqual(set(URUTAN_TIPE), set(NAMA_TIPE))
        self.assertEqual(set(URUTAN_TIPE), set(DESKRIPSI_TIPE))

    def test_skor_minimum_maksimum_dan_titik_tengah(self):
        self.assertEqual({t: 0.0 for t in URUTAN_TIPE}, hitung_profil([1] * 60))
        self.assertEqual({t: 100.0 for t in URUTAN_TIPE}, hitung_profil([5] * 60))
        self.assertEqual({t: 50.0 for t in URUTAN_TIPE}, hitung_profil([3] * 60))

    def test_perhitungan_sepuluh_jawaban_per_tipe(self):
        jawaban = [1] * 10 + [2] * 10 + [3] * 10 + [4] * 10 + [5] * 10 + [1] * 10
        self.assertEqual(
            {"R": 0.0, "I": 25.0, "A": 50.0, "S": 75.0, "E": 100.0, "C": 0.0},
            hitung_profil(jawaban),
        )

    def test_string_angka_dari_data_lama_diterima(self):
        self.assertEqual({t: 50.0 for t in URUTAN_TIPE}, hitung_profil(["3"] * 60))

    def test_jumlah_jawaban_salah_ditolak(self):
        for jawaban in ([], [3] * 59, [3] * 61):
            with self.subTest(jumlah=len(jawaban)):
                with self.assertRaises(ValueError):
                    hitung_profil(jawaban)

    def test_jawaban_di_luar_skala_ditolak(self):
        for nilai in (0, 6, "0", "6", 1.5, True, None, "abc"):
            with self.subTest(nilai=nilai):
                with self.assertRaises(ValueError):
                    hitung_profil([3] * 59 + [nilai])

    def test_tiga_tipe_teratas_tanpa_seri(self):
        profil = {"R": 90, "I": 80, "A": 70, "S": 60, "E": 50, "C": 40}
        self.assertEqual(["R", "I", "A"], tipe_teratas(profil))

    def test_seri_di_batas_posisi_ketiga_semua_ditampilkan(self):
        profil = {"R": 90, "I": 80, "A": 70, "S": 70, "E": 50, "C": 40}
        self.assertEqual(["R", "I", "A", "S"], tipe_teratas(profil))

    def test_semua_tipe_seri_tidak_diberi_peringkat_semu(self):
        profil = {t: 80 for t in URUTAN_TIPE}
        self.assertEqual(list(URUTAN_TIPE), tipe_teratas(profil))

    def test_jumlah_tipe_tidak_valid_ditolak(self):
        profil = {t: 50 for t in URUTAN_TIPE}
        for jumlah in (0, -1, 1.5, True):
            with self.subTest(jumlah=jumlah):
                with self.assertRaises(ValueError):
                    tipe_teratas(profil, jumlah)

    def test_kecocokan_menggunakan_bobot_sama_enam_dimensi(self):
        pengguna = {"R": 100, "I": 0, "A": 50, "S": 50, "E": 50, "C": 50}
        jurusan = {"R": 0, "I": 100, "A": 50, "S": 50, "E": 50, "C": 50}
        self.assertEqual(66.7, skor_kecocokan(pengguna, jurusan))

    def test_kecocokan_profil_identik_seratus(self):
        profil = {t: 50 for t in URUTAN_TIPE}
        self.assertEqual(100.0, skor_kecocokan(profil, profil))

    def test_profil_tidak_lengkap_atau_skor_tidak_valid_ditolak(self):
        profil = {t: 50 for t in URUTAN_TIPE}
        tidak_lengkap = dict(profil)
        del tidak_lengkap["C"]
        tidak_valid = dict(profil)
        tidak_valid["R"] = 101
        for pasangan in ((tidak_lengkap, profil), (profil, tidak_valid)):
            with self.subTest(pasangan=pasangan):
                with self.assertRaises(ValueError):
                    skor_kecocokan(*pasangan)

    def test_rekomendasi_menggunakan_kemiripan_enam_dimensi(self):
        profil = {t: 50 for t in URUTAN_TIPE}
        katalog = [
            {"nama": "A", "bidang": "X", "riasec": dict(profil)},
            {"nama": "B", "bidang": "Y",
             "riasec": {"R": 100, "I": 0, "A": 50, "S": 50, "E": 50, "C": 50}},
        ]
        hasil = rekomendasikan(profil, katalog, 2)
        self.assertEqual(["A", "B"], [item["nama"] for item, _ in hasil])
        self.assertEqual([100.0, 83.3], [skor for _, skor in hasil])

    def test_batas_penggunaan_instrumen_dinyatakan(self):
        self.assertIn("belum", KETERANGAN_INSTRUMEN.lower())
        self.assertIn("bukan", KETERANGAN_INSTRUMEN.lower())


if __name__ == "__main__":
    unittest.main()
