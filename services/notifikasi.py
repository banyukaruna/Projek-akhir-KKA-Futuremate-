"""Pengingat otomatis dari deadline tugas, ujian, dan target."""
from datetime import date


class Notifikasi:
    @staticmethod
    def _label(sisa):
        if sisa < 0:
            return f"TERLAMBAT {-sisa} hari"
        if sisa == 0:
            return "HARI INI"
        if sisa == 1:
            return "BESOK"
        return f"{sisa} hari lagi"

    @classmethod
    def buat(cls, murid, hari_ini=None):
        hari_ini = hari_ini or date.today()
        daftar = []  # (sisa, teks) supaya bisa diurutkan paling mendesak dulu
        for i in murid.item_aktif(hari_ini):
            sisa = i.sisa_hari(hari_ini)
            if sisa <= 3:
                daftar.append((sisa, f"{i.jenis()} '{i.judul}' ({i.mapel}): {cls._label(sisa)}"))
        for t in murid.targets:
            if t.deadline:
                sisa = (t.deadline - hari_ini).days
                if sisa <= 7:
                    daftar.append((sisa, f"{t.jenis()} '{t.nama}': pendaftaran {cls._label(sisa)}"))
        for hari, items in murid.hari_padat(hari_ini=hari_ini).items():
            daftar.append(((hari - hari_ini).days,
                           f"Hari padat {hari}: {len(items)} deadline sekaligus, cicil dari sekarang!"))
        return [teks for _, teks in sorted(daftar)]
