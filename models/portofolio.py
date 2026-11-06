"""Portofolio: komposisi dari banyak Prestasi."""


class Prestasi:
    BOBOT = {"Sekolah": 1, "Kota": 2, "Provinsi": 3, "Nasional": 4, "Internasional": 5}

    def __init__(self, judul, kategori, tingkat, tahun):
        if tingkat not in self.BOBOT:
            raise ValueError(f"Tingkat harus salah satu dari {list(self.BOBOT)}")
        self.judul, self.kategori, self.tingkat, self.tahun = judul, kategori, tingkat, tahun

    @property
    def poin(self):
        return self.BOBOT[self.tingkat]

    def to_dict(self):
        return {"judul": self.judul, "kategori": self.kategori,
                "tingkat": self.tingkat, "tahun": self.tahun}


class Portofolio:
    TINGKAT = list(Prestasi.BOBOT)

    def __init__(self):
        self.__daftar = []

    def tambah(self, prestasi):
        self.__daftar.append(prestasi)

    def daftar(self):
        return list(self.__daftar)

    def jumlah(self):
        return len(self.__daftar)

    def total_poin(self):
        return sum(p.poin for p in self.__daftar)

    def to_dict(self):
        return [p.to_dict() for p in self.__daftar]

    @classmethod
    def dari_dict(cls, data):
        obj = cls()
        for d in data:
            obj.tambah(Prestasi(d["judul"], d["kategori"], d["tingkat"], d["tahun"]))
        return obj
