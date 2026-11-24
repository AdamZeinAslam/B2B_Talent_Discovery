# Menjalankan VINIX7 Talent Discovery di Google Colab dan Streamlit Community Cloud

## 1. Upload dan ekstrak

Gunakan cell upload/ekstraksi otomatis yang mencari `app.py` di dalam ZIP, sehingga nama ZIP dan folder induk boleh berbeda. Setelah folder aplikasi ditemukan, jalankan `os.chdir(PROJECT_DIR)`.

## 2. Install dependensi

```python
!pip install -r requirements.txt
```

## 3. Jalankan Streamlit

```python
!streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

Gunakan tunnel untuk mengakses aplikasi dari browser jika menjalankan di Colab. URL Quick Tunnel bersifat sementara.

## 4. Evaluasi kandidat selalu tersedia

Buka **Hasil & Perbandingan → 04 Evaluasi Kandidat**, lalu klik **Jalankan evaluasi kandidat**. Aplikasi menghitung skor menggunakan rubrik internal secara lokal; proses ini tidak membutuhkan API key, layanan AI eksternal, atau kuota model. Hasil memuat rincian 30 poin profil, 50 poin pencapaian kompetensi, dan 20 poin relevansi karier/minat.

Rubrik internal bukan generative AI dan belum divalidasi terhadap penilaian HR manusia. Gunakan sebagai alat bantu peninjauan, bukan keputusan otomatis.

## 5. Generative AI: Groq utama dan Gemini cadangan

Tambahkan secret berikut di Google Colab Secrets atau Streamlit Community Cloud → Settings → Secrets. Jangan masukkan key ke source code/GitHub.

```toml
GROQ_API_KEY = "isi_api_key_groq"
GEMINI_API_KEY = "isi_api_key_gemini"
GROQ_MODEL = "openai/gpt-oss-20b"
GEMINI_MODEL = "gemini-2.5-flash"
ENABLE_GEMINI_FALLBACK = true
```

Aplikasi mencoba Groq terlebih dahulu. Jika permintaan Groq gagal, aplikasi mencoba Gemini hanya jika `ENABLE_GEMINI_FALLBACK = true` dan `GEMINI_API_KEY` tersedia. Jika keduanya gagal, evaluasi rubrik internal tetap tersedia. Ketersediaan model, kuota, dan batas pemakaian mengikuti akun masing-masing penyedia; konfigurasi secret yang terbaca tidak otomatis membuktikan API dapat diakses.

Di Colab, simpan secret dengan nama persis `GROQ_API_KEY` dan `GEMINI_API_KEY`, lalu aktifkan akses notebook. Di Community Cloud, masukkan pasangan key dan konfigurasi model di menu **Settings → Secrets**.

Evaluasi Generative AI hanya dijalankan setelah persetujuan pengguna. Data yang dikirim dibatasi pada ID kandidat pseudonim, informasi relevan posisi/karier, dan kompetensi terpilih. Jangan kirim data pribadi atau data kandidat tanpa dasar pemrosesan dan persetujuan yang sesuai.
