## Konteks Proyek: Lookup Alamat PKB

## Tujuan

Menambahkan Kecamatan, Kota/Kabupaten, Provinsi ke data PKB Details
lewat lookup by nomor PKB (kolom WO).

## Data (JANGAN dibuka penuh, ukurannya jutaan baris)

- PKB Details 2025: 79 file xlsx, 2026: 55 file xlsx. Satu baris per part/jasa.
- Kolom dipakai: BU, WO, Product Type, Product, Product Description,
  Service Category, Total Transaction Amount, Created On
- Kunci: WO, format 101PKB2501-0034
- Address/Addres Final.xlsx: header baris 2, kolom PKB | Kecamatan |
  Kota/Kabupaten | Provinsi (372.986 PKB unik)
- Address/fiks_alamat_belum_lengkap.xlsx: header baris 2, 188.299 PKB.
  Kolom: PKB, Chassis No, Kecamatan, Kota/Kabupaten, Provinsi, Alamat,
  Kecamatan (hasil), Kota/Kabupaten (hasil), Provinsi (hasil), Status, Metode.
  Status: Tidak teridentifikasi 158.560 | Parsial 28.970 | Periksa konflik 769

## Hasil lookup ke Address Final (output: *_dengan_alamat.csv)

| Tahun | Total baris | Alamat tidak ketemu |
| ----- | ----------- | ------------------- |
| 2025  | 1.803.574   | 563.253 (31%)       |
| 2026  | 1.401.589   | 456.251 (33%)       |

- Tidak ketemu rata ~28-30% di semua bulan (bukan masalah periode atau format)
- 153.849 WO unik tidak ketemu: 120.237 (78%) ada di belum_lengkap,
  33.612 (22%) tidak ada di file alamat mana pun
- Dari 120.237 itu, wilayah parsial terisi: kecamatan 793, kota 4.377, provinsi 5.793

## Masalah diketahui

- 7 file 2025 (export 12-10-2026) korup, direkonstruksi lewat perbaiki.py.
  Kemungkinan ada baris di ujung file yang hilang.
- Sebagian alamat di Master Lokasi dari pencarian internet, akurasi belum diverifikasi.

## Aturan kerja

- Jangan baca file data penuh. Tulis script, jalankan, baca output ringkasnya saja.
- Proses per file atau per chunk (RAM terbatas).
- Jangan menimpa CSV yang sudah ada, tulis ke file output baru.
- Jangan commit .csv atau .xlsx.
- Cetak maksimal 5 baris contoh.

## Script

gabung.py (gabung + lookup) | perbaiki.py (perbaiki file korup)
cek.py (persen tidak ketemu per bulan) | cek2.py (cek ke belum_lengkap)

## Tahap 2

- tahap2.py sudah dijalankan.
- Output: PKB Details 2025_tahap2.csv dan PKB Details 2026_tahap2.csv.
- Kolom baru: Alamat_Asli, Status_Alamat.
- Ringkasan jumlah baris per Status_Alamat:
  - 2025:
    - Lengkap: 1.240.321
    - Tidak teridentifikasi: 369.588
    - Tidak ada data alamat: 170.415
    - Parsial: 23.186
    - Periksa konflik sumber vs alamat: 64
  - 2026:
    - Lengkap: 945.338
    - Tidak teridentifikasi: 308.769
    - Tidak ada data alamat: 127.161
    - Parsial: 19.897
    - Periksa konflik sumber vs alamat: 424
