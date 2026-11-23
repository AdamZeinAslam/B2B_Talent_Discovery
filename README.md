# VINIX7 Talent Discovery

Portal Streamlit untuk membantu mitra industri mencari dan meninjau kandidat dari dataset konsultasi karier VINIX7. Aplikasi memuat dua metode pencocokan dan satu evaluasi kandidat berbasis rubrik:

1. **Weighted KNN** — metode utama berbasis weighted Euclidean distance.
2. **Weighted Scoring Model (WSM)** — metode pembanding dengan agregasi skor kesesuaian secara linear.
3. **Evaluasi berbasis rubrik internal** — menghitung penilaian eksploratif secara lokal, sehingga selalu tersedia tanpa API key atau layanan AI eksternal.
4. **Opini generative AI eksternal (opsional)** — dapat digunakan sebagai opini tambahan jika administrator mengaktifkan integrasi dan pengguna memberikan persetujuan.

Aplikasi menggunakan bundle `model/talentmatch_model_bundle.joblib` yang disertakan pada paket ini.

## Fitur aplikasi

- Identitas visual VINIX7 dengan palet biru-kuning dan layout operasional yang lebih ringkas.
- Overview, panduan penggunaan, dan penjelasan dimensi M1–M9.
- Form pencarian kandidat dengan hard filter, profil target, dan target kompetensi.
- Ranking Top 10 Weighted KNN dan Top 10 Weighted Scoring.
- Perbandingan ranking, overlap Top 10, dan korelasi Spearman.
- Evaluasi berbasis rubrik internal untuk gabungan Top 10 KNN dan Top 10 WSM (maksimal 20 kandidat unik), serta opini generative AI eksternal bila diaktifkan.
- Detail kandidat, shortlist, dan ekspor CSV.

## Cara menjalankan di komputer

Gunakan Python 3.10–3.12 dan versi library yang tercantum pada `requirements.txt`. `scikit-learn==1.6.1` diperlukan untuk kompatibilitas model joblib.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\\Scripts\\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dan jalankan:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Buka alamat lokal yang ditampilkan Streamlit, biasanya `http://localhost:8501`.

## Cara menjalankan di Google Colab

1. Upload dan ekstrak ZIP.
2. Pindah ke direktori `B2B_Talent_Discovery_Versi_Kita`.
3. Install dependensi dan jalankan aplikasi.

```python
%cd /content/B2B_Talent_Discovery_Versi_Kita
!pip install -r requirements.txt
!streamlit run app.py &
```

Untuk mengakses dari browser luar Colab, jalankan tunnel terpisah. URL Quick Tunnel bersifat sementara dan berubah ketika tunnel dibuat ulang. Jangan buka aplikasi publik tanpa kontrol akses apabila berisi data kandidat.

## Alur penggunaan

1. **Overview** — lihat jumlah profil, alur kerja, dan metode yang tersedia.
2. **Panduan Aplikasi** — pelajari indikator asesmen dan cara kerja tiap metode.
3. **Cari Kandidat** — masukkan posisi, lalu pilih filter serta kriteria yang relevan.
4. **Pilih 2–9 dimensi M1–M9** — tetapkan target sesuai kebutuhan posisi dan rubrik resmi.
5. **Hasil & Perbandingan** — tinjau Top 10 KNN, Top 10 WSM, kesepakatan ranking, dan evaluasi berbasis rubrik internal. Opini AI eksternal bersifat opsional.
6. **Shortlist** — simpan kandidat untuk dibahas lebih lanjut dan ekspor CSV.

## Metode penilaian

### Weighted KNN

Hard filter Program Studi dan kategori IPK (jika dipilih) diterapkan terlebih dahulu. Sistem menyusun fitur profil berdasarkan input perusahaan, menghitung jarak profil serta kompetensi, kemudian menggabungkannya:

`Final Distance = sqrt(0.70 * ProfileDistanceNormalized^2 + 0.30 * CompetencyDistanceNormalized^2)`

Final Distance bukan persentase. Semakin kecil nilai, semakin dekat kandidat terhadap kriteria pada pencarian tersebut.

### Weighted Scoring Model

WSM menggunakan komponen jarak yang sama dengan KNN, tetapi menggabungkan skor kesesuaian secara linear:

`WSM Score = 0.70 * ProfileFit + 0.30 * CompetencyFit`

`ProfileFit = (1 - ProfileDistanceNormalized) * 100`

`CompetencyFit = (1 - CompetencyDistanceNormalized) * 100`

Skor 0–100 ini bersifat relatif terhadap kumpulan kandidat yang lolos hard filter pada pencarian tersebut. Skor bukan probabilitas diterima dan tidak boleh dibandingkan sebagai skor absolut antar-posisi. Perbedaan ranking KNN dan WSM berasal dari cara agregasi jarak (Euclidean/L2 versus linear/L1).

### Evaluasi kandidat berbasis rubrik internal

Evaluasi utama berjalan sepenuhnya di dalam aplikasi dan tidak membutuhkan koneksi AI eksternal atau API key. Sistem menilai gabungan maksimal 20 kandidat unik dari Top 10 KNN dan Top 10 WSM menggunakan rubrik tetap:

- Kesesuaian profil relatif: 0–30 poin. Menggunakan skor Profile Fit dari kumpulan kandidat yang lolos filter pencarian.
- Pencapaian target kompetensi: 0–50 poin. Menghitung rata-rata pencapaian kandidat terhadap target M1–M9 yang dipilih perusahaan.
- Relevansi karier/minat: 0–20 poin. Mengukur kecocokan teks Dream Job, Bidang Minat, dan Work Values terhadap kriteria posisi yang diberikan.

Skor ini deterministik dan dapat dijelaskan, tetapi bukan generative AI, bukan ground truth HR, bukan probabilitas keberhasilan, serta bukan dasar otomatis untuk menerima/menolak kandidat. Komponen Profile Fit bersifat relatif terhadap kandidat yang lolos filter pada pencarian tersebut.

### Opini generative AI eksternal (opsional)

Administrator dapat mengaktifkan layanan AI eksternal melalui Streamlit Secrets dengan nama `OPENROUTER_API_KEY`. Pengguna tidak perlu memasukkan API key. Jika layanan eksternal tidak diaktifkan, sedang penuh, atau kuotanya habis, evaluasi berbasis rubrik internal tetap bisa dijalankan dan ditampilkan.

Jika opini eksternal diaktifkan, aplikasi meminta persetujuan sebelum mengirim atribut kandidat yang diminimalkan. Candidate_ID digunakan sebagai pseudonim; nama, kontak, perguruan tinggi, dan nama tempat magang tidak dikirim. Jangan menaruh API key di source code, GitHub, notebook yang dibagikan, atau ZIP aplikasi.

## Panduan dimensi M1–M9

| Kode | Nama pada data | Gambaran operasional | Skala maksimum model |
|---|---|---|---:|
| M1 | Background | Latar belakang kandidat yang relevan dengan posisi | 10 |
| M2 | Skills | Kemampuan atau keterampilan kandidat | 15 |
| M3 | Industry | Keterkaitan kandidat dengan bidang/konteks industri | 10 |
| M4 | Interest | Ketertarikan pada bidang atau aktivitas pekerjaan | 15 |
| M5 | Compass | Arah atau orientasi pengembangan karier | 10 |
| M6 | Company | Orientasi pada konteks atau lingkungan perusahaan | 10 |
| M7 | Branding | Identitas dan penyampaian profil profesional | 10 |
| M8 | Ambisi | Dorongan dan aspirasi untuk berkembang | 10 |
| M9 | Resiliensi | Ketahanan menghadapi tantangan atau perubahan | 10 |

**Penting:** deskripsi M1–M9 di atas adalah interpretasi operasional nama indikator, bukan rubrik atau definisi psikometrik resmi. Gunakan pedoman asesmen resmi VINIX7 untuk menetapkan target.

## Validasi integrasi

Jalankan:

```bash
python verify_integration.py
```

Skrip memastikan hasil Top 10 KNN tetap cocok dengan output referensi dan memastikan WSM menghasilkan ranking pembanding untuk cohort kandidat yang sama.

## Batasan dan penggunaan yang bertanggung jawab

- Belum ada label relevansi dari HR manusia atau outcome rekrutmen historis. Karena itu aplikasi belum dapat mengklaim akurasi, Precision@10, Recall@10, atau NDCG@10 yang tervalidasi.
- Korelasi KNN–WSM dan KNN–AI hanya ukuran kesepakatan antarmetode, bukan kebenaran rekomendasi.
- AI evaluator dapat keliru atau bias. Hasil perlu diperiksa HR dan tidak boleh menjadi keputusan tunggal.
- Kampus dan tempat magang hanya preferensi tambahan exact-match. Jangan gunakan sebagai syarat umum tanpa alasan rekrutmen yang relevan.
- Pemetaan IPK kode 1–4 mengikuti bundle model dan harus diverifikasi dengan kuesioner sumber sebelum penggunaan operasional.
- Shortlist disimpan dalam `st.session_state`; data hilang ketika sesi berakhir.
- Prototype belum mempunyai login, otorisasi per perusahaan, audit log, atau database permanen. Untuk deployment nyata, tambahkan kontrol akses, HTTPS, dan penyimpanan aman.


### Hotfix 22 November 2026

Memperbaiki key widget Streamlit yang sebelumnya bertabrakan ketika kandidat yang sama tampil pada tab Weighted KNN dan Weighted Scoring. Setiap tombol shortlist kini memiliki namespace metode. Perhitungan model tidak berubah.


## Insight Overview

Overview menampilkan tiga chart dari data kandidat: perguruan tinggi terbanyak, program studi terbanyak, dan bidang minat yang paling banyak dipilih. Chart dihitung langsung dari bundle kandidat; satu kandidat dapat memilih beberapa bidang minat.

## Filter pengalaman VINIX7

Form menyediakan tiga keadaan: tidak dijadikan kriteria, pernah magang di VINIX7, atau tidak pernah magang di VINIX7. Opsi “tidak pernah” hanya diterapkan pada kandidat dengan catatan tempat magang terisi dan bukan nama VINIX7; data kosong diperlakukan sebagai tidak diketahui.

