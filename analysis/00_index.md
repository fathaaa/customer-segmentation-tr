# Indeks Analisis PKB

Daftar ini merangkum 46 usulan dari `Check.xlsx` berdasarkan skema `data/pkb_master.parquet` (diperiksa lewat skema saja). Rentang data PKB: 2025-01-02–2026-10-12. `Customer ID` diproksikan dengan `Chassis`; 33.649 WO tidak memiliki Chassis. `BU` dipakai sebagai cabang servis (nama cabang tersedia di `data/ref_cabang.csv`). `Tanggal_PKB` adalah tanggal PKB dan `Total_Revenue` disebut **nilai transaksi**.

`Bisa` berarti data kebutuhan inti tersedia; `Sebagian` berarti analisis terbatas oleh data kosong atau kebutuhan yang belum tersedia; `Butuh data tambahan` berarti satu atau lebih data inti tidak tersedia. Frekuensi, urutan kunjungan, recency, dan jumlah PKB dapat diturunkan dari baris per WO dan tanggal, dengan batasan Chassis di atas.

| No | Analisis | Prioritas | Kolom yang dibutuhkan | Status | Alasan |
|---:|---|---|---|---|---|
| 1 | Customer Distribution by Area | High | Chassis, Kecamatan, Kota/Kabupaten, Provinsi | Sebagian | Data wilayah hanya sampai kecamatan; kelurahan tidak tersedia. |
| 2 | Service Frequency by Area | High | Chassis, Kecamatan, Kota/Kabupaten/Provinsi, Tanggal_PKB | Bisa | Frekuensi PKB dan wilayah tersedia; hitungan per customer terbatas pada WO yang memiliki Chassis. |
| 3 | Service Penetration by Area | High | Chassis, Kecamatan/Kota/Kabupaten/Provinsi, Tanggal_PKB; tanggal penjualan | Butuh data tambahan | Data penjualan/unit terjual dan tanggal penjualan tidak tersedia untuk menghitung denominator penetrasi. |
| 4 | Distance to Workshop Analysis | High | Alamat/wilayah customer, lokasi bengkel, Tanggal_PKB | Butuh data tambahan | Alamat rinci/customer dan koordinat atau lokasi tiap bengkel diperlukan untuk menghitung jarak. |
| 5 | Customer Demographics Analysis | Low | Chassis, umur, customer type | Butuh data tambahan | Umur dan jenis pelanggan tidak tersedia. |
| 6 | Geographic Customer Loyalty | High | Chassis, Kecamatan/Kota/Kabupaten/Provinsi, Tanggal_PKB | Bisa | Riwayat PKB dan wilayah tersedia; loyalitas berbasis customer terbatas oleh Chassis kosong. |
| 7 | Branch Catchment Area | Medium | Chassis, Kecamatan/Kota/Kabupaten/Provinsi, BU | Bisa | BU dapat dipakai sebagai cabang servis dan wilayah tersedia; customer unik tidak terhitung untuk WO tanpa Chassis. |
| 8 | Cross-Branch Service Behavior | High | Chassis, cabang penjualan, BU | Butuh data tambahan | Cabang penjualan tidak tersedia; BU hanya menunjukkan cabang servis. |
| 9 | Untapped Geographic Market | High | Chassis, wilayah, penjualan/unit terjual, PKB | Butuh data tambahan | Data penjualan/unit terjual dan tanggal penjualan tidak tersedia untuk dibandingkan dengan penetrasi service. |
| 10 | Repeat Service Rate | High | Chassis, Tanggal_PKB | Bisa | Dapat dihitung untuk Chassis terisi; 33.649 WO tanpa Chassis tidak dapat ditautkan sebagai customer. |
| 11 | Average Service Interval | High | Chassis, Tanggal_PKB | Bisa | Jarak hari antar-PKB dapat dihitung untuk Chassis terisi; kunjungan WO tanpa Chassis tidak dapat dirangkai. |
| 12 | Customer Retention Rate | High | Chassis, Tanggal_PKB, definisi periode retention | Bisa | Riwayat tersedia untuk Chassis terisi; perlu memilih definisi/periode retention dan hasil tidak mencakup customer tanpa Chassis. |
| 13 | Service Drop-off Analysis | High | Chassis, Tanggal_PKB, urutan service | Bisa | Urutan kunjungan dapat diturunkan dari tanggal untuk Chassis terisi; 33.649 WO tanpa Chassis tidak dapat dirangkai. |
| 14 | First Service Conversion | High | Chassis, tanggal penjualan, Tanggal_PKB | Butuh data tambahan | Tanggal/daftar penjualan tidak tersedia untuk mengidentifikasi pembeli dan mengukur konversi service pertama. |
| 15 | Second Service Conversion | High | Chassis, Tanggal_PKB, urutan service | Bisa | Urutan kunjungan dapat diturunkan untuk Chassis terisi; WO tanpa Chassis tidak dapat ditautkan. |
| 16 | Free-to-Paid Service Conversion | High | Chassis, Service_Category, Tanggal_PKB, status T-Care | Sebagian | TWC, SSC, SBI, RTJ dapat dikenali sebagai free; SBE harus dipisahkan karena status T-Care tidak ada. Chassis juga kosong pada 33.649 WO. |
| 17 | Service Cohort Analysis | High | Chassis, tanggal penjualan, Tanggal_PKB | Butuh data tambahan | Tanggal penjualan untuk membentuk cohort pembelian tidak tersedia. |
| 18 | Customer Churn Analysis | High | Chassis, Tanggal_PKB, definisi/ambang service interval | Bisa | Riwayat dan recency dapat dihitung, tetapi aturan periode ekspektasi/ambang churn perlu ditentukan atau diberikan. |
| 19 | Customer Service Lifecycle | High | Chassis, tanggal penjualan, Tanggal_PKB, Service_Category | Butuh data tambahan | Perjalanan sejak pembelian tidak dapat disusun tanpa tanggal dan riwayat penjualan; data PKB saja hanya menggambarkan service. |
| 20 | Retention by Vehicle Model | High | Chassis, model kendaraan, Tanggal_PKB | Butuh data tambahan | Model kendaraan tidak tersedia. |
| 21 | Retention by Vehicle Age | High | Chassis, tahun/tanggal kendaraan, Tanggal_PKB | Butuh data tambahan | Tahun atau tanggal produksi/penjualan kendaraan tidak tersedia untuk menentukan usia kendaraan. |
| 22 | Retention by Fuel Type | Medium | Chassis, fuel type, Tanggal_PKB | Butuh data tambahan | Jenis bahan bakar tidak tersedia. |
| 23 | Mileage vs Service Frequency | High | Chassis, odometer, Tanggal_PKB | Butuh data tambahan | Pembacaan odometer tidak tersedia. |
| 24 | Service Type by Vehicle Model | Medium | model kendaraan, Service_Category, WO/PKB | Butuh data tambahan | Service_Category dan WO tersedia, tetapi model kendaraan tidak tersedia. |
| 25 | Service Spending by Model | Medium | model kendaraan, Total_Revenue, WO/PKB | Butuh data tambahan | Model kendaraan tidak tersedia. Nilai transaksi dari Total_Revenue belum tentu uang yang dibayar customer, termasuk pada servis free; arti nominal menunggu konfirmasi mentor. |
| 26 | Service Interval Compliance | High | Chassis, odometer, Tanggal_PKB, jadwal service | Butuh data tambahan | Odometer dan jadwal/standar service yang harus dipatuhi tidak tersedia. |
| 27 | Revenue per Customer | Medium | Chassis, Total_Revenue, WO/PKB | Bisa | Dapat dihitung terbatas untuk Chassis terisi. Total_Revenue adalah nilai transaksi, belum tentu uang yang dibayar customer, termasuk pada servis free; arti nominal menunggu konfirmasi mentor. |
| 28 | Customer Lifetime Value | Medium | Chassis, histori PKB, revenue, margin | Butuh data tambahan | Margin tidak tersedia dan Total_Revenue belum terkonfirmasi sebagai pembayaran; Chassis juga kosong untuk sebagian WO. |
| 29 | RFM Segmentation | High | Chassis, Tanggal_PKB, Total_Revenue | Bisa | Recency, frequency, dan monetary dapat dibentuk terbatas untuk Chassis terisi; Total_Revenue belum tentu uang yang dibayar customer, termasuk pada servis free; arti nominal menunggu konfirmasi mentor. |
| 30 | Service Revenue by Area | Medium | Kecamatan/Kota/Kabupaten/Provinsi, Total_Revenue, WO/PKB | Bisa | Nilai transaksi dan wilayah tersedia, tetapi sebagian wilayah bisa kosong/tidak lengkap. Total_Revenue belum tentu uang yang dibayar customer, termasuk pada servis free; arti nominal menunggu konfirmasi mentor. |
| 31 | Parts vs Labor Spending | Medium | Chassis, Revenue_Product, Revenue_Jasa | Bisa | Nilai produk dan jasa tersedia, tetapi Chassis kosong untuk sebagian WO. Keduanya belum tentu pengeluaran yang dibayar customer; arti Total_Revenue menunggu konfirmasi mentor. |
| 32 | Free vs Paid Service Revenue | Medium | Service_Category, Total_Revenue, Tanggal_PKB, status T-Care | Sebagian | Kategori free pasti dapat dipisah dan SBE dilaporkan tersendiri; status T-Care belum ada. Total_Revenue pada servis free tetap >0 dan belum tentu uang yang dibayar customer; arti nominal menunggu konfirmasi mentor. |
| 33 | High-Value Customer Analysis | Medium | Chassis, frekuensi PKB, Total_Revenue | Bisa | Frekuensi dan nilai transaksi bisa dihitung terbatas untuk Chassis terisi. Total_Revenue belum tentu uang yang dibayar customer, termasuk pada servis free; arti nominal menunggu konfirmasi mentor. |
| 34 | Reminder Conversion Rate | High | Chassis, tanggal reminder, booking, PKB | Butuh data tambahan | Riwayat reminder, booking, dan hasil reminder tidak tersedia. |
| 35 | Best Reminder Timing | High | tanggal reminder, estimasi tanggal service, response, PKB | Butuh data tambahan | Data reminder, estimasi service, dan respons tidak tersedia. |
| 36 | Reminder Channel Effectiveness | High | Chassis, channel, tanggal reminder, response, PKB | Butuh data tambahan | Channel dan riwayat/respons reminder tidak tersedia. |
| 37 | Booking-to-Service Conversion | High | Chassis, tanggal booking, status booking, PKB | Butuh data tambahan | Data booking, tanggal, dan status booking tidak tersedia. |
| 38 | Customer Satisfaction vs Retention | Medium | Chassis, CSAT, Tanggal_PKB | Butuh data tambahan | Skor kepuasan/CSAT tidak tersedia. |
| 39 | Service Complaint Analysis | Medium | Chassis, komplain, Tanggal_PKB | Butuh data tambahan | Data komplain tidak tersedia. |
| 40 | Service Return Prediction | High | Chassis, histori PKB, usia kendaraan, service interval, wilayah | Butuh data tambahan | Histori PKB dan wilayah tersedia, tetapi usia kendaraan dan aturan/riwayat service interval tidak tersedia. |
| 41 | Customer Churn Prediction | High | Chassis, histori PKB, recency, frequency, usia kendaraan | Butuh data tambahan | Histori, recency, dan frequency dapat diturunkan; usia kendaraan tidak tersedia. Chassis juga kosong untuk sebagian WO. |
| 42 | Next Service Date Prediction | High | Chassis, Tanggal_PKB, odometer, service interval | Butuh data tambahan | Odometer dan aturan interval service tidak tersedia untuk memperkirakan tanggal kunjungan berikutnya. |
| 43 | Customer Segmentation | High | Chassis, model kendaraan, wilayah, frekuensi, nilai transaksi | Butuh data tambahan | Segmen dapat dibentuk dari wilayah dan riwayat yang tersedia, tetapi model kendaraan tidak ada dan Chassis kosong untuk sebagian WO. Nilai transaksi belum tentu uang yang dibayar customer; arti nominal menunggu konfirmasi mentor. |
| 44 | Service Demand Forecasting | Medium | BU, Tanggal_PKB, volume PKB, kalender | Bisa | Data hanya 21 bulan, sehingga pola musiman belum bisa dipelajari penuh. |
| 45 | Customer Propensity Scoring | High | Chassis, histori PKB, usia kendaraan, wilayah, riwayat reminder | Butuh data tambahan | Usia kendaraan dan riwayat reminder tidak tersedia; sebagian WO juga tidak memiliki Chassis. |
| 46 | Service Revenue Prediction | Medium | histori revenue, WO/PKB, model kendaraan, wilayah | Butuh data tambahan | Histori, wilayah, dan nilai transaksi tersedia untuk pemodelan terbatas; model kendaraan tidak ada. Total_Revenue belum tentu uang yang dibayar customer, termasuk pada servis free; arti nominal menunggu konfirmasi mentor. |

## Ringkasan status

| Status | Jumlah |
|---|---:|
| Bisa | 15 |
| Sebagian | 2 |
| Butuh data tambahan | 29 |
| **Total** | **46** |

Semua usulan memiliki batasan data yang dinyatakan di kolom alasan; tidak ada yang sepenuhnya memenuhi seluruh kebutuhan aslinya tanpa pembatasan atau penambahan data.

## Data tambahan yang perlu diminta ke mentor

- Data T-Care aktif per kendaraan, atau tanggal penjualan untuk menentukan masa berlaku T-Care/SBE dan membentuk cohort pembelian.
- Konfirmasi arti `Total_Revenue`/`Revenue_Product`/`Revenue_Jasa`: apakah nilai invoice/transaksi, nilai yang dibayar customer, atau nilai lain; termasuk perlakuan servis free.
- Data penjualan kendaraan: Chassis/unit terjual, tanggal penjualan, cabang penjualan, model, tahun/tanggal produksi, serta fuel type.
- Data customer bila tersedia: Customer ID, umur, dan customer type; atau pemetaan Customer ID ke Chassis untuk melengkapi WO yang Chassis-nya kosong.
- Lokasi bengkel dan alamat/koordinat customer yang memadai untuk analisis jarak; data wilayah lebih rinci (kelurahan) bila diperlukan.
- Data odometer dan jadwal/standar interval service per kendaraan/model.
- Definisi resmi retention, churn, dan interval ekspektasi untuk menetapkan periode/ambang analisis.
- Data reminder (tanggal, channel, target/estimasi service, response), booking (tanggal/status), CSAT, serta komplain.
- Kalender operasional dan hari libur/event untuk demand forecasting.
- Margin atau biaya untuk menghitung Customer Lifetime Value berbasis margin.
- Pemetaan BU ke nama cabang dari `data/ref_cabang.csv` untuk label pelaporan.
