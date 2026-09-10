# SIMBON BBM
### Sistem Informasi Manajemen Bon BBM — Kejaksaan Tinggi Jawa Tengah

Aplikasi web lokal (localhost) untuk otomatisasi pembuatan Nota Bon BBM.
Seluruh data (SQLite, Excel, PDF) tersimpan di dalam folder project ini
sehingga aplikasi mudah dipindahkan ke komputer lain — cukup salin folder.

## Cara Menjalankan

1. Pastikan Python 3.9+ sudah terpasang.
2. Buka folder ini di Visual Studio Code (atau terminal biasa).
3. Install dependency:
   ```
   pip install -r requirements.txt
   ```
4. Jalankan aplikasi:
   ```
   python app.py
   ```
5. Buka browser ke: http://127.0.0.1:5000

## Login Default (sementara)

- Username: `admin`
- Password: `kejati`

> Ganti kredensial ini sebelum digunakan di lingkungan produksi
> (lihat variabel `VALID_USERNAME` / `VALID_PASSWORD` di `app.py`).

## Struktur Folder

```
simbon-bbm/
├── app.py                 # Backend Flask (routing, API)
├── database.py             # Koneksi & inisialisasi SQLite
├── terbilang.py             # Konversi angka -> teks Rupiah
├── excel_writer.py          # Rekap otomatis ke Excel
├── pdf_generator.py         # Generator PDF Nota BBM (ReportLab)
├── requirements.txt
├── database.db               # (dibuat otomatis saat pertama dijalankan)
├── static/
│   ├── css/style.css
│   ├── js/clock.js
│   ├── js/dashboard.js
│   └── img/logo-kejati.png, gedung-kejati.jpg   (placeholder — ganti dengan foto resmi)
├── templates/
│   ├── login.html
│   └── dashboard.html
├── generated_pdf/           # PDF nota hasil generate tersimpan di sini
└── exports/
    └── data-bon-bbm.xlsx     # Rekap otomatis (dibuat saat submit pertama)
```

## Catatan Penting

- **Logo & foto gedung** pada folder `static/img/` masih berupa placeholder
  yang dibuat otomatis. Silakan ganti file `logo-kejati.png` dan
  `gedung-kejati.jpg` dengan logo resmi dan foto gedung Kejaksaan Tinggi
  Jawa Tengah yang sebenarnya (gunakan nama file yang sama).
- Data kendaraan awal (H 1234 AA, dst.) otomatis dibuat saat pertama kali
  dijalankan. Kendaraan baru bisa langsung ditambahkan lewat form (ketik
  nomor polisi yang belum ada, lalu klik "+ Tambahkan...").
- Field **Terbilang** terisi otomatis begitu field "Uang Sebanyak" diisi,
  namun tetap bisa diedit manual jika diperlukan.
- Jangan hapus folder `generated_pdf/` dan `exports/` — folder ini
  digunakan aplikasi untuk menyimpan hasil.
