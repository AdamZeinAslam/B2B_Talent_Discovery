from __future__ import annotations

from typing import Any
import pandas as pd
import streamlit as st

from components import page_header, section_heading
from views.guide import COMPETENCY_GUIDE

IPK_FILTERS = {
    "Tidak ada batas minimum": None,
    "Mulai kategori 2.50–2.99": 2.50,
    "Mulai kategori 3.00–3.49": 3.00,
    "Mulai kategori 3.50–4.00": 3.50,
}


def _none_option(options: list[str]) -> list[str]:
    return ["Tidak ditentukan"] + options


def render(matcher) -> None:
    options = matcher.available_options()
    competency_options = matcher.competency_options()
    competency_labels = {item["code"]: f"{item['label']} · skala 0–{item['max']}" for item in competency_options}
    competency_by_code = {item["code"]: item for item in competency_options}
    guide_by_code = {item["code"]: item for item in COMPETENCY_GUIDE}

    page_header(
        "PENCARIAN KANDIDAT",
        "Buat kebutuhan kandidat baru.",
        "Isi kriteria secara bertahap. Gunakan hanya persyaratan yang relevan dengan posisi; kolom opsional yang tidak dipilih tidak akan digunakan dalam pencocokan.",
    )

    with st.container(border=True):
        section_heading("A. Informasi posisi", "Informasi ini digunakan untuk memberi konteks pada hasil pencarian.")
        c1, c2 = st.columns(2)
        with c1:
            company_name = st.text_input("Nama perusahaan", placeholder="Contoh: PT Contoh Indonesia", key="company_name")
        with c2:
            position_title = st.text_input("Posisi yang dibutuhkan *", placeholder="Contoh: Data Analyst", key="position_title")

    with st.container(border=True):
        section_heading("B. Filter awal kandidat", "Hard filter diterapkan sebelum penghitungan jarak. Gunakan hanya jika menjadi persyaratan wajib.")
        c1, c2 = st.columns(2)
        with c1:
            program_choice = st.selectbox(
                "Program Studi",
                ["Semua Program Studi"] + options["Program Studi"],
                help="Jika program studi tidak wajib, biarkan pada Semua Program Studi.", key="program_choice",
            )
        with c2:
            ipk_choice = st.selectbox(
                "IPK minimum",
                list(IPK_FILTERS.keys()),
                help="Data IPK tersimpan sebagai kategori 1–4, bukan IPK desimal individual.", key="ipk_choice",
            )
        st.caption("Catatan: IPK tersimpan sebagai kode kategori 1–4. Pemetaan kategori pada bundle harus diverifikasi terhadap kuesioner resmi VINIX7 sebelum filter ini digunakan untuk keputusan operasional.")
        st.warning("Perguruan Tinggi dan Tempat Magang tidak perlu dipilih sebagai syarat umum. Keduanya memengaruhi jarak profil bila dipilih, sehingga sebaiknya dibiarkan kosong kecuali ada alasan rekrutmen yang jelas.")

    with st.container(border=True):
        section_heading("C. Profil kandidat yang dicari", "Pilih kriteria tambahan yang relevan. Perguruan Tinggi bersifat opsional, sedangkan pengalaman magang VINIX7 dapat digunakan sebagai filter tersendiri.")
        st.markdown("**Jabatan / Dream Job**")
        st.caption("Nama posisi menjadi teks pencarian utama pada fitur Dream Job. Contoh: Data Analyst, Frontend Developer, atau Business Analyst.")
        c1, c2 = st.columns(2)
        with c1:
            interests = st.multiselect("Bidang Minat", options["Bidang Minat"], help="Boleh memilih lebih dari satu bidang.", key="interests")
            values = st.multiselect("Work Values", options["Work Values"], help="Pilih nilai kerja yang penting bagi perusahaan atau tim.", key="work_values")
            campus = st.selectbox("Perguruan Tinggi (opsional)", _none_option(options["Perguruan Tinggi"]), help="Pilihan ini hanya preferensi tambahan. Hindari menjadikan nama kampus sebagai syarat umum rekrutmen.", key="campus")
            vinix_experience = st.radio(
                "Pengalaman magang di VINIX7",
                ["Tidak dijadikan kriteria", "Pernah magang di VINIX7", "Tidak pernah magang di VINIX7"],
                index=0,
                help="Pilihan 'tidak pernah' hanya mencakup kandidat dengan catatan tempat magang yang terisi dan bukan VINIX7. Data kosong diperlakukan sebagai tidak diketahui.",
                key="vinix_experience_filter",
            )
            st.caption("Pilih 'Tidak dijadikan kriteria' bila pengalaman di VINIX7 tidak perlu memengaruhi pencarian.")
        with c2:
            motivation = st.selectbox("Motivasi", _none_option(options["Motivasi"]), key="motivation")
            cognitive = st.selectbox("Cognitive Style", _none_option(options["Cognitive Style"]), key="cognitive")
            company_size = st.selectbox("Ukuran Perusahaan", _none_option(options["Ukuran Perusahaan"]), key="company_size")
            work_culture = st.selectbox("Kultur Kerja", _none_option(options["Kultur Kerja"]), key="work_culture")
            location = st.selectbox("Preferensi Lokasi", _none_option(options["Preferensi Lokasi"]), key="location")
            english = st.selectbox("Level Bahasa Inggris", ["Tidak ditentukan"] + [f"Level {level}" for level in options["Level Bahasa Inggris"]], key="english_level")

    with st.container(border=True):
        section_heading("D. Kompetensi yang dibutuhkan", "Pilih 2–9 dimensi M1–M9. Sistem hanya menghitung dimensi yang kamu pilih.")
        with st.expander("Lihat penjelasan setiap dimensi M1–M9", expanded=True):
            guide_rows = []
            for item in COMPETENCY_GUIDE:
                model_item = competency_by_code[item["code"]]
                guide_rows.append({
                    "Kode": item["code"], "Dimensi": item["name"],
                    "Gambaran": item["description"], "Skala target": f"0–{model_item['max']}",
                })
            st.dataframe(pd.DataFrame(guide_rows), hide_index=True, use_container_width=True,
                         column_config={"Gambaran": st.column_config.TextColumn(width="large")})
            st.caption("Deskripsi merupakan penjelasan operasional dari nama indikator, bukan rubrik penilaian resmi. Gunakan pedoman resmi VINIX7 untuk menetapkan skor target secara lebih akurat.")

        selected_codes = st.multiselect(
            "Pilih kompetensi yang relevan",
            options=[item["code"] for item in competency_options],
            format_func=lambda code: competency_labels[code],
            help="Minimal 2 dan maksimal 9 kompetensi. Tidak wajib memilih semuanya.",
            key="selected_competencies",
        )
        target_values: dict[str, float] = {}
        if selected_codes:
            st.markdown("**Tentukan skor target untuk posisi ini**")
            st.caption("Rentang nilai mengikuti skala masing-masing dimensi. Target adalah nilai acuan yang ingin dicari pada data kandidat, bukan persentase.")
            score_cols = st.columns(2)
            for index, code in enumerate(selected_codes):
                item = competency_by_code[code]
                with score_cols[index % 2]:
                    target_values[code] = st.slider(
                        f"{item['label']}", min_value=0, max_value=item["max"],
                        value=max(0, min(item["max"], round(item["max"] * 0.7))), step=1,
                        help=f"Target skala 0 sampai {item['max']}. Atur berdasarkan kebutuhan posisi dan rubrik skor yang berlaku.",
                        key=f"target_{code}",
                    )
        else:
            st.info("Pilih paling sedikit dua kompetensi untuk menampilkan pengaturan target skor.")

    st.write("")
    submitted = st.button("Cari 10 kandidat", type="primary", use_container_width=True, key="run_matching")
    st.caption("KNN dan WSM menggunakan bobot 70% profil dan 30% kompetensi. Perbedaannya terletak pada cara menggabungkan kedua komponen tersebut.")

    if submitted:
        errors = []
        if not position_title.strip():
            errors.append("Nama posisi perlu diisi.")
        if not 2 <= len(selected_codes) <= 9:
            errors.append("Pilih minimal 2 dan maksimal 9 kompetensi.")
        if errors:
            for error in errors:
                st.error(error)
            return

        requirement: dict[str, Any] = {
            "Program Studi": None if program_choice == "Semua Program Studi" else program_choice,
            "IPK Minimum": IPK_FILTERS[ipk_choice],
            "Perguruan Tinggi": None if campus == "Tidak ditentukan" else campus,
            "Tempat Magang": None,
            "Pengalaman VINIX7": None if vinix_experience == "Tidak dijadikan kriteria" else vinix_experience,
            "Dream Job": position_title.strip(),
            "Bidang Minat": ", ".join(interests) if interests else None,
            "Work Values": ", ".join(values) if values else None,
            "Motivasi": None if motivation == "Tidak ditentukan" else motivation,
            "Cognitive Style": None if cognitive == "Tidak ditentukan" else cognitive,
            "Ukuran Perusahaan": None if company_size == "Tidak ditentukan" else company_size,
            "Kultur Kerja": None if work_culture == "Tidak ditentukan" else work_culture,
            "Preferensi Lokasi": None if location == "Tidak ditentukan" else location,
            "Level Bahasa Inggris": None if english == "Tidak ditentukan" else int(english.replace("Level ", "")),
        }
        selected_competency_targets = {code: target_values[code] for code in selected_codes}
        try:
            with st.spinner("Menghitung ranking Weighted KNN dan Weighted Scoring..."):
                result = matcher.recommend(requirement, selected_competency_targets)
            st.session_state.match_result = result
            st.session_state.ai_assessment = None
            st.session_state.ai_assessment_signature = None
            st.session_state.ai_assessment_source = None
            st.session_state.ai_external_error = None
            st.session_state.search_context = {
                "company_name": company_name.strip(), "position_title": position_title.strip(),
                "requirement": requirement, "selected_competencies": selected_competency_targets,
            }
            st.session_state.page = "Hasil Rekomendasi"
            st.rerun()
        except Exception as exc:
            st.error(f"Pencarian belum dapat diproses: {exc}")
