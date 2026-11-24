from __future__ import annotations

import pandas as pd
import streamlit as st

from components import page_header, section_heading

COMPETENCY_GUIDE = [
    {"code": "M1", "name": "Background", "description": "Gambaran latar belakang kandidat yang relevan dengan kebutuhan posisi.", "max": 10},
    {"code": "M2", "name": "Skills", "description": "Gambaran kemampuan atau keterampilan yang dimiliki kandidat.", "max": 15},
    {"code": "M3", "name": "Industry", "description": "Keterkaitan kandidat dengan bidang atau konteks industri yang dituju.", "max": 10},
    {"code": "M4", "name": "Interest", "description": "Gambaran minat kandidat terhadap bidang atau aktivitas pekerjaan.", "max": 15},
    {"code": "M5", "name": "Compass", "description": "Gambaran arah, orientasi, atau tujuan pengembangan karier kandidat.", "max": 10},
    {"code": "M6", "name": "Company", "description": "Gambaran orientasi kandidat terhadap konteks atau lingkungan perusahaan.", "max": 10},
    {"code": "M7", "name": "Branding", "description": "Gambaran cara kandidat membangun dan menyampaikan identitas profesionalnya.", "max": 10},
    {"code": "M8", "name": "Ambisi", "description": "Gambaran dorongan, aspirasi, dan keinginan kandidat untuk berkembang.", "max": 10},
    {"code": "M9", "name": "Resiliensi", "description": "Gambaran ketahanan kandidat dalam menghadapi tantangan atau perubahan.", "max": 10},
]


def render(matcher) -> None:
    page_header(
        "PANDUAN APLIKASI",
        "Panduan penggunaan VINIX7 Talent Discovery",
        "Pelajari alur penggunaan, metode pencocokan, pembobotan, dan indikator asesmen sebelum membuat rekomendasi.",
    )

    section_heading("Alur penggunaan aplikasi", "Ikuti tahapan ini untuk mendapatkan rekomendasi kandidat yang dapat ditinjau.")
    steps = [
        ("01", "Tentukan posisi", "Masukkan nama perusahaan dan posisi yang sedang dibutuhkan."),
        ("02", "Tetapkan filter", "Gunakan Program Studi atau kategori IPK hanya jika benar-benar wajib."),
        ("03", "Pilih kriteria profil", "Masukkan bidang minat, Work Values, pengalaman VINIX7, dan preferensi yang relevan."),
        ("04", "Pilih kompetensi", "Pilih 2–9 dimensi M1–M9 dan tetapkan target skornya."),
        ("05", "Evaluasi hasil", "Bandingkan ranking dan jalankan evaluasi kandidat berbasis rubrik internal."),
        ("06", "Buat shortlist", "Simpan kandidat untuk ditinjau lebih lanjut oleh tim HR/perusahaan."),
    ]
    for start in range(0, len(steps), 2):
        cols = st.columns(2)
        for col, step in zip(cols, steps[start:start + 2]):
            with col:
                number, title, description = step
                st.markdown(
                    f"<div class='step-card'><div class='step-number'>{number}</div>"
                    f"<div class='step-title'>{title}</div><div class='step-copy'>{description}</div></div>",
                    unsafe_allow_html=True,
                )
        st.write("")

    st.divider()
    section_heading("Metode penilaian dan pembobotan", "Dua metode pencocokan ditambah evaluasi rubrik internal untuk membantu peninjauan kandidat.")
    with st.container(border=True):
        st.markdown("**01 · Weighted KNN — metode utama**")
        st.write("Mengukur jarak kandidat terhadap profil dan target kompetensi perusahaan menggunakan weighted Euclidean distance.")
        m1, m2 = st.columns(2)
        m1.metric("Bobot kesesuaian profil", "70%")
        m2.metric("Bobot kesesuaian kompetensi", "30%")
        st.latex(r"FinalDistance=\sqrt{0.70\,ProfileDistance^2+0.30\,CompetencyDistance^2}")
        st.caption("Semakin kecil Final Distance, semakin dekat kandidat terhadap kombinasi kriteria. Final Distance bukan persentase kecocokan.")
    with st.container(border=True):
        st.markdown("**02 · Weighted Scoring Model — metode pembanding**")
        st.write("Mengubah jarak profil dan kompetensi menjadi skor kesesuaian relatif, lalu menggabungkannya secara linear.")
        st.latex(r"WSM=0.70\times ProfileFit+0.30\times CompetencyFit")
        st.caption("Skor WSM 0–100 adalah skor relatif terhadap kandidat yang lolos filter pada pencarian tersebut, bukan probabilitas diterima.")
    with st.container(border=True):
        st.markdown("**03 · Evaluasi kandidat berbasis rubrik internal — selalu tersedia**")
        st.write("Aplikasi menghitung skor eksploratif dengan rumus tetap untuk kandidat gabungan Top 10 KNN dan Top 10 WSM. Evaluasi ini berjalan di dalam aplikasi dan tidak membutuhkan API key atau layanan eksternal.")
        st.latex(r"EvaluationScore = 0.30(ProfileFit) + 0.50(CompetencyAttainment) + 0.20(CareerRelevance)")
        st.caption("Skor ini adalah alat bantu berbasis aturan, bukan generative AI, bukan label kebenaran HR, dan bukan dasar tunggal keputusan rekrutmen.")
    with st.container(border=True):
        st.markdown("**Opini tambahan generative AI — opsional**")
        st.write("Jika administrator menghubungkan layanan AI eksternal dan kebijakan privasi mengizinkan, aplikasi dapat meminta opini pembanding tambahan. Evaluasi rubrik internal tetap berjalan meskipun layanan eksternal tidak tersedia.")

    st.divider()
    section_heading("Dimensi kompetensi M1–M9", "Nama dan skala maksimum mengikuti bundle model. Deskripsi adalah penjelasan operasional, bukan rubrik resmi.")
    guide_frame = pd.DataFrame([
        {"Kode": item["code"], "Dimensi": item["name"], "Gambaran": item["description"],
         "Skala maksimum": matcher.competency_scale_max[matcher.competency_mapping[item["code"]]]}
        for item in COMPETENCY_GUIDE
    ])
    st.dataframe(guide_frame, hide_index=True, use_container_width=True,
                 column_config={"Gambaran": st.column_config.TextColumn(width="large")})
    st.warning(
        "Penjelasan dimensi di atas merupakan interpretasi berdasarkan label indikator. Untuk menetapkan target skor secara presisi, "
        "gunakan pedoman asesmen resmi VINIX7. M2 dan M4 mempunyai skala maksimum berbeda dari dimensi lainnya."
    )

    with st.expander("Catatan penggunaan dan batasan model"):
        st.markdown(
            "- Total M1–M9 dan rata-rata kompetensi merupakan informasi asesmen; bukan fitur yang menentukan ranking KNN.\n"
            "- Bobot 70:30 merupakan konfigurasi eksperimen saat ini, belum dibuktikan sebagai bobot optimal melalui validasi HR.\n"
            "- Skor WSM dinormalisasi terhadap kandidat yang lolos filter pada pencarian tersebut; jangan dibandingkan sebagai skor absolut antar-posisi.\n"
            "- IPK disimpan sebagai kode kategori 1–4. Pemetaan kategori harus diverifikasi terhadap kuesioner resmi sebelum digunakan untuk keputusan operasional.\n"
            "- Evaluasi utama berjalan secara lokal dengan rubrik internal. Opini generative AI eksternal bersifat opsional dan memerlukan persetujuan pemrosesan data.\n"
            "- Belum tersedia label relevansi HR atau outcome rekrutmen historis. Semua ranking harus ditinjau recruiter/manusia."
        )

    if st.button("Buat pencarian kandidat", type="primary"):
        st.session_state.page = "Cari Kandidat"
        st.rerun()
