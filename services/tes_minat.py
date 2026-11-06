"""Tes minat ringan bergaya RIASEC dan rekomendasi jurusan."""

NAMA_TIPE = {"R": "Realistic (praktis/teknis)", "I": "Investigative (analitis)",
             "A": "Artistic (kreatif)", "S": "Social (membantu orang)",
             "E": "Enterprising (memimpin/bisnis)", "C": "Conventional (teliti/terstruktur)"}

PERTANYAAN = [
    ("Aku suka membongkar atau memperbaiki barang.", "R"),
    ("Aku senang bekerja dengan alat atau di luar ruangan.", "R"),
    ("Aku penasaran dan suka mencari tahu 'kenapa' sesuatu terjadi.", "I"),
    ("Aku senang memecahkan soal logika atau sains.", "I"),
    ("Aku suka menggambar, menulis, atau membuat karya kreatif.", "A"),
    ("Aku lebih suka tugas yang bebas berekspresi.", "A"),
    ("Aku senang membantu teman yang kesulitan.", "S"),
    ("Aku suka mengajar atau menjelaskan sesuatu ke orang lain.", "S"),
    ("Aku suka memimpin kelompok atau meyakinkan orang.", "E"),
    ("Aku tertarik memulai usaha atau organisasi.", "E"),
    ("Aku suka merapikan data, jadwal, atau catatan.", "C"),
    ("Aku nyaman dengan aturan dan langkah yang jelas.", "C"),
]


class ProfilMinat:
    @staticmethod
    def hitung(jawaban):
        """jawaban: list angka 1-5, urut sesuai PERTANYAAN. Hasil: {tipe: skor 2-10}."""
        skor = {t: 0 for t in NAMA_TIPE}
        for (_, tipe), nilai in zip(PERTANYAAN, jawaban):
            skor[tipe] += nilai
        return skor

    @staticmethod
    def tipe_teratas(profil, n=3):
        return sorted(profil, key=profil.get, reverse=True)[:n]

    @staticmethod
    def rekomendasikan(profil, katalog, n=3):
        """Mengembalikan [(Jurusan, kecocokan_persen)] terbaik."""
        hasil = []
        for j in katalog:
            skor = sum(profil.get(t, 0) for t in j.riasec) / (10 * len(j.riasec)) * 100
            hasil.append((j, skor))
        return sorted(hasil, key=lambda x: x[1], reverse=True)[:n]
