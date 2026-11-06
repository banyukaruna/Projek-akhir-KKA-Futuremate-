# FutureMate

FutureMate adalah aplikasi Python untuk membantu murid mengelola kegiatan belajar dan merencanakan target masa depan. Proyek ini menggunakan konsep Pemrograman Berorientasi Objek (PBO).

## Persyaratan

- Python 3.9 atau lebih baru
- CustomTkinter untuk antarmuka grafis

## Menjalankan aplikasi GUI

1. Clone atau unduh repository ini.
2. Buka terminal pada folder proyek.
3. Pasang dependensi:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Jalankan aplikasi:

   ```bash
   python -m gui.app
   ```

Data murid tersimpan secara lokal di `data/data.json`. File tersebut dibuat otomatis setelah murid masuk dan data disimpan.

## Menjalankan versi CLI

Versi CLI tetap tersedia:

```bash
python main.py
```

## Catatan

- Data pada `data/jurusan.json` merupakan katalog contoh dan dapat disesuaikan.
- GUI menggunakan kembali model dan layanan yang sudah ada agar aturan bisnis tidak diduplikasi.
- Pengembangan GUI dilakukan pada branch `gui-foundation`.
