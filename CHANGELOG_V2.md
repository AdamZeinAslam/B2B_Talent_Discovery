# Perubahan VINIX7 Talent Discovery v2

- Mempertahankan Weighted KNN sebagai metode utama dan menjaga Top 10 tetap cocok dengan referensi bundle.
- Menambahkan Weighted Scoring Model (WSM) sebagai pembanding dengan agregasi linear Profile Fit dan Competency Fit.
- Menambahkan halaman/tab perbandingan: overlap Top 10, rank KNN, rank WSM, dan korelasi Spearman.
- Menambahkan AI HR Evaluator opsional melalui OpenAI Responses API dengan structured JSON output.
- AI hanya menerima gabungan Top 10 KNN dan Top 10 WSM (maksimal 20 kandidat unik); Candidate_ID pseudonim, tanpa Total Score, Skor Kualitas, atau kode IPK.
- Menambahkan checkbox persetujuan pengiriman data ke API eksternal dan larangan penggunaan hasil AI sebagai keputusan otomatis.
- Menyederhanakan tampilan menjadi gaya enterprise operasional dengan identitas warna VINIX7, mengurangi panel dekoratif dan tampilan berlebihan.
- Memperjelas panduan M1–M9, komposisi metode, batasan skor WSM, serta penggunaan kampus dan tempat magang sebagai preferensi opsional.
- Menambahkan referensi hasil WSM dan memperluas `verify_integration.py` untuk memeriksa KNN, WSM, dan payload sampel AI tanpa memanggil API.

## Hotfix UI (22 November 2026)

- Memperbaiki `StreamlitDuplicateElementKey` pada tab KNN dan WSM: setiap detail kandidat dan tombol shortlist kini memiliki key unik per metode (`knn`/`wsm`).
- Menambahkan key eksplisit pada expander hasil AI HR untuk mencegah konflik identitas elemen.
- Tidak mengubah perhitungan KNN, WSM, bundle model, atau ranking kandidat.


## Revisi Overview, Form, dan OpenRouter (22 November 2026)

- Logo VINIX7 dipotong ke area logo dan dipusatkan di sidebar dengan aset retina-size.
- Overview menampilkan tepat tiga chart: perguruan tinggi terbanyak, program studi terbanyak, dan bidang minat paling sering dipilih.
- Panel metode dan pembobotan dipindahkan dari Overview ke Panduan Aplikasi.
- Navigasi Panduan diubah menjadi Panduan Aplikasi.
- Opsi Program Studi `TI`, `Universitas Airlangga`, dan `Universitas Pancasila` disembunyikan dari dropdown Program Studi saja; data kandidat tidak dihapus.
- Filter pengalaman di VINIX7 ditambahkan dengan opsi pernah, tidak pernah (catatan magang terisi), atau tidak dijadikan kriteria. Data kosong tidak diasumsikan sebagai tidak pernah.
- AI HR Evaluator dialihkan dari OpenAI Responses API ke OpenRouter Chat Completions dengan model `google/gemma-4-26b-a4b-it:free`. API key hanya dibaca dari environment/Streamlit Secrets, tidak dimasukkan ke ZIP.
- Payload AI diminimalkan: tidak mengirim nama, kontak, kampus, tempat magang, Total Score, atau Skor Kualitas.
- Label empat tab hasil diperbesar dan active state diperjelas.


## Perbaikan AI Evaluator dan pembatasan informasi teknis (22 November 2026)

- Antarmuka pengguna tidak lagi menampilkan nama penyedia, model, atau kebutuhan API key.
- Kredensial disiapkan satu kali oleh administrator melalui environment/Colab Secrets; pengguna hanya membaca pemberitahuan privasi dan memberi persetujuan.
- Perutean model menggunakan pemilihan otomatis model gratis yang tersedia.
- Penanganan 429 dibedakan antara kuota akun dan kapasitas penyedia; retry terbatas hanya untuk gangguan kapasitas penyedia.
- Pesan error disederhanakan agar tidak membocorkan detail teknis penyedia kepada pengguna.
- Hasil AI disimpan per signature kebutuhan dan sampel kandidat selama sesi, sehingga hasil lama tidak salah ditampilkan untuk pencarian baru.


## Revisi evaluasi tanpa ketergantungan layanan eksternal (22 November 2026)

- Menambahkan evaluasi kandidat berbasis rubrik internal dengan formula 30 poin profil, 50 poin pencapaian target kompetensi, dan 20 poin relevansi karier/minat.
- Evaluasi internal berjalan lokal dan selalu tersedia tanpa API key, kuota model, atau layanan eksternal.
- Opini generative AI dipindahkan menjadi fitur tambahan opsional dan tidak lagi menjadi prasyarat evaluasi.
- Overview: menghapus caption “Pilihan valid pada form” dan mengganti metrik “Dimensi kompetensi” menjadi “Jumlah perguruan tinggi”.


## Integrasi Generative AI Groq + Gemini (24 November 2026)

- Mengganti provider AI eksternal lama dengan Groq sebagai provider utama dan Gemini sebagai fallback opsional.
- Konfigurasi default: `openai/gpt-oss-20b` untuk Groq dan `gemini-2.5-flash` untuk Gemini.
- Tombol utama evaluasi kandidat menjalankan Generative AI setelah persetujuan pengguna dan API tersedia.
- Jika Groq gagal, aplikasi mencoba Gemini saat `ENABLE_GEMINI_FALLBACK=true`; jika layanan AI gagal, rubrik internal tetap menghasilkan evaluasi lokal.
- Menyederhanakan instruksi AI dan label hasil menjadi bahasa Indonesia yang lebih mudah dipahami.
- Tombol shortlist sudah tersedia di dalam detail kandidat pada tab Weighted KNN dan Weighted Scoring; aksi memakai key terpisah per metode.
- Desain/CSS, tata letak utama, dan struktur empat tab dipertahankan.
- Pengujian provider memakai mock lokal; belum melakukan panggilan live karena API key pengguna tidak tersedia di lingkungan pengujian.
