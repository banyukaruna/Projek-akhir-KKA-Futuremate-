"""Portofolio khusus prestasi lomba akademik.

Rumus:
Poin = Skor Dasar x Faktor Penyelenggara x Faktor Kepesertaan x Faktor Jenjang.

Skor ini merupakan estimasi internal FutureMate, bukan nilai resmi seleksi perguruan tinggi.
"""

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real
from typing import Optional


@dataclass
class SkorDasarMatrix:
    values: dict = field(default_factory=lambda: {
        "Internasional": {
            "Juara 1": 100, "Juara 2": 90, "Juara 3": 80,
            "Juara Harapan / Finalis": 65,
        },
        "Nasional": {
            "Juara 1": 75, "Juara 2": 65, "Juara 3": 55,
            "Juara Harapan / Finalis": 40,
        },
        "Provinsi": {
            "Juara 1": 50, "Juara 2": 40, "Juara 3": 30,
            "Juara Harapan / Finalis": 20,
        },
        "Kabupaten / Kota": {
            "Juara 1": 25, "Juara 2": 20, "Juara 3": 15,
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
    individu: float = 1.00
    tim: float = 0.80


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

TINGKAT_OPSI = list(SKOR_DASAR_MATRIX.values)
JUARA_OPSI = [
    "Juara 1", "Juara 2", "Juara 3",
    "Juara Harapan / Finalis", "Peserta / Panitia",
]
PENYELENGGARA_OPSI = list(FAKTOR_PENYELENGGARA.values)
JENJANG_OPSI = list(FAKTOR_JENJANG.values)
KEPESERTAAN_OPSI = ["Individu", "Tim"]


class PrestasiAkademik:
    """Satu catatan prestasi lomba akademik."""

    def __init__(
        self,
        judul: str,
        tingkat: str,
        juara: str,
        penyelenggara: str = "Kementerian / Lembaga Negara",
        jenis_kepesertaan: str = "Individu",
        jenjang_lomba: str = "Berjenjang",
        bobot_beregu: Optional[float] = None,
        tahun: Optional[int] = None,
        catatan: str = "",
        data_lama: bool = False,
    ):
        if not isinstance(judul, str) or not judul.strip():
            raise ValueError("Nama prestasi wajib diisi.")
        if tingkat not in TINGKAT_OPSI:
            raise ValueError(f"Tingkat harus salah satu dari {TINGKAT_OPSI}")
        if juara not in JUARA_OPSI:
            raise ValueError(f"Peringkat harus salah satu dari {JUARA_OPSI}")
        if penyelenggara not in PENYELENGGARA_OPSI:
            raise ValueError(f"Penyelenggara harus salah satu dari {PENYELENGGARA_OPSI}")
        jenis_kepesertaan = {"Individual": "Individu", "Beregu": "Tim"}.get(
            jenis_kepesertaan, jenis_kepesertaan
        )
        if jenis_kepesertaan not in KEPESERTAAN_OPSI:
            raise ValueError(f"Jenis kepesertaan harus salah satu dari {KEPESERTAAN_OPSI}")
        if jenjang_lomba not in JENJANG_OPSI:
            raise ValueError(f"Jenjang lomba harus salah satu dari {JENJANG_OPSI}")
        # Parameter bobot_beregu tetap diterima untuk kompatibilitas data lama.
        # Faktor kepesertaan Tim selalu 0.80.
        if tahun is not None:
            if isinstance(tahun, bool) or not isinstance(tahun, int):
                raise ValueError("Tahun harus berupa bilangan bulat.")
            if not 2000 <= tahun <= 2100:
                raise ValueError("Tahun harus antara 2000 dan 2100.")
        if not isinstance(catatan, str):
            raise ValueError("Catatan harus berupa teks.")

        self.judul = judul.strip()
        self.kategori = "Akademik"
        self.tingkat = tingkat
        self.juara = juara
        self.penyelenggara = penyelenggara
        self.jenis_kepesertaan = jenis_kepesertaan
        self.jenjang_lomba = jenjang_lomba
        self.bobot_beregu = None
        self.tahun = tahun
        self.catatan = catatan.strip()
        self.data_lama = bool(data_lama)

    @property
    def skor_dasar(self) -> int:
        if self.juara == "Peserta / Panitia":
            return 0
        return SKOR_DASAR_MATRIX.values[self.tingkat][self.juara]

    @property
    def faktor_penyelenggara(self) -> float:
        return FAKTOR_PENYELENGGARA.values[self.penyelenggara]

    @property
    def faktor_kepesertaan(self) -> float:
        if self.jenis_kepesertaan == "Individu":
            return FAKTOR_KEPESERTAAN.individu
        return FAKTOR_KEPESERTAAN.tim

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
            "data_lama": self.data_lama,
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
            "tahun": self.tahun,
            "catatan": self.catatan,
            "data_lama": self.data_lama,
        }

    @classmethod
    def dari_dict(cls, data: dict) -> "PrestasiAkademik":
        return cls(
            judul=data["judul"],
            tingkat=data["tingkat"],
            juara=data.get("juara", "Peserta / Panitia"),
            penyelenggara=data.get("penyelenggara", "Kementerian / Lembaga Negara"),
            jenis_kepesertaan=data.get("jenis_kepesertaan", "Individu"),
            jenjang_lomba=data.get("jenjang_lomba", "Berjenjang"),
            bobot_beregu=data.get("bobot_beregu"),
            tahun=data.get("tahun"),
            catatan=data.get("catatan", ""),
            data_lama=data.get("data_lama", False),
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
            and self.catatan == other.catatan
            and self.data_lama == other.data_lama
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
        if maks_sertifikat is not None and (
            isinstance(maks_sertifikat, bool)
            or not isinstance(maks_sertifikat, int)
            or maks_sertifikat < 0
        ):
            raise ValueError("Batas sertifikat harus bilangan bulat nol atau lebih.")
        self.__daftar: list[PrestasiAkademik] = []
        self.maks_sertifikat = maks_sertifikat

    def tambah(self, prestasi: PrestasiAkademik):
        if not isinstance(prestasi, PrestasiAkademik):
            raise TypeError("Data yang ditambahkan harus berupa PrestasiAkademik.")
        self.__daftar.append(prestasi)

    def hapus(self, prestasi: PrestasiAkademik) -> bool:
        if prestasi not in self.__daftar:
            return False
        self.__daftar.remove(prestasi)
        return True

    def daftar(self) -> list[PrestasiAkademik]:
        return list(self.__daftar)

    def daftar_terbaik(self, limit: Optional[int] = None) -> list[PrestasiAkademik]:
        batas = self.maks_sertifikat if limit is None else limit
        if batas is not None and (
            isinstance(batas, bool) or not isinstance(batas, int) or batas < 0
        ):
            raise ValueError("Limit harus bilangan bulat nol atau lebih.")
        urut = sorted(self.__daftar, key=lambda p: p.poin, reverse=True)
        return urut[:batas] if batas is not None else urut

    def jumlah(self) -> int:
        return len(self.__daftar)

    def total_poin(self, hanya_terbaik: bool = True) -> float:
        sumber = self.daftar_terbaik() if hanya_terbaik else self.__daftar
        return round(sum(p.poin for p in sumber), 2)

    def rata_rata_poin(self, hanya_terbaik: bool = True) -> float:
        sumber = self.daftar_terbaik() if hanya_terbaik else self.__daftar
        if not sumber:
            return 0.0
        return round(sum(p.poin for p in sumber) / len(sumber), 2)

    def total_skor_dasar(self, hanya_terbaik: bool = True) -> int:
        sumber = self.daftar_terbaik() if hanya_terbaik else self.__daftar
        return sum(p.skor_dasar for p in sumber)

    def hitung_nilai_akhir_seleksi(
        self,
        nilai_rapor: float,
        bobot_rapor: float = 0.60,
        bobot_prestasi: float = 0.40,
        hanya_terbaik: bool = True,
    ) -> float:
        nilai = (nilai_rapor, bobot_rapor, bobot_prestasi)
        if any(
            isinstance(x, bool) or not isinstance(x, Real) or not isfinite(float(x))
            for x in nilai
        ):
            raise ValueError("Nilai dan bobot harus berupa angka yang valid.")
        if not 0 <= nilai_rapor <= 100:
            raise ValueError("Nilai rapor harus berada pada rentang 0 sampai 100.")
        if bobot_rapor < 0 or bobot_prestasi < 0:
            raise ValueError("Bobot tidak boleh negatif.")
        if abs((bobot_rapor + bobot_prestasi) - 1.0) > 0.0001:
            raise ValueError("Jumlah bobot_rapor dan bobot_prestasi harus sama dengan 1.0")
        nilai_prestasi = self.rata_rata_poin(hanya_terbaik=hanya_terbaik)
        return round((nilai_rapor * bobot_rapor) + (nilai_prestasi * bobot_prestasi), 2)

    def ringkasan_per_tingkat(self) -> dict:
        hasil = {}
        for prestasi in self.__daftar:
            data = hasil.setdefault(prestasi.tingkat, {"jumlah": 0, "poin": 0.0})
            data["jumlah"] += 1
            data["poin"] += prestasi.poin
        return {
            tingkat: {"jumlah": data["jumlah"], "poin": round(data["poin"], 2)}
            for tingkat, data in hasil.items()
        }

    def to_dict(self) -> list[dict]:
        return [prestasi.to_dict() for prestasi in self.__daftar]

    @classmethod
    def dari_dict(
        cls, data: list[dict], maks_sertifikat: Optional[int] = 3
    ) -> "PortofolioAkademik":
        if not isinstance(data, list):
            raise ValueError("Data portofolio harus berupa daftar.")
        obj = cls(maks_sertifikat=maks_sertifikat)
        for item in data:
            # Migrasi catatan dari format lama. Peringkat tidak diketahui,
            # jadi catatan diberi nol poin sampai pengguna memperbaruinya.
            if "juara" not in item:
                tingkat_lama = item.get("tingkat", "Kabupaten / Kota")
                tingkat_baru = {
                    "Sekolah": "Kabupaten / Kota",
                    "Kota": "Kabupaten / Kota",
                }.get(tingkat_lama, tingkat_lama)
                if tingkat_baru not in TINGKAT_OPSI:
                    tingkat_baru = "Kabupaten / Kota"
                kategori_lama = item.get("kategori", "Tidak diketahui")
                item = {
                    "judul": item.get("judul", "Prestasi lama"),
                    "tingkat": tingkat_baru,
                    "juara": "Peserta / Panitia",
                    "penyelenggara": "Kementerian / Lembaga Negara",
                    "jenis_kepesertaan": "Individual",
                    "jenjang_lomba": "Berjenjang",
                    "tahun": item.get("tahun"),
                    "catatan": (
                        "Data lama belum memiliki rincian lomba. "
                        f"Kategori sebelumnya: {kategori_lama}. Perbarui data ini."
                    ),
                    "data_lama": True,
                }
            obj.tambah(PrestasiAkademik.dari_dict(item))
        return obj
