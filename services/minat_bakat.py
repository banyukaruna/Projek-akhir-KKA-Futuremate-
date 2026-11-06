"""Layanan tes minat RIASEC dan pencocokan jurusan FutureMate."""
from datetime import datetime

NAMA_TIPE = {
    "R": "Realistic", "I": "Investigative", "A": "Artistic",
    "S": "Social", "E": "Enterprising", "C": "Conventional"
}
DESKRIPSI_TIPE = {
    "R": "Menyukai praktik langsung, alat, teknologi, dan penerapan teknis.",
    "I": "Menyukai analisis, penelitian, logika, dan pemecahan masalah.",
    "A": "Menyukai kreativitas, desain, ekspresi, dan pengembangan ide.",
    "S": "Menyukai kegiatan membantu, mengajar, membimbing, dan berinteraksi.",
    "E": "Menyukai kepemimpinan, persuasi, kewirausahaan, dan pengelolaan.",
    "C": "Menyukai data, administrasi, prosedur, dan pekerjaan terstruktur."
}
PERTANYAAN_PER_TIPE = {
    "R": [
        "Saya tertarik merakit komputer dari berbagai komponen hingga dapat digunakan.",
        "Saya ingin mencoba memperbaiki perangkat elektronik yang mengalami kerusakan.",
        "Saya tertarik membuat prototipe sederhana menggunakan bahan seperti kayu, plastik, atau logam.",
        "Saya menikmati kegiatan menanam dan merawat tanaman hingga siap dipanen.",
        "Saya tertarik mengoperasikan peralatan teknis untuk menyelesaikan suatu pekerjaan.",
        "Saya ingin mencoba memasang dan menguji rangkaian listrik sederhana.",
        "Saya tertarik membuat model bangunan atau struktur menggunakan bahan tertentu.",
        "Saya menikmati kegiatan mengamati dan memetakan kondisi lingkungan secara langsung.",
        "Saya tertarik mempelajari cara kerja mesin kendaraan dan komponennya.",
        "Saya ingin terlibat dalam proyek yang menghasilkan benda atau produk fisik."
    ],
    "I": [
        "Saya tertarik menganalisis data survei untuk menemukan pola perilaku masyarakat.",
        "Saya ingin mencari penyebab suatu program komputer mengalami kesalahan.",
        "Saya menikmati kegiatan melakukan eksperimen untuk menguji suatu hipotesis.",
        "Saya tertarik menyelidiki mengapa suatu fenomena alam dapat terjadi.",
        "Saya ingin membandingkan beberapa metode untuk menemukan solusi paling efektif.",
        "Saya tertarik menganalisis hasil penelitian sebelum menarik kesimpulan.",
        "Saya menikmati kegiatan memecahkan teka-teki logika atau persoalan matematika.",
        "Saya ingin mempelajari bagaimana suatu penyakit dapat memengaruhi tubuh manusia.",
        "Saya tertarik mengamati perubahan lingkungan menggunakan data pengukuran.",
        "Saya ingin mencari hubungan antara beberapa faktor yang memengaruhi suatu masalah."
    ],
    "A": [
        "Saya tertarik merancang tampilan aplikasi agar mudah digunakan dan menarik.",
        "Saya ingin membuat ilustrasi untuk menyampaikan suatu cerita atau gagasan.",
        "Saya menikmati kegiatan menulis cerita dengan karakter dan alur buatan sendiri.",
        "Saya tertarik membuat desain poster untuk sebuah acara.",
        "Saya ingin menciptakan komposisi musik atau suara untuk sebuah karya.",
        "Saya menikmati kegiatan mengambil dan mengolah foto dengan konsep tertentu.",
        "Saya tertarik merancang interior ruangan berdasarkan tema yang saya pilih.",
        "Saya ingin membuat video kreatif dengan penyuntingan dan konsep visual sendiri.",
        "Saya menikmati kegiatan mengembangkan ide produk dengan bentuk atau fungsi yang unik.",
        "Saya tertarik mengeksplorasi berbagai gaya seni untuk menghasilkan karya orisinal."
    ],
    "S": [
        "Saya tertarik membantu teman memahami materi pelajaran yang belum mereka kuasai.",
        "Saya ingin menjadi pendamping dalam kegiatan belajar anak-anak.",
        "Saya menikmati kegiatan mendengarkan orang lain ketika mereka menghadapi masalah.",
        "Saya tertarik mengadakan kegiatan edukasi mengenai kesehatan bagi masyarakat.",
        "Saya ingin membantu anggota kelompok yang mengalami kesulitan menyelesaikan tugas.",
        "Saya menikmati kegiatan mengajarkan keterampilan baru kepada orang lain.",
        "Saya tertarik merancang program untuk membantu masyarakat yang membutuhkan.",
        "Saya ingin menjadi fasilitator dalam diskusi kelompok.",
        "Saya menikmati kegiatan membimbing seseorang agar dapat mengembangkan potensinya.",
        "Saya tertarik mempelajari cara menyelesaikan konflik antarmanusia melalui komunikasi."
    ],
    "E": [
        "Saya tertarik memimpin tim dalam mengerjakan sebuah proyek.",
        "Saya ingin merancang strategi pemasaran untuk memperkenalkan produk baru.",
        "Saya menikmati kegiatan mempresentasikan ide untuk mendapatkan dukungan orang lain.",
        "Saya tertarik merintis usaha kecil dengan produk atau layanan buatan sendiri.",
        "Saya ingin menjadi koordinator dalam penyelenggaraan sebuah acara.",
        "Saya menikmati kegiatan bernegosiasi untuk mencapai kesepakatan.",
        "Saya tertarik menentukan strategi agar sebuah organisasi dapat mencapai targetnya.",
        "Saya ingin mengembangkan konsep bisnis berdasarkan kebutuhan konsumen.",
        "Saya menikmati kegiatan mengambil keputusan ketika tim menghadapi beberapa pilihan.",
        "Saya tertarik mencari peluang kerja sama dengan pihak lain untuk mengembangkan proyek."
    ],
    "C": [
        "Saya tertarik mengelola data dalam spreadsheet agar mudah dianalisis.",
        "Saya ingin memeriksa laporan keuangan untuk menemukan kesalahan pencatatan.",
        "Saya menikmati kegiatan menyusun arsip digital berdasarkan kategori tertentu.",
        "Saya tertarik membuat jadwal kegiatan dan memastikan setiap tugas memiliki tenggat waktu.",
        "Saya ingin mengelola basis data agar informasi tersimpan secara teratur.",
        "Saya menikmati kegiatan memeriksa kelengkapan dokumen sebelum dikumpulkan.",
        "Saya tertarik membuat sistem pencatatan inventaris untuk suatu organisasi.",
        "Saya ingin menyusun laporan berdasarkan data yang telah dikumpulkan.",
        "Saya menikmati kegiatan mengikuti prosedur kerja secara sistematis.",
        "Saya tertarik membuat format administrasi yang memudahkan pekerjaan berulang."
    ]
}
PERTANYAAN = [(pertanyaan, tipe) for tipe in ("R", "I", "A", "S", "E", "C")
              for pertanyaan in PERTANYAAN_PER_TIPE[tipe]]
SKALA_JAWABAN = {
    1: "Sangat tidak tertarik", 2: "Tidak tertarik",
    3: "Netral", 4: "Tertarik", 5: "Sangat tertarik"
}

def hitung_profil(jawaban):
    """Mengubah rerata 10 jawaban per tipe dari skala 1-5 menjadi 0-100."""
    if len(jawaban) != 60 or any(int(x) not in range(1, 6) for x in jawaban):
        raise ValueError("Tes harus memiliki 60 jawaban dengan skala 1 sampai 5.")
    hasil = {}
    posisi = 0
    for tipe in ("R", "I", "A", "S", "E", "C"):
        bagian = [int(x) for x in jawaban[posisi:posisi + 10]]
        rerata = sum(bagian) / 10
        hasil[tipe] = round(((rerata - 1) / 4) * 100, 1)
        posisi += 10
    return hasil

def tipe_teratas(profil, jumlah=3):
    urutan = ("R", "I", "A", "S", "E", "C")
    return sorted(urutan, key=lambda t: (-float(profil.get(t, 0)), urutan.index(t)))[:jumlah]

def skor_kecocokan(profil_pengguna, profil_jurusan):
    """Menghitung kecocokan dengan bobot 70% untuk tiga tipe pengguna tertinggi
    dan 30% untuk tiga tipe lainnya. Setiap kelompok dibagi rata.
    """
    tiga_utama = set(tipe_teratas(profil_pengguna, 3))
    bobot_per_tipe = {
        tipe: (0.7 / 3 if tipe in tiga_utama else 0.3 / 3)
        for tipe in NAMA_TIPE
    }
    jarak_berbobot = sum(
        abs(float(profil_pengguna.get(tipe, 0)) -
            float(profil_jurusan.get(tipe, 0))) * bobot_per_tipe[tipe]
        for tipe in NAMA_TIPE
    )
    return round(max(0.0, 100 - jarak_berbobot), 1)

def rekomendasikan(profil, katalog, jumlah=10):
    hasil = []
    for jurusan in katalog:
        nilai = skor_kecocokan(profil, jurusan["riasec"])
        hasil.append((jurusan, nilai))
    return sorted(hasil, key=lambda item: (-item[1], item[0]["nama"]))[:jumlah]

def buat_riwayat(jawaban, katalog):
    profil = hitung_profil(jawaban)
    rekomendasi = [
        {"nama": item["nama"], "bidang": item["bidang"], "kecocokan": skor}
        for item, skor in rekomendasikan(profil, katalog, 10)
    ]
    return {
        "tanggal": datetime.now().isoformat(timespec="seconds"),
        "jawaban": [int(x) for x in jawaban],
        "skor": profil,
        "tiga_teratas": tipe_teratas(profil),
        "rekomendasi": rekomendasi
    }
