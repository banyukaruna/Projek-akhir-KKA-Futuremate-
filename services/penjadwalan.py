"""Penyusunan jadwal belajar otomatis berdasarkan deadline dan waktu luang."""
from datetime import date, datetime, timedelta


class Penjadwalan:
    HARI = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu")

    @staticmethod
    def buat_jadwal(items, hari_tersedia, jam_mulai, jam_selesai, hari_ini=None):
        """Buat sesi maksimal 60 menit sesuai durasi kegiatan dan tenggatnya."""
        hari_ini = hari_ini or date.today()
        mulai = datetime.strptime(jam_mulai, "%H:%M")
        selesai = datetime.strptime(jam_selesai, "%H:%M")
        if selesai <= mulai:
            raise ValueError("Jam selesai harus setelah jam mulai.")
        if not hari_tersedia:
            raise ValueError("Pilih minimal satu hari belajar.")

        slots = []
        tanggal = hari_ini
        batas = hari_ini + timedelta(days=30)
        while tanggal <= batas:
            if tanggal.weekday() in hari_tersedia:
                waktu = mulai
                while waktu + timedelta(minutes=60) <= selesai:
                    slots.append((tanggal, waktu.strftime("%H:%M")))
                    waktu += timedelta(minutes=75)
            tanggal += timedelta(days=1)

        aktif = [item for item in items if not item.selesai and item.deadline >= hari_ini]
        aktif.sort(key=lambda item: (item.deadline, -item.skor_prioritas(hari_ini)))
        jadwal = []
        indeks_slot = 0

        for item in aktif:
            if item.jenis() == "Sesi":
                durasi_total = int(getattr(item, "durasi_menit", 60))
                if not 15 <= durasi_total <= 480:
                    raise ValueError("Durasi sesi belajar harus 15 sampai 480 menit.")
                durasi_sesi = []
                while durasi_total:
                    bagian = min(60, durasi_total)
                    durasi_sesi.append(bagian)
                    durasi_total -= bagian
            else:
                jumlah_sesi = 2 if item.jenis() == "Ujian" else (
                    2 if item.jenis() == "Tugas" and getattr(item, "kesulitan", 3) >= 4 else 1
                )
                durasi_sesi = [60] * jumlah_sesi

            for durasi in durasi_sesi:
                while indeks_slot < len(slots) and slots[indeks_slot][0] > item.deadline:
                    indeks_slot += 1
                if indeks_slot >= len(slots):
                    break
                tanggal_sesi, waktu_sesi = slots[indeks_slot]
                jadwal.append({
                    "judul": item.judul,
                    "mapel": item.mapel,
                    "jenis": item.jenis(),
                    "tanggal": tanggal_sesi.isoformat(),
                    "mulai": waktu_sesi,
                    "durasi": durasi,
                    "manual": False,
                })
                indeks_slot += 1
        return jadwal

    @staticmethod
    def ubah_sesi(sesi, tanggal, mulai, durasi):
        tanggal_obj = date.fromisoformat(tanggal)
        waktu_obj = datetime.strptime(mulai, "%H:%M")
        durasi = int(durasi)
        if durasi < 15 or durasi > 240:
            raise ValueError("Durasi harus 15 sampai 240 menit.")
        sesi.update({
            "tanggal": tanggal_obj.isoformat(),
            "mulai": waktu_obj.strftime("%H:%M"),
            "durasi": durasi,
            "manual": True,
        })
