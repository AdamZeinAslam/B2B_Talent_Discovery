# VINIX7 Talent Discovery
### Sistem Pencocokan Kandidat dengan Kebutuhan Mitra Industri

VINIX7 Talent Discovery merupakan aplikasi berbasis web yang membantu perusahaan menemukan kandidat potensial berdasarkan kebutuhan posisi yang sedang dibuka.

Aplikasi ini dikembangkan untuk mempermudah proses pencarian dan penyaringan kandidat dari kumpulan data profil mahasiswa dan lulusan. Perusahaan dapat menentukan kriteria yang dibutuhkan, mulai dari latar belakang pendidikan, kategori IPK, minat karier, nilai kerja, hingga kompetensi tertentu.

Berdasarkan kriteria tersebut, sistem akan membandingkan profil kandidat dan menyajikan daftar rekomendasi yang dapat ditinjau lebih lanjut oleh tim HR.

---

## 1. Mengapa VINIX7 Talent Discovery dibuat?

Dalam proses rekrutmen, perusahaan sering kali harus memeriksa banyak profil kandidat untuk menemukan orang yang sesuai dengan kebutuhan posisi.

Proses tersebut dapat memerlukan waktu, terutama ketika perusahaan memiliki banyak persyaratan yang harus dipertimbangkan secara bersamaan.

Di sisi lain, data kandidat yang tersedia belum tentu dimanfaatkan secara maksimal untuk membantu perusahaan menemukan talenta yang relevan.

VINIX7 Talent Discovery dikembangkan untuk menjawab kebutuhan tersebut melalui sistem pencarian dan pemeringkatan kandidat yang lebih terstruktur.

Dengan aplikasi ini, perusahaan dapat:
- Mencari kandidat berdasarkan kebutuhan posisi.
- Menentukan kriteria dan kompetensi yang dibutuhkan.
- Melihat rekomendasi kandidat berdasarkan hasil perhitungan sistem.
- Membandingkan hasil dari beberapa metode pencocokan.
- Menyimpan kandidat potensial untuk ditinjau kembali.

## 2. Mengenal VINIX7 Talent Discovery

Aplikasi ini menggunakan dataset yang terdiri dari **2.988 profil kandidat dengan 39 atribut**.

Informasi kandidat mencakup beberapa aspek, seperti:
- **Akademik:** program studi, perguruan tinggi, dan kategori IPK.
- **Pengalaman:** informasi tempat magang yang tersedia pada dataset.
- **Minat karier:** bidang pekerjaan dan Dream Job.
- **Work Values:** nilai dan preferensi kerja.
- **Kompetensi:** sembilan dimensi penilaian, yaitu M1 sampai M9.

Seluruh informasi tersebut digunakan sebagai bahan pertimbangan dalam proses pencocokan kandidat.

## 3. Fitur Utama

### A. Dasbor Analitik

Menampilkan gambaran umum dataset kandidat melalui ringkasan jumlah profil dan visualisasi distribusi data.

Pengguna dapat melihat informasi seperti perguruan tinggi, program studi, serta bidang minat karier kandidat.

### B. Pencarian Kriteria

Perusahaan dapat memasukkan kebutuhan posisi melalui formulir pencarian.

Kriteria yang dapat digunakan meliputi:
- Posisi atau Dream Job.
- Program studi.
- Kategori IPK minimum.
- Work Values.
- Perguruan tinggi dan informasi tempat magang sebagai pertimbangan tambahan.
- Target kompetensi M1–M9.

Untuk pencarian berbasis kompetensi, pengguna memilih 2 sampai 9 dimensi yang dianggap penting bagi posisi tersebut.

### C. Hasil Rekomendasi Kandidat

Sistem menampilkan kandidat berdasarkan dua metode pencocokan:

1. **Weighted K-Nearest Neighbors (Weighted KNN)**

   Digunakan sebagai metode utama untuk mengurutkan kandidat berdasarkan jarak antara profil dan kebutuhan perusahaan.

   Semakin kecil nilai Final Distance, semakin dekat kandidat dengan kriteria pencarian.

2. **Weighted Scoring Model (WSM)**

   Digunakan sebagai metode pembanding dengan menggabungkan skor kesesuaian profil dan kompetensi menggunakan bobot 70:30.

   Hasilnya berupa skor kesesuaian relatif dalam skala 0–100.

### D. Perbandingan Metode

Membantu perusahaan melihat perbedaan hasil rekomendasi Weighted KNN dan WSM.

Informasi yang ditampilkan antara lain:
- Kesamaan kandidat pada Top 10.
- Peringkat kandidat pada masing-masing metode.
- Korelasi ranking menggunakan Spearman.

Dengan demikian, pengguna dapat mengetahui apakah kedua metode menghasilkan urutan kandidat yang serupa atau berbeda.

### E. Evaluasi Kandidat

Menyediakan dua bentuk penilaian tambahan:

**1. Evaluasi berbasis rubrik internal**

Sistem memberikan skor berdasarkan tiga komponen:
- Kesesuaian profil: 30%.
- Pencapaian target kompetensi: 50%.
- Relevansi karier dan minat: 20%.

Penilaian ini dihitung langsung oleh aplikasi menggunakan aturan yang sudah ditentukan.

**2. Generative AI HR Evaluator**

Menyediakan opini tambahan untuk membantu HR memahami profil kandidat dengan lebih mudah.

Hasil evaluasi dapat mencakup:
- Alasan kandidat memperoleh penilaian.
- Kelebihan yang teridentifikasi.
- Hal yang masih perlu diperiksa oleh HR.

Integrasi ini menggunakan Groq sebagai layanan utama dan Gemini sebagai layanan cadangan apabila diaktifkan oleh administrator.

Penggunaan layanan AI eksternal bersifat opsional dan memerlukan persetujuan sebelum ringkasan data kandidat dikirimkan.

### F. Shortlist Kandidat

Memungkinkan pengguna menyimpan kandidat yang menarik untuk dipertimbangkan lebih lanjut.

Kandidat dapat ditambahkan ke shortlist melalui:
- Detail kandidat pada hasil Weighted KNN.
- Detail kandidat pada hasil Weighted Scoring.
- Detail hasil evaluasi Generative AI.

Daftar shortlist dapat dilihat kembali dan diunduh dalam format CSV.

### G. Panduan Aplikasi

Menyediakan informasi mengenai cara penggunaan aplikasi, metode pencocokan, dan penjelasan dimensi kompetensi M1–M9.

---

## 4. Bagaimana Cara Menggunakan Aplikasi?

Berikut alur penggunaan VINIX7 Talent Discovery dari awal sampai mendapatkan rekomendasi kandidat.

**Langkah 1 — Buka Dasbor Analitik**

Mulai dengan melihat ringkasan dataset dan distribusi profil kandidat yang tersedia.

**Langkah 2 — Tentukan Kebutuhan Posisi**

Buka halaman Pencarian Kriteria, kemudian masukkan posisi yang sedang dibutuhkan perusahaan.

**Langkah 3 — Pilih Kriteria Kandidat**

Tentukan persyaratan yang relevan, seperti program studi, kategori IPK, nilai kerja, dan informasi profil lainnya.

**Langkah 4 — Tentukan Kompetensi**

Pilih 2–9 dimensi M1–M9 sesuai kebutuhan posisi. Masukkan target kompetensi yang ingin dicapai kandidat.

**Langkah 5 — Jalankan Pencarian**

Sistem akan memproses kriteria, menerapkan hard filter, dan menghitung kesesuaian kandidat menggunakan Weighted KNN dan WSM.

**Langkah 6 — Tinjau Hasil Rekomendasi**

Periksa daftar kandidat, nilai jarak KNN, skor WSM, serta perbandingan peringkat dari kedua metode.

**Langkah 7 — Jalankan Evaluasi Kandidat**

Gunakan evaluasi berbasis rubrik internal atau opini tambahan Generative AI jika layanan eksternal sudah diaktifkan.

**Langkah 8 — Simpan Kandidat Pilihan**

Tambahkan kandidat yang ingin dipertimbangkan ke Shortlist. Daftar tersebut dapat ditinjau kembali dan diunduh sebagai file CSV.

---

## 5. Metode Penilaian yang Digunakan

### Weighted KNN

Weighted KNN menggabungkan jarak profil dan jarak kompetensi menggunakan bobot 70:30.

Rumus:

`Final Distance = √(0.70 × Profile Distance² + 0.30 × Competency Distance²)`

Nilai yang lebih kecil menunjukkan kandidat lebih dekat dengan kriteria pencarian.

### Weighted Scoring Model

WSM mengubah kedua komponen menjadi skor kesesuaian, kemudian menggabungkannya secara linear.

Rumus:

`WSM = (0.70 × Profile Fit) + (0.30 × Competency Fit)`

Skor WSM berada pada skala 0–100 dan bersifat relatif terhadap kandidat yang lolos filter pada pencarian tersebut.

**Catatan:** Final Distance dan skor WSM memiliki cara perhitungan berbeda. Keduanya bukan persentase peluang kandidat diterima.

---

## 6. Teknologi yang Digunakan

Aplikasi VINIX7 Talent Discovery dikembangkan menggunakan beberapa teknologi berikut:

| Teknologi | Penggunaan |
|---|---|
| Python | Bahasa pemrograman utama |
| Streamlit | Pengembangan antarmuka web |
| Pandas | Pengolahan dan pengelolaan data |
| NumPy | Operasi numerik |
| Scikit-learn | Perhitungan dan pengolahan model pencocokan |
| Joblib | Penyimpanan dan pemuatan model |
| Groq API | Layanan Generative AI utama |
| Gemini API | Layanan Generative AI cadangan |
| Streamlit Community Cloud | Hosting dan deployment aplikasi |

---


## 7. Manfaat VINIX7 Talent Discovery

Melalui aplikasi ini, proses pencarian kandidat dapat dilakukan dengan lebih terstruktur.

Beberapa manfaat yang diharapkan antara lain:

- **Mempermudah pencarian kandidat:** perusahaan dapat menemukan kandidat berdasarkan kebutuhan posisi tanpa harus memeriksa setiap profil secara manual dari awal.
- **Menghemat waktu penyaringan:** sistem membantu mengerucutkan ribuan profil menjadi daftar kandidat yang lebih mudah ditinjau.
- **Mempertimbangkan banyak aspek:** pencocokan tidak hanya melihat latar belakang pendidikan, tetapi juga minat karier, nilai kerja, dan kompetensi.
- **Memberikan dasar perbandingan:** perusahaan dapat melihat hasil dari Weighted KNN dan WSM.
- **Memudahkan pembahasan kandidat:** fitur shortlist membantu menyimpan kandidat yang ingin dipertimbangkan lebih lanjut.
- **Mendukung evaluasi HR:** hasil penilaian dan penjelasan tambahan dapat digunakan sebagai bahan pertimbangan sebelum proses seleksi berikutnya.

---

## 8. Catatan dan Batasan Penggunaan

VINIX7 Talent Discovery dikembangkan sebagai alat bantu pencarian dan peninjauan kandidat, bukan sebagai pengganti keputusan HR.

Beberapa hal yang perlu diperhatikan:

- Hasil ranking bergantung pada kriteria dan bobot yang dimasukkan perusahaan.
- Belum tersedia label penilaian HR atau riwayat hasil rekrutmen sebagai dasar validasi akurasi rekomendasi.
- Korelasi antar-metode menunjukkan kesamaan urutan ranking, bukan akurasi penerimaan kandidat.
- Hasil Generative AI dapat mengandung kesalahan dan perlu diperiksa kembali.
- Keputusan akhir mengenai kandidat tetap menjadi tanggung jawab perusahaan.
- Shortlist saat ini disimpan menggunakan session state Streamlit. Data shortlist belum menggunakan database permanen dan dapat hilang ketika sesi berakhir.
- Aplikasi belum menyediakan sistem login, pembagian hak akses perusahaan, dan audit log.

Perusahaan perlu memastikan penggunaan data kandidat sesuai dengan izin, kebijakan privasi, dan ketentuan perlindungan data yang berlaku.

---

---

## 9. Penutup

VINIX7 Talent Discovery diharapkan dapat membantu perusahaan memanfaatkan data kandidat dengan lebih baik, mempercepat proses pencarian talenta, serta memberikan gambaran yang lebih terstruktur dalam meninjau kesesuaian kandidat dengan kebutuhan posisi.

Melalui kombinasi pengolahan data, metode pencocokan, dan evaluasi kandidat, aplikasi ini menjadi salah satu upaya untuk menghubungkan potensi talenta dengan kebutuhan dunia industri.

**VINIX7 Talent Discovery — Connecting Talent with Industry Needs.**
