"""Portofolio: sistem perhitungan poin prestasi lomba akademik SMA untuk pendaftaran kuliah.

Rumus perhitungan poin per sertifikat:
    Poin = Skor_Dasar × Faktor_Penyelenggara × Faktor_Kepesertaan × Faktor_Jenjang

Keterangan:
    - Skor_Dasar (Sd): Matriks Tingkat Kejuaraan × Peringkat Juara (skala 1–100)
    - Faktor_Penyelenggara (Fp): Kementerian/Lembaga Negara (1.00), PTN/PTS/Induk Organisasi (0.85), Swasta/Komunitas (0.70)
    - Faktor_Kepesertaan (Fk): Individual (1.00), Beregu/Tim (0.75 – 0.85, default 0.80)
    - Faktor_Jenjang (Fj): Berjenjang (1.00), Non-Berjenjang/Terbuka (0.85)
    - Khusus prestasi lomba akademik (tidak mencakup keagamaan, organisasi, maupun relevansi jurusan).
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SkorDasarMatrix:
    """Matriks Skor Dasar (Sd) berdasarkan Tingkat Kejuaraan dan Peringkat Juara."""
    values: dict = field(default_factory=lambda: {
        "Internasional": {
            "Juara 1": 100,
            "Juara 2": 90,
            "Juara 3": 80,
            "Juara Harapan / Finalis": 65,
        },
        "Nasional": {
            "Juara 1": 75,
            "Juara 2": 65,
            "Juara 3": 55,
            "Juara Harapan / Finalis": 40,
        },
        "Provinsi": {
            "Juara 1": 50,
            "Juara 2": 40,
            "Juara 3": 30,
            "Juara Harapan / Finalis": 20,
        },
        "Kabupaten / Kota": {
            "Juara 1": 25,
            "Juara 2": 20,
            "Juara 3": 15,
            "Juara Harapan / Finalis": 10,
        },
    })


@dataclass
class FaktorPenyelenggara:
    values: dict = field(default_factory=lambda: {
        "Kementerian / Lembaga Negara": 1.00,
        "PTN / PTS / Induk Organisasi Resmi": 0.85,
        "Lembaga Swasta / Yayasan / Komunitas": 0.70,
    })


@dataclass
class FaktorKepesertaan:
    individual: float = 1.00
    beregu_default: float = 0.80
    beregu_min: float = 0.75
    beregu_max: float = 0.85


@dataclass
class FaktorJenjang:
    values: dict = field(default_factory=lambda: {
        "Berjenjang": 1.00,
        "Non-Berjenjang": 0.85,
    })


SKOR_DASAR_MATRIX = SkorDasarMatrix()
FAKTOR_PENYELENGGARA = FaktorPenyelenggara()
FAKTOR_KEPESERTAAN = FaktorKepesertaan()
FAKTOR_JENJANG = FaktorJenjang()

TINGKAT_OPSI = list(SKOR_DASAR_MATRIX.values.keys())
JUARA_OPSI = ["Juara 1", "Juara 2", "Juara 3", "Juara Harapan / Finalis", "Peserta / Panitia"]
PENYELENGGARA_OPSI = list(FAKTOR_PENYELENGGARA.values.keys())
JENJANG_OPSI = list(FAKTOR_JENJANG.values.keys())
KEPESERTAAN_OPSI = ["Individual", "Beregu"]


class PrestasiAkademik:
    """Mewakili satu pencapaian prestasi lomba akademik SMA untuk pendaftaran kuliah."""

    def __init__(
        self,
        judul: str,
        tingkat: str,
        juara: str,
        penyelenggara: str = "Kementerian / Lembaga Negara",
        jenis_kepesertaan: str = "Individual",
        jenjang_lomba: str = "Berjenjang",
        bobot_beregu: Optional[float] = None,
        tahun: Optional[int] = None,
        catatan: str = "",
    ):
        if tingkat not in TINGKAT_OPSI:
            raise ValueError(f"Tingkat harus salah satu dari {TINGKAT_OPSI}")
        if juara not in JUARA_OPSI:
            raise ValueError(f"Juara harus salah satu dari {JUARA_OPSI}")
        if penyelenggara not in PENYELENGGARA_OPSI:
            raise ValueError(f"Penyelenggara harus salah satu dari {PENYELENGGARA_OPSI}")
        if jenis_kepesertaan not in KEPESERTAAN_OPSI:
            raise ValueError(f"Jenis kepesertaan harus salah satu dari {KEPESERTAAN_OPSI}")
        if jenjang_lomba not in JENJANG_OPSI:
            raise ValueError(f"Jenjang lomba harus salah satu dari {JENJANG_OPSI}")
        if bobot_beregu is not None and not (FAKTOR_KEPESERTAAN.beregu_min <= bobot_beregu <= FAKTOR_KEPESERTAAN.beregu_max):
            raise ValueError(
                f"Bobot beregu harus berada di rentang {FAKTOR_KEPESERTAAN.beregu_min} - {FAKTOR_KEPESERTAAN.beregu_max}"
            )
        if tahun is not None and (tahun < 2000 or tahun > 2100):
            raise ValueError("Tahun harus antara 2000 dan 2100")

        self.judul = judul
        self.kategori = "Akademik"
        self.tingkat = tingkat
        self.juara = juara
        self.penyelenggara = penyelenggara
        self.jenis_kepesertaan = jenis_kepesertaan
        self.jenjang_lomba = jenjang_lomba
        self.bobot_beregu = bobot_beregu
        self.tahun = tahun
        self.catatan = catatan

    @property
    def skor_dasar(self) -> int:
        if self.juara == "Peserta / Panitia" or self.tingkat == "Sekolah / Kecamatan":
            return 0
        return SKOR_DASAR_MATRIX.values[self.tingkat][self.juara]

    @property
    def faktor_penyelenggara(self) -> float:
        return FAKTOR_PENYELENGGARA.values[self.penyelenggara]

    @property
    def faktor_kepesertaan(self) -> float:
        if self.jenis_kepesertaan == "Individual":
            return FAKTOR_KEPESERTAAN.individual
        if self.bobot_beregu is not None:
            return self.bobot_beregu
        return FAKTOR_KEPESERTAAN.beregu_default

    @property
    def faktor_jenjang(self) -> float:
        return FAKTOR_JENJANG.values[self.jenjang_lomba]

    @property
    def faktor_pengali_total(self) -> float:
        return (
            self.faktor_penyelenggara
            * self.faktor_kepesertaan
            * self.faktor_jenjang
        )

    @property
    def poin(self) -> float:
        return round(self.skor_dasar * self.faktor_pengali_total, 2)

    def rincian_poin(self) -> dict:
        return {
            "judul": self.judul,
            "kategori": self.kategori,
            "tingkat": self.tingkat,
            "juara": self.juara,
            "penyelenggara": self.penyelenggara,
            "jenis_kepesertaan": self.jenis_kepesertaan,
            "jenjang_lomba": self.jenjang_lomba,
            "tahun": self.tahun,
            "skor_dasar": self.skor_dasar,
            "faktor_penyelenggara": self.faktor_penyelenggara,
            "faktor_kepesertaan": self.faktor_kepesertaan,
            "faktor_jenjang": self.faktor_jenjang,
            "faktor_pengali_total": round(self.faktor_pengali_total, 4),
            "poin_akhir": self.poin,
        }

    def to_dict(self) -> dict:
        return {
            "judul": self.judul,
            "kategori": self.kategori,
            "tingkat": self.tingkat,
            "juara": self.juara,
            "penyelenggara": self.penyelenggara,
            "jenis_kepesertaan": self.jenis_kepesertaan,
            "jenjang_lomba": self.jenjang_lomba,
            "bobot_beregu": self.bobot_beregu,
            "tahun": self.tahun,
            "catatan": self.catatan,
        }

    @classmethod
    def dari_dict(cls, data: dict) -> "PrestasiAkademik":
        return cls(
            judul=data["judul"],
            tingkat=data["tingkat"],
            juara=data.get("juara", "Peserta / Panitia"),
            penyelenggara=data.get("penyelenggara", "Kementerian / Lembaga Negara"),
            jenis_kepesertaan=data.get("jenis_kepesertaan", "Individual"),
            jenjang_lomba=data.get("jenjang_lomba", "Berjenjang"),
            bobot_beregu=data.get("bobot_beregu"),
            tahun=data.get("tahun"),
            catatan=data.get("catatan", ""),
        )

    def __eq__(self, other):
        if not isinstance(other, PrestasiAkademik):
            return NotImplemented
        return (
            self.judul == other.judul
            and self.tingkat == other.tingkat
            and self.juara == other.juara
            and self.penyelenggara == other.penyelenggara
            and self.jenis_kepesertaan == other.jenis_kepesertaan
            and self.jenjang_lomba == other.jenjang_lomba
            and self.tahun == other.tahun
        )

    def __repr__(self):
        return f"PrestasiAkademik({self.judul!r}, {self.tingkat}, {self.juara})"


class PortofolioAkademik:
    TINGKAT = TINGKAT_OPSI
    JUARA = JUARA_OPSI
    PENYELENGGARA = PENYELENGGARA_OPSI
    JENJANG = JENJANG_OPSI
    KEPESERTAAN = KEPESERTAAN_OPSI

    def __init__(self, maks_sertifikat: Optional[int] = 3):
        self.__daftar: list[PrestasiAkademik] = []
        self.maks_sertifikat = maks_sertifikat

    def tambah(self, prestasi: PrestasiAkademik):
        if not isinstance(prestasi, PrestasiAkademik):
            raise TypeError("Data yang ditambahkan harus berupa PrestasiAkademik.")
        self.__daftar.append(prestasi)

    def hapus(self, prestasi: PrestasiAkademik) -> bool:
        """Menghapus satu pencapaian. Mengembalikan False jika tidak ditemukan."""
        if prestasi not in self.__daftar:
            return False
        self.__daftar.remove(prestasi)
        return True

    def daftar(self) -> list[PrestasiAkademik]:
        return list(self.__daftar)

    def daftar_terbaik(self, limit: Optional[int] = None) -> list[PrestasiAkademik]:
        """Mengambil daftar prestasi dengan poin tertinggi (default maksimal 3 terbaik)."""
        batas = limit if limit is not None else self.maks_sertifikat
        urut = sorted(self.__daftar, key=lambda p: p.poin, reverse=True)
        return urut[:batas] if batas is not None else urut

    def jumlah(self) -> int:
        return len(self.__daftar)

    def total_poin(self, hanya_terbaik: bool = True) -> float:
        """Menghitung total poin prestasi (default mengambil 3 sertifikat terbaik)."""
        sumber = self.daftar_terbaik() if hanya_terbaik else self.__daftar
        return round(sum(p.poin for p in sumber), 2)

    def rata_rata_poin(self, hanya_terbaik: bool = True) -> float:
        """Menghitung rata-rata poin prestasi."""
        sumber = self.daftar_terbaik() if hanya_terbaik else self.__daftar
        if not sumber:
            return 0.0
        return round(sum(p.poin for p in sumber) / len(sumber), 2)

    def total_skor_dasar(self, hanya_terbaik: bool = True) -> int:
        """Total skor dasar tanpa faktor pengali tambahan."""
        sumber = self.daftar_terbaik() if hanya_terbaik else self.__daftar
        return sum(p.skor_dasar for p in sumber)

    def hitung_nilai_akhir_seleksi(
        self,
        nilai_rapor: float,
        bobot_rapor: float = 0.60,
        bobot_prestasi: float = 0.40,
        hanya_terbaik: bool = True,
    ) -> float:
        """Menggabungkan rata-rata poin prestasi (skala 0–100) dengan nilai rapor."""
        if round(bobot_rapor + bobot_prestasi, 4) != 1.0:
            raise ValueError("Jumlah bobot_rapor dan bobot_prestasi harus sama dengan 1.0")
        nilai_prestasi = self.rata_rata_poin(hanya_terbaik=hanya_terbaik)
        return round((nilai_rapor * bobot_rapor) + (nilai_prestasi * bobot_prestasi), 2)

    def ringkasan_per_tingkat(self) -> dict:
        hasil = {}
        for p in self.__daftar:
            hasil.setdefault(p.tingkat, {"jumlah": 0, "poin": 0.0})
            hasil[p.tingkat]["jumlah"] += 1
            hasil[p.tingkat]["poin"] += p.poin
        return {k: {"jumlah": v["jumlah"], "poin": round(v["poin"], 2)} for k, v in hasil.items()}

    def to_dict(self) -> list[dict]:
        return [p.to_dict() for p in self.__daftar]

    @classmethod
    def dari_dict(cls, data: list[dict], maks_sertifikat: Optional[int] = 3) -> "PortofolioAkademik":
        obj = cls(maks_sertifikat=maks_sertifikat)
        for d in data:
            obj.tambah(PrestasiAkademik.dari_dict(d))
        return obj
