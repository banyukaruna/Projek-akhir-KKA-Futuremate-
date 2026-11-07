"""Penyusunan jadwal belajar otomatis berdasarkan deadline dan waktu luang."""
from datetime import date, datetime, timedelta
from uuid import uuid4


class Penjadwalan:
    HARI = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu")

    @staticmethod
    def buat_jadwal(items, hari_tersedia, jam_mulai, jam_selesai, hari_ini=None, sesi_manual=None):
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
        sesi_manual = [dict(sesi) for sesi in (sesi_manual or [])]
        item_by_id = {item.id: item for item in aktif}
        durasi_manual = {}
        for sesi in sesi_manual:
            item_id = sesi.get("item_id")
            if item_id in item_by_id:
                sesi.setdefault("id", str(uuid4()))
                sesi["manual"] = True
                jadwal.append(sesi)
                durasi_manual[item_id] = durasi_manual.get(item_id, 0) + int(sesi.get("durasi", 0))

        slot_terpakai = set()

        for item in aktif:
            durasi_total = max(0, int(getattr(item, "durasi_menit", 60)) - durasi_manual.get(item.id, 0))
            if not 15 <= durasi_total <= 480:
                raise ValueError("Durasi kegiatan harus 15 sampai 480 menit.")

            sisa_durasi = durasi_total
            while sisa_durasi > 0:
                indeks_tersedia = next(
                    (
                        indeks for indeks, (tanggal_slot, jam_slot) in enumerate(slots)
                        if indeks not in slot_terpakai and tanggal_slot <= item.deadline
                        and not any(
                            sesi["tanggal"] == tanggal_slot.isoformat()
                            and datetime.strptime(sesi["mulai"], "%H:%M")
                                < datetime.strptime(jam_slot, "%H:%M") + timedelta(minutes=60)
                            and datetime.strptime(sesi["mulai"], "%H:%M") + timedelta(minutes=int(sesi["durasi"]))
                                > datetime.strptime(jam_slot, "%H:%M")
                            for sesi in jadwal
                        )
                    ),
                    None,
                )
                if indeks_tersedia is None:
                    break

                tanggal_sesi, waktu_sesi = slots[indeks_tersedia]
                durasi_sesi = min(60, sisa_durasi)
                jadwal.append({
                    "id": str(uuid4()),
                    "item_id": item.id,
                    "judul": item.judul,
                    "mapel": item.mapel,
                    "jenis": item.jenis(),
                    "tanggal": tanggal_sesi.isoformat(),
                    "mulai": waktu_sesi,
                    "durasi": durasi_sesi,
                    "manual": False,
                })
                slot_terpakai.add(indeks_tersedia)
                sisa_durasi -= durasi_sesi
        return jadwal

    @staticmethod
    def ubah_sesi(sesi, tanggal, mulai, durasi):
        tanggal_obj = date.fromisoformat(tanggal)
        waktu_obj = datetime.strptime(mulai, "%H:%M")
        durasi = int(durasi)
        if durasi < 15 or durasi > 240:
            raise ValueError("Durasi sesi harus 15 sampai 240 menit.")
        if tanggal_obj < date.today():
            raise ValueError("Tanggal sesi tidak boleh berada di masa lalu.")
        sesi.update({
            "tanggal": tanggal_obj.isoformat(),
            "mulai": waktu_obj.strftime("%H:%M"),
            "durasi": durasi,
            "manual": True,
        })
