"""FutureMate - aplikasi CLI yang menghubungkan belajar hari ini dengan target masa depan.
Jalankan:  python main.py
"""
from datetime import date, timedelta
from pathlib import Path

from exceptions import DuplikatError, FutureMateError
from models.item import SesiBelajar, Tugas, Ujian
from models.pengguna import Guru, Murid
from models.portofolio import Portofolio, Prestasi
from models.target import Beasiswa, Lomba
from services.notifikasi import Notifikasi
from services.penyimpanan import Penyimpanan
from services.sistem_kesiapan import SistemKesiapan
from services.tes_minat import NAMA_TIPE, PERTANYAAN, ProfilMinat

DATA = Path(__file__).parent / "data"
kesiapan = SistemKesiapan()


# ---------- helper input ----------
def input_teks(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("Tidak boleh kosong.")


def input_angka(prompt, lo, hi, tipe=int):
    while True:
        try:
            v = tipe(input(prompt).strip().replace(",", "."))
            if lo <= v <= hi:
                return v
            print(f"Masukkan angka {lo}-{hi}.")
        except ValueError:
            print("Input harus berupa angka.")


def input_tanggal(prompt):
    while True:
        s = input(f"{prompt} (YYYY-MM-DD atau +N untuk N hari lagi): ").strip()
        try:
            if s.startswith("+"):
                return date.today() + timedelta(days=int(s[1:]))
            return date.fromisoformat(s)
        except ValueError:
            print("Format tanggal salah.")


def pilih(daftar, label, judul="Pilih nomor"):
    if not daftar:
        print("  (kosong)")
        return None
    for i, x in enumerate(daftar, 1):
        print(f"  {i}. {label(x)}")
    n = input_angka(f"{judul} (0 = batal): ", 0, len(daftar))
    return daftar[n - 1] if n else None


def jalankan_menu(judul, opsi):
    """opsi: list of (label, fungsi). Error aplikasi ditangkap agar program tidak crash."""
    while True:
        print(f"\n=== {judul} ===")
        for i, (label, _) in enumerate(opsi, 1):
            print(f"{i}. {label}")
        print("0. Kembali")
        n = input_angka("Pilih: ", 0, len(opsi))
        if n == 0:
            return
        try:
            opsi[n - 1][1]()
        except FutureMateError as e:
            print(f"[!] {e}")


def sisa_label(item):
    return Notifikasi._label(item.sisa_hari())


def tampil_item(i):
    return f"[{i.prioritas().value:<8}] {i.jenis():<6} {i.judul} ({i.mapel}) - {i.deadline}, {sisa_label(i)}"


# ---------- dashboard ----------
def dashboard(m):
    hasil = kesiapan.hitung(m)
    print(f"\nSkor Kesiapan Masa Depan {m.nama}: {hasil['total']}/100 ({kesiapan.kategori(hasil['total'])})")
    for k, v in hasil["komponen"].items():
        print(f"  {k:<18} {v:>5}/{SistemKesiapan.BOBOT[k]}")
    print("\nPengingat:")
    for n in Notifikasi.buat(m) or ["Tidak ada deadline dekat."]:
        print(f"  - {n}")
    print("\nRoadmap saran:")
    for i, s in enumerate(kesiapan.roadmap(m), 1):
        print(f"  {i}. {s}")


# ---------- tugas & jadwal ----------
def tambah_item(m, kelas):
    judul = input_teks("Judul: ")
    mapel = input_teks("Mata pelajaran: ").title()
    deadline = input_tanggal("Tanggal")
    if kelas is Tugas:
        item = Tugas(judul, mapel, deadline, input_angka("Tingkat kesulitan (1-5): ", 1, 5))
    elif kelas is SesiBelajar:
        item = SesiBelajar(judul, mapel, deadline, input_angka("Durasi (menit): ", 15, 480))
    else:
        item = Ujian(judul, mapel, deadline)
    m.tambah_item(item)
    print(f"Tersimpan. Prioritas: {item.prioritas().value}")


def lihat_item(m):
    aktif = m.item_aktif()
    print("\nDaftar (urut prioritas):")
    for i in aktif:
        print("  " + tampil_item(i))
    if not aktif:
        print("  Tidak ada tugas aktif.")


def selesaikan_item(m):
    item = pilih(m.item_aktif(), tampil_item)
    if item:
        item.tandai_selesai()
        print("Selesai tepat waktu!" if item.tepat_waktu() else "Ditandai selesai (terlambat).")


def lihat_hari_padat(m):
    padat = m.hari_padat()
    if not padat:
        print("Tidak ada hari padat (kurang dari 3 deadline di hari yang sama).")
    for hari, items in padat.items():
        print(f"{hari}: " + ", ".join(i.judul for i in items))


def menu_tugas(m):
    jalankan_menu("Tugas & Jadwal", [
        ("Tambah tugas", lambda: tambah_item(m, Tugas)),
        ("Tambah ujian", lambda: tambah_item(m, Ujian)),
        ("Tambah sesi belajar", lambda: tambah_item(m, SesiBelajar)),
        ("Lihat daftar prioritas", lambda: lihat_item(m)),
        ("Tandai selesai", lambda: selesaikan_item(m)),
        ("Cek hari padat", lambda: lihat_hari_padat(m)),
    ])


# ---------- nilai ----------
def tambah_nilai(m):
    mapel = input_teks("Mata pelajaran: ")
    m.nilai.tambah(mapel, input_angka("Nilai (0-100): ", 0, 100, float))
    print("Nilai tersimpan.")


def ringkasan_nilai(m):
    mapel = m.nilai.daftar_mapel()
    for mp in mapel:
        print(f"  {mp:<18} rata-rata {m.nilai.rata_mapel(mp):5.1f}  tren: {m.nilai.tren(mp)}")
    print(f"  Rata-rata keseluruhan: {m.nilai.rata_rata():.1f}" if mapel else "  Belum ada nilai.")


def menu_nilai(m):
    jalankan_menu("Nilai Akademik", [("Tambah nilai", lambda: tambah_nilai(m)),
                                     ("Ringkasan & tren", lambda: ringkasan_nilai(m))])


# ---------- target masa depan ----------
def pilih_jurusan(m, katalog):
    j = pilih(katalog, lambda x: f"{x.nama_jurusan} - {x.kampus} (rata-rata min {x.rata_min})")
    if j:
        if any(t.nama == j.nama for t in m.targets):
            raise DuplikatError("Target itu sudah ada.")
        m.tambah_target(j)
        print("Target jurusan ditambahkan.")


def tambah_beasiswa(m):
    m.tambah_target(Beasiswa(input_teks("Nama beasiswa: "), input_tanggal("Deadline"),
                             input_angka("Rata-rata minimal: ", 0, 100, float),
                             input_angka("Jumlah prestasi minimal: ", 0, 20)))
    print("Beasiswa ditambahkan.")


def tambah_lomba(m):
    m.tambah_target(Lomba(input_teks("Nama lomba: "), input_tanggal("Deadline"),
                          input_teks("Mapel terkait: ").title(),
                          input_angka("Nilai mapel minimal: ", 0, 100, float)))
    print("Lomba ditambahkan.")


def gap_analysis(m):
    if not m.targets:
        print("Belum ada target.")
    for t in m.targets:
        print(f"\n{t.jenis()}: {t.nama}  (kecocokan {t.kecocokan(m) * 100:.0f}%)")
        for s in t.cek_syarat(m):
            print(f"  [{'OK' if s.terpenuhi else 'X '}] {s.deskripsi}"
                  + ("" if s.terpenuhi else f"  -> kurang {s.selisih:.1f}"))


def hapus_target(m):
    t = pilih(m.targets, lambda x: f"{x.jenis()}: {x.nama}")
    if t:
        m.targets.remove(t)
        print("Target dihapus.")


def menu_target(m, katalog):
    jalankan_menu("Target Masa Depan", [
        ("Pilih jurusan impian", lambda: pilih_jurusan(m, katalog)),
        ("Tambah beasiswa", lambda: tambah_beasiswa(m)),
        ("Tambah lomba", lambda: tambah_lomba(m)),
        ("Gap analysis semua target", lambda: gap_analysis(m)),
        ("Hapus target", lambda: hapus_target(m)),
    ])


# ---------- tes minat ----------
def tes_minat(m, katalog):
    print("\nJawab 1 (sangat tidak setuju) sampai 5 (sangat setuju).")
    jawaban = [input_angka(f"{i}. {teks} ", 1, 5) for i, (teks, _) in enumerate(PERTANYAAN, 1)]
    m.profil_minat = ProfilMinat.hitung(jawaban)
    print("\nTipe minat terkuatmu:")
    for t in ProfilMinat.tipe_teratas(m.profil_minat):
        print(f"  {NAMA_TIPE[t]} - skor {m.profil_minat[t]}/10")
    print("\n3 jurusan yang paling cocok:")
    for j, skor in ProfilMinat.rekomendasikan(m.profil_minat, katalog):
        print(f"  {j.nama_jurusan} ({j.kampus}) - kecocokan minat {skor:.0f}%")


# ---------- portofolio ----------
def tambah_prestasi(m):
    judul = input_teks("Judul prestasi/sertifikat: ")
    kategori = input_teks("Kategori (lomba/organisasi/kursus/proyek): ")
    tingkat = pilih(Portofolio.TINGKAT, str, "Tingkat")
    if tingkat:
        m.portofolio.tambah(Prestasi(judul, kategori, tingkat, input_angka("Tahun: ", 2000, 2100)))
        print("Prestasi ditambahkan.")


def lihat_portofolio(m):
    for p in m.portofolio.daftar():
        print(f"  {p.tahun} | {p.judul} ({p.kategori}, {p.tingkat}) +{p.poin} poin")
    print(f"  Total poin portofolio: {m.portofolio.total_poin()}" if m.portofolio.jumlah()
          else "  Portofolio masih kosong.")


def menu_portofolio(m):
    jalankan_menu("Portofolio", [("Tambah prestasi", lambda: tambah_prestasi(m)),
                                 ("Lihat portofolio", lambda: lihat_portofolio(m))])


# ---------- sesi pengguna ----------
def sesi_murid(m, katalog):
    jalankan_menu(f"FutureMate - {m.nama} ({m.kelas})", [
        ("Dashboard kesiapan & roadmap", lambda: dashboard(m)),
        ("Tugas & jadwal belajar", lambda: menu_tugas(m)),
        ("Nilai akademik", lambda: menu_nilai(m)),
        ("Target masa depan", lambda: menu_target(m, katalog)),
        ("Tes minat", lambda: tes_minat(m, katalog)),
        ("Portofolio", lambda: menu_portofolio(m)),
    ])


def sesi_guru(nama, daftar):
    guru = Guru(nama)
    print(f"\nHalo {guru.peran()} {guru.nama}. Hak akses: {', '.join(guru.hak_akses())}")
    if not daftar:
        print("Belum ada data murid.")
    for m in sorted(daftar.values(), key=lambda x: kesiapan.hitung(x)["total"], reverse=True):
        total = kesiapan.hitung(m)["total"]
        print(f"  {m.nama:<15} {m.kelas:<12} skor {total:>3}  ({kesiapan.kategori(total)})")


def buat_demo(katalog):
    """Data contoh agar fitur mudah didemokan."""
    m, hari = Murid("Demo", "XII IPA 1"), date.today()
    for mapel, daftar in {"Matematika": [78, 74, 68], "Fisika": [80, 82], "Bahasa Inggris": [85, 88],
                          "Biologi": [78]}.items():
        for n in daftar:
            m.nilai.tambah(mapel, n)
    tugas_lama = Tugas("Laporan Bab 1", "Fisika", hari - timedelta(days=3), 3)
    tugas_lama.tandai_selesai(hari - timedelta(days=4))
    for item in (tugas_lama,
                 Tugas("Laporan Praktikum", "Fisika", hari + timedelta(days=2), 4),
                 Tugas("Esai Sejarah", "Sejarah", hari + timedelta(days=2), 2),
                 Tugas("Soal Integral", "Matematika", hari + timedelta(days=2), 5),
                 Ujian("UTS Matematika", "Matematika", hari + timedelta(days=6)),
                 Tugas("Resensi Buku", "Bahasa Indonesia", hari - timedelta(days=1), 2)):
        m.tambah_item(item)
    m.portofolio.tambah(Prestasi("Juara 2 Lomba Coding", "lomba", "Kota", hari.year))
    m.tambah_target(next(j for j in katalog if j.nama_jurusan == "Teknik Informatika"))
    m.tambah_target(Lomba("OSN Matematika", hari + timedelta(days=5), "Matematika", 80))
    return m


def main():
    penyimpanan = Penyimpanan(DATA / "data.json", DATA / "jurusan.json")
    try:
        katalog, daftar = penyimpanan.muat_katalog(), penyimpanan.muat()
    except FutureMateError as e:
        print(f"[!] {e}")
        return
    print("=" * 44 + "\n  FUTUREMATE - belajar hari ini, siap masa depan\n" + "=" * 44)
    try:
        while True:
            print("\n1. Masuk sebagai Murid\n2. Masuk sebagai Guru\n3. Buat data demo\n0. Simpan & keluar")
            pilihan = input_angka("Pilih: ", 0, 3)
            if pilihan == 0:
                break
            if pilihan == 3:
                daftar["demo"] = buat_demo(katalog)
                print("Data demo dibuat. Masuk sebagai Murid dengan nama: Demo")
                continue
            nama = input_teks("Nama: ")
            if pilihan == 2:
                sesi_guru(nama, daftar)
                continue
            if nama.lower() not in daftar:
                daftar[nama.lower()] = Murid(nama, input_teks("Kelas: "))
                print("Akun baru dibuat.")
            sesi_murid(daftar[nama.lower()], katalog)
            penyimpanan.simpan(daftar)
    except (EOFError, KeyboardInterrupt):
        print("\nKeluar...")
    finally:
        penyimpanan.simpan(daftar)
        print("Data tersimpan. Sampai jumpa!")


if __name__ == "__main__":
    main()
