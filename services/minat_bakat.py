"""Layanan tes eksplorasi minat RIASEC FutureMate.

Instrumen disusun mandiri dengan acuan kerangka RIASEC. Instrumen belum
tervalidasi secara psikometri dan bukan tes bakat atau diagnosis.
"""
from datetime import datetime
import math

URUTAN_TIPE = ("R", "I", "A", "S", "E", "C")
NAMA_TIPE = {
    "R": "Realistic", "I": "Investigative", "A": "Artistic",
    "S": "Social", "E": "Enterprising", "C": "Conventional"
}
DESKRIPSI_TIPE = {
    "R": "Menyukai praktik langsung, alat, teknologi, dan penerapan teknis.",
    "I": "Menyukai analisis, penelitian, logika, dan pemecahan masalah.",
    "A": "Menyukai kreativitas, desain, ekspresi, dan pengembangan ide.",
    "S": "Menyukai kegiatan membantu, mengajar, membimbing, dan berinteraksi.",
    "E": "Menyukai inisiatif, persuasi, negosiasi, dan penggerakan kegiatan.",
    "C": "Menyukai ketelitian, pengaturan informasi, prosedur, dan keteraturan."
}

# Pengantar seragam pada GUI: Seberapa tertarik kamu melakukan aktivitas berikut?
PERTANYAAN_PER_TIPE = {
    "R": [
        "Merakit komponen komputer hingga menjadi perangkat yang berfungsi.",
        "Memperbaiki benda atau perangkat yang mengalami kerusakan.",
        "Membuat model fisik dari bahan seperti kardus, kayu, atau plastik.",
        "Mengoperasikan alat untuk menghasilkan atau mengolah suatu benda.",
        "Memasang rangkaian listrik sederhana sesuai petunjuk.",
        "Membuat atau merakit benda dengan mengikuti gambar rancangan.",
        "Melakukan pengamatan langsung terhadap kondisi suatu tempat.",
        "Menguji cara kerja perangkat mekanis sederhana.",
        "Membuat benda praktis untuk menyelesaikan masalah sehari-hari.",
        "Melakukan kegiatan lapangan yang melibatkan penggunaan peralatan."
    ],
    "I": [
        "Menganalisis kumpulan data untuk menemukan pola.",
        "Mencari penyebab kesalahan dalam sebuah program komputer.",
        "Melakukan percobaan untuk menguji dugaan atau hipotesis.",
        "Menyelidiki penyebab suatu fenomena alam.",
        "Membandingkan beberapa cara untuk menentukan solusi paling efektif.",
        "Menelaah hasil penelitian sebelum menarik kesimpulan.",
        "Memecahkan persoalan logika atau matematika yang menantang.",
        "Mempelajari proses biologis yang terjadi di dalam tubuh manusia.",
        "Menggunakan hasil pengukuran untuk memahami perubahan lingkungan.",
        "Mencari hubungan sebab-akibat dari beberapa faktor dalam suatu masalah."
    ],
    "A": [
        "Merancang tampilan visual untuk sebuah aplikasi atau situs.",
        "Membuat ilustrasi untuk menyampaikan sebuah gagasan.",
        "Menulis cerita dengan tokoh dan alur yang dibuat sendiri.",
        "Membuat poster dengan konsep visual yang orisinal.",
        "Menciptakan melodi atau komposisi musik.",
        "Mengambil foto dengan konsep dan sudut pandang tertentu.",
        "Merancang tata ruang berdasarkan gagasan atau tema tertentu.",
        "Menyunting video untuk membangun suasana atau alur cerita.",
        "Menciptakan karya seni menggunakan media yang dipilih sendiri.",
        "Mengembangkan gagasan kreatif untuk bentuk atau tampilan sebuah produk."
    ],
    "S": [
        "Menjelaskan materi pelajaran kepada teman yang membutuhkan bantuan.",
        "Mendampingi anak-anak dalam kegiatan belajar.",
        "Mendengarkan cerita seseorang yang ingin menyampaikan masalahnya.",
        "Memberikan informasi yang membantu orang memahami suatu topik.",
        "Membantu anggota kelompok memahami tugas yang harus dikerjakan.",
        "Mengajarkan keterampilan baru kepada orang lain.",
        "Mendampingi seseorang saat ia berlatih keterampilan tertentu.",
        "Memfasilitasi diskusi agar setiap anggota dapat menyampaikan pendapat.",
        "Membantu dua orang menemukan jalan keluar dari perselisihan.",
        "Mengadakan kegiatan bersama untuk memenuhi kebutuhan masyarakat."
    ],
    "E": [
        "Mengajak orang lain mendukung sebuah gagasan atau rencana.",
        "Mempresentasikan usulan agar pihak lain bersedia mempertimbangkannya.",
        "Menawarkan produk atau gagasan kepada calon pengguna.",
        "Memulai sebuah kegiatan dari ide yang saya ajukan.",
        "Mengoordinasikan pembagian tugas dalam sebuah kelompok.",
        "Bernegosiasi untuk mencapai kesepakatan bersama.",
        "Menentukan langkah untuk mencapai target sebuah kelompok.",
        "Mencari peluang kerja sama untuk mengembangkan sebuah kegiatan.",
        "Meyakinkan kelompok agar berani mencoba pendekatan baru.",
        "Mengambil inisiatif ketika sebuah kegiatan belum memiliki penggerak."
    ],
    "C": [
        "Mengelompokkan dokumen digital agar mudah ditemukan kembali.",
        "Memeriksa angka dalam tabel untuk memastikan ketepatannya.",
        "Menyusun informasi ke dalam format yang seragam.",
        "Membuat jadwal rinci untuk mengatur urutan kegiatan.",
        "Memasukkan data ke dalam tabel dengan teliti.",
        "Memeriksa kelengkapan berkas berdasarkan daftar periksa.",
        "Mencatat keluar-masuk barang agar jumlahnya selalu terpantau.",
        "Menyusun catatan kegiatan secara runtut dan teratur.",
        "Mengikuti langkah kerja tertulis secara berurutan.",
        "Menata berkas berdasarkan aturan penamaan dan kategori."
    ]
}
PERTANYAAN = [
    (pertanyaan, tipe)
    for tipe in URUTAN_TIPE
    for pertanyaan in PERTANYAAN_PER_TIPE[tipe]
]
SKALA_JAWABAN = {
    1: "Sangat tidak tertarik", 2: "Tidak tertarik",
    3: "Netral", 4: "Tertarik", 5: "Sangat tertarik"
}
KETERANGAN_INSTRUMEN = (
    "Tes ini merupakan instrumen eksplorasi minat FutureMate berdasarkan "
    "kerangka RIASEC. Instrumen belum melalui validasi psikometri. Hasilnya "
    "bukan diagnosis, bukan ukuran kemampuan atau bakat, dan bukan penentu "
    "pilihan pendidikan atau karier. Gunakan sebagai bahan refleksi."
)
SUMBER_LANDASAN = (
    ("O*NET Interest Profiler Manual", "https://www.onetcenter.org/reports/IP_Manual.pdf"),
    ("O*NET Interest Profiler", "https://www.onetcenter.org/IP.html"),
    ("Kemnaker Karirhub", "https://karirhub.kemnaker.go.id/"),
)

def _normalisasi_jawaban(jawaban):
    try:
        nilai = list(jawaban)
    except TypeError as error:
        raise ValueError("Jawaban harus berupa daftar berisi 60 nilai.") from error
    if len(nilai) != 60:
        raise ValueError("Tes harus memiliki tepat 60 jawaban.")
    hasil = []
    for item in nilai:
        if isinstance(item, bool):
            raise ValueError("Setiap jawaban harus berupa angka bulat 1 sampai 5.")
        if isinstance(item, int):
            angka = item
        elif isinstance(item, str) and item.strip() in ("1", "2", "3", "4", "5"):
            angka = int(item.strip())
        else:
            raise ValueError("Setiap jawaban harus berupa angka bulat 1 sampai 5.")
        if angka not in range(1, 6):
            raise ValueError("Setiap jawaban harus berupa angka bulat 1 sampai 5.")
        hasil.append(angka)
    return hasil

def _validasi_profil(profil, nama="profil"):
    if not isinstance(profil, dict):
        raise ValueError(f"{nama.capitalize()} harus berupa dictionary.")
    hasil = {}
    for tipe in URUTAN_TIPE:
        if tipe not in profil:
            raise ValueError(f"Dimensi {tipe} tidak ditemukan dalam {nama}.")
        try:
            angka = float(profil[tipe])
        except (TypeError, ValueError) as error:
            raise ValueError(f"Skor {tipe} pada {nama} harus berupa angka.") from error
        if not math.isfinite(angka) or not 0 <= angka <= 100:
            raise ValueError(f"Skor {tipe} pada {nama} harus berada pada 0 sampai 100.")
        hasil[tipe] = angka
    return hasil

def hitung_profil(jawaban):
    """Skor 0-100 adalah transformasi skala, bukan persentil atau ukuran bakat."""
    nilai = _normalisasi_jawaban(jawaban)
    hasil = {}
    for indeks, tipe in enumerate(URUTAN_TIPE):
        bagian = nilai[indeks * 10:(indeks + 1) * 10]
        rerata = sum(bagian) / 10
        hasil[tipe] = round(((rerata - 1) / 4) * 100, 1)
    return hasil

def tipe_teratas(profil, jumlah=3):
    """Sertakan seluruh tipe yang seri pada batas jumlah yang diminta."""
    nilai = _validasi_profil(profil)
    if isinstance(jumlah, bool) or not isinstance(jumlah, int) or jumlah < 1:
        raise ValueError("Jumlah tipe harus berupa bilangan bulat positif.")
    urutan = sorted(URUTAN_TIPE, key=lambda tipe: nilai[tipe], reverse=True)
    batas = nilai[urutan[min(jumlah, len(urutan)) - 1]]
    return [tipe for tipe in urutan if nilai[tipe] >= batas]

def skor_kecocokan(profil_pengguna, profil_jurusan):
    """Kemiripan heuristik dengan bobot sama untuk enam dimensi RIASEC."""
    pengguna = _validasi_profil(profil_pengguna, "profil pengguna")
    jurusan = _validasi_profil(profil_jurusan, "profil program studi")
    selisih = sum(
        abs(pengguna[tipe] - jurusan[tipe]) for tipe in URUTAN_TIPE
    ) / 6
    return round(100 - selisih, 1)

def rekomendasikan(profil, katalog, jumlah=10):
    _validasi_profil(profil)
    if isinstance(jumlah, bool) or not isinstance(jumlah, int) or jumlah < 0:
        raise ValueError("Jumlah rekomendasi harus berupa bilangan bulat nonnegatif.")
    hasil = []
    for jurusan in katalog:
        status = str(jurusan.get("status_program", "")).lower()
        if ("konsentrasi atau bidang kajian" in status
                or "bidang peminatan atau spesialisasi" in status):
            continue
        nilai = skor_kecocokan(profil, jurusan["riasec"])
        hasil.append((jurusan, nilai))
    return sorted(hasil, key=lambda item: (-item[1], item[0]["nama"]))[:jumlah]

def buat_riwayat(jawaban, katalog):
    nilai_jawaban = _normalisasi_jawaban(jawaban)
    profil = hitung_profil(nilai_jawaban)
    rekomendasi = [
        {"nama": item["nama"], "bidang": item["bidang"], "kecocokan": skor}
        for item, skor in rekomendasikan(profil, katalog, 10)
    ]
    return {
        "tanggal": datetime.now().isoformat(timespec="seconds"),
        "jawaban": nilai_jawaban,
        "skor": profil,
        "tiga_teratas": tipe_teratas(profil),
        "rekomendasi": rekomendasi
    }
