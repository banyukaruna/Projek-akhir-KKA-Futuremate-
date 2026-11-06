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
        "Aku tertarik merakit atau memperbaiki perangkat elektronik.",
        "Aku senang menggunakan peralatan untuk membuat sesuatu.",
        "Aku tertarik melakukan kegiatan praktik di laboratorium atau bengkel.",
        "Aku menikmati kegiatan luar ruang yang melibatkan keterampilan fisik.",
        "Aku suka mempelajari cara kerja mesin atau perangkat teknis.",
        "Aku tertarik membuat model atau prototipe benda.",
        "Aku senang mengerjakan tugas yang hasilnya dapat dilihat secara langsung.",
        "Aku tertarik mengoperasikan alat atau mesin sesuai prosedur.",
        "Aku menikmati kegiatan yang membutuhkan koordinasi tangan dan ketelitian teknis.",
        "Aku ingin mencoba pekerjaan yang banyak melibatkan praktik langsung."
    ],
    "I": [
        "Aku senang mencari penyebab dari suatu peristiwa.",
        "Aku tertarik menganalisis data untuk menemukan pola.",
        "Aku menikmati soal yang membutuhkan penalaran logis.",
        "Aku suka melakukan eksperimen untuk menguji dugaan.",
        "Aku tertarik mempelajari konsep ilmiah secara mendalam.",
        "Aku senang membandingkan beberapa solusi sebelum mengambil keputusan.",
        "Aku tertarik membaca hasil penelitian atau kajian ilmiah.",
        "Aku suka memecahkan masalah yang belum memiliki jawaban jelas.",
        "Aku menikmati kegiatan mengumpulkan dan menafsirkan informasi.",
        "Aku tertarik memahami hubungan sebab dan akibat."
    ],
    "A": [
        "Aku suka membuat desain visual dengan ide sendiri.",
        "Aku menikmati menulis cerita, artikel, atau karya kreatif.",
        "Aku tertarik membuat karya seni dalam berbagai media.",
        "Aku suka menyampaikan gagasan melalui gambar, musik, atau tulisan.",
        "Aku menikmati tugas yang memberi ruang untuk bereksperimen.",
        "Aku tertarik merancang tampilan atau pengalaman yang menarik.",
        "Aku suka mengembangkan konsep yang berbeda dari biasanya.",
        "Aku menikmati kegiatan fotografi, ilustrasi, atau produksi konten.",
        "Aku tertarik mempelajari budaya dan bentuk ekspresi seni.",
        "Aku senang mengubah ide abstrak menjadi karya."
    ],
    "S": [
        "Aku senang membantu orang memahami sesuatu yang sulit.",
        "Aku tertarik menjadi pendamping bagi orang yang membutuhkan dukungan.",
        "Aku menikmati kerja kelompok yang melibatkan banyak interaksi.",
        "Aku suka mengajar atau membagikan pengetahuan.",
        "Aku tertarik mempelajari cara manusia berpikir dan berperilaku.",
        "Aku senang mendengarkan dan memahami sudut pandang orang lain.",
        "Aku tertarik terlibat dalam kegiatan sosial masyarakat.",
        "Aku suka bekerja sama untuk menyelesaikan kebutuhan orang lain.",
        "Aku menikmati kegiatan membimbing atau melatih orang.",
        "Aku tertarik meningkatkan kualitas hidup orang lain."
    ],
    "E": [
        "Aku tertarik memimpin tim untuk mencapai tujuan.",
        "Aku senang menyampaikan ide agar orang lain tertarik.",
        "Aku tertarik merintis usaha atau proyek baru.",
        "Aku menikmati kegiatan negosiasi dan membangun kesepakatan.",
        "Aku suka mengambil keputusan dalam situasi yang menantang.",
        "Aku tertarik mengembangkan strategi bisnis atau organisasi.",
        "Aku senang mengatur kegiatan dan membagi tanggung jawab.",
        "Aku tertarik mempromosikan produk, layanan, atau gagasan.",
        "Aku menikmati tantangan mencapai target bersama tim.",
        "Aku ingin mengembangkan kemampuan kepemimpinan."
    ],
    "C": [
        "Aku senang menyusun data agar mudah dicari dan dipahami.",
        "Aku teliti saat memeriksa angka atau dokumen.",
        "Aku nyaman bekerja dengan aturan dan prosedur yang jelas.",
        "Aku suka membuat jadwal dan memastikan kegiatan berjalan teratur.",
        "Aku menikmati pekerjaan administrasi yang membutuhkan ketelitian.",
        "Aku tertarik mengelola catatan keuangan atau inventaris.",
        "Aku suka memeriksa kembali pekerjaan untuk menemukan kesalahan.",
        "Aku senang mengolah informasi dalam tabel atau basis data.",
        "Aku tertarik membuat sistem kerja yang rapi dan konsisten.",
        "Aku nyaman menyelesaikan tugas secara bertahap dan terstruktur."
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
    """Indikator kecocokan sederhana berdasarkan jarak absolut enam dimensi."""
    selisih = sum(abs(float(profil_pengguna.get(t, 0)) -
                      float(profil_jurusan.get(t, 0))) for t in NAMA_TIPE)
    return round(max(0.0, 100 - selisih / 6), 1)

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
