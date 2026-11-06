"""Baca/tulis data JSON. Error file rusak dibungkus jadi DataTidakValidError."""
import json
from pathlib import Path

from exceptions import DataTidakValidError
from models.pengguna import Murid
from models.target import Jurusan


class Penyimpanan:
    def __init__(self, path_data, path_jurusan):
        self.path_data = Path(path_data)
        self.path_jurusan = Path(path_jurusan)

    def muat(self):
        """Mengembalikan dict {nama_kecil: Murid}."""
        if not self.path_data.exists():
            return {}
        try:
            mentah = json.loads(self.path_data.read_text(encoding="utf-8"))
            return {m["nama"].lower(): Murid.dari_dict(m) for m in mentah["murid"]}
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            raise DataTidakValidError(f"File {self.path_data.name} rusak ({e}). "
                                      "Hapus atau perbaiki file tersebut.") from e

    def simpan(self, daftar_murid):
        self.path_data.parent.mkdir(exist_ok=True)
        isi = {"murid": [m.to_dict() for m in daftar_murid.values()]}
        self.path_data.write_text(json.dumps(isi, indent=2, ensure_ascii=False), encoding="utf-8")

    def muat_katalog(self):
        try:
            mentah = json.loads(self.path_jurusan.read_text(encoding="utf-8"))
            return [Jurusan(j["nama"], j["kampus"], j["rata_min"], j["syarat_mapel"], j["riasec"])
                    for j in mentah]
        except (OSError, json.JSONDecodeError, KeyError) as e:
            raise DataTidakValidError(f"Katalog jurusan tidak bisa dibaca ({e}).") from e
