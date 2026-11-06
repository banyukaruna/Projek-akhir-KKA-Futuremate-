"""Skor Kesiapan Masa Depan (0-100) dan roadmap saran langkah berikutnya."""
from datetime import date


class SistemKesiapan:
    BOBOT = {"Nilai akademik": 30, "Ketepatan tugas": 25, "Portofolio": 20, "Kecocokan target": 25}
    POIN_PORTOFOLIO_PENUH = 15

    def hitung(self, murid):
        relevan = [i for i in murid.items if i.selesai or i.sisa_hari() < 0]
        tepat = sum(1 for i in relevan if i.tepat_waktu())
        rasio = {
            "Nilai akademik": murid.nilai.rata_rata() / 100,
            "Ketepatan tugas": tepat / len(relevan) if relevan else 0.5,  # netral jika belum ada data
            "Portofolio": min(murid.portofolio.total_poin() / self.POIN_PORTOFOLIO_PENUH, 1),
            "Kecocokan target": (sum(t.kecocokan(murid) for t in murid.targets) / len(murid.targets))
            if murid.targets else 0,
        }
        komponen = {k: round(rasio[k] * self.BOBOT[k], 1) for k in self.BOBOT}
        return {"komponen": komponen, "total": round(sum(komponen.values()))}

    @staticmethod
    def kategori(total):
        if total >= 70:
            return "Siap"
        if total >= 40:
            return "Cukup siap"
        return "Perlu banyak persiapan"

    def roadmap(self, murid, hari_ini=None):
        hari_ini = hari_ini or date.today()
        saran = []
        if not murid.targets:
            saran.append("Kamu belum punya target. Ikuti Tes Minat lalu pilih jurusan impian.")
        for t in murid.targets:
            for s in t.cek_syarat(murid):
                if not s.terpenuhi:
                    saran.append(f"[{t.nama}] {s.deskripsi} -> kurang {s.selisih:.1f}")
        for mapel in murid.nilai.daftar_mapel():
            if murid.nilai.tren(mapel) == "turun":
                saran.append(f"Nilai {mapel} cenderung turun: jadwalkan sesi belajar tambahan.")
        terlambat = [i for i in murid.item_aktif(hari_ini) if i.sisa_hari(hari_ini) < 0]
        if terlambat:
            saran.append(f"Ada {len(terlambat)} item terlambat: selesaikan dulu agar skor ketepatan naik.")
        if murid.hari_padat(hari_ini=hari_ini):
            saran.append("Ada hari padat deadline: mulai cicil tugas dari hari ini.")
        if murid.portofolio.total_poin() < 5:
            saran.append("Portofolio masih sedikit: ikut lomba, organisasi, atau kursus bersertifikat.")
        return saran or ["Pertahankan! Terus jaga nilai dan ketepatan waktumu."]
