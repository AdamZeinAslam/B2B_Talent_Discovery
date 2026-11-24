from __future__ import annotations

import pandas as pd
import streamlit as st
import altair as alt

from components import page_header, radar_svg, section_heading

PROGRAM_STUDY_EXCLUDED = {"ti", "universitas airlangga", "universitas pancasila"}

INTEREST_LABELS = {
    "tech": "Teknologi", "biz": "Bisnis", "finance": "Keuangan",
    "creative": "Kreatif", "edu": "Pendidikan", "industry": "Industri",
    "ecom": "E-commerce", "govt": "Pemerintahan", "health": "Kesehatan",
    "social": "Sosial",
}


def _top_chart(frame: pd.DataFrame, label_col: str, count_col: str, color: str = "#17428F"):
    chart = alt.Chart(frame).mark_bar(color=color, cornerRadiusEnd=4, size=17).encode(
        y=alt.Y(f"{label_col}:N", sort="-x", title=None,
                axis=alt.Axis(labelLimit=250, labelFontSize=11, ticks=False, domain=False)),
        x=alt.X(f"{count_col}:Q", title="Jumlah kandidat",
                axis=alt.Axis(labelFontSize=10, titleFontSize=11, grid=True)),
        tooltip=[alt.Tooltip(f"{label_col}:N", title="Kategori"),
                 alt.Tooltip(f"{count_col}:Q", title="Jumlah", format=",")],
    ).properties(height=max(250, min(360, len(frame) * 29 + 30)))
    labels = alt.Chart(frame).mark_text(align="left", baseline="middle", dx=5,
                                        color="#25344B", fontSize=10).encode(
        y=alt.Y(f"{label_col}:N", sort="-x"),
        x=alt.X(f"{count_col}:Q"),
        text=alt.Text(f"{count_col}:Q", format=",")
    )
    # Padding belongs to the top-level LayerChart, not to an individual
    # chart layer. Putting padding on `chart` makes Altair reject the layer
    # with: "Objects with 'padding' attribute cannot be used within LayerChart".
    layered = (chart + labels).properties(padding={"left": 2, "right": 12})
    return layered.configure_view(stroke=None).configure_axis(
        gridColor="#E9EDF3", domainColor="#D8DFE9", labelColor="#536176", titleColor="#536176"
    )


def _prepare_top_values(profile: pd.DataFrame, column: str, top_n: int = 10) -> pd.DataFrame:
    series = profile[column].dropna().astype(str).str.strip()
    series = series[series.ne("")]
    counts = series.value_counts().head(top_n)
    return counts.rename_axis("Kategori").reset_index(name="Jumlah")


def _prepare_interests(profile: pd.DataFrame) -> pd.DataFrame:
    series = profile["Bidang Minat"].dropna().astype(str)
    counts: dict[str, int] = {}
    for raw in series:
        tokens = {token.strip().casefold() for token in raw.split(",") if token.strip()}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
    rows = [
        {"Bidang": INTEREST_LABELS.get(key, key.title()), "Jumlah": value}
        for key, value in counts.items()
    ]
    return pd.DataFrame(rows).sort_values("Jumlah", ascending=False).head(10).reset_index(drop=True)


def render(bundle: dict) -> None:
    profile: pd.DataFrame = bundle["candidate_profile"].copy()
    model_features: pd.DataFrame = bundle["candidate_model_features"]

    page_header(
        "OVERVIEW",
        "Talent Discovery",
        "Portal pencarian kandidat VINIX7 untuk membantu mitra industri menyusun shortlist berdasarkan kebutuhan posisi, profil, dan kompetensi.",
    )

    _axes = [{"code": f"M{i}", "max": 1} for i in range(1, 10)]
    _codes = [a["code"] for a in _axes]
    _demo = [
        {"cls": "tgt", "values": dict(zip(_codes, [.80, .70, .60, .85, .70, .55, .75, .80, .65]))},
        {"cls": "cand", "values": dict(zip(_codes, [.78, .66, .62, .80, .72, .50, .70, .82, .60]))},
        {"cls": "cand c2", "values": dict(zip(_codes, [.70, .60, .50, .75, .60, .62, .66, .70, .72]))},
        {"cls": "cand c3", "values": dict(zip(_codes, [.55, .78, .72, .62, .58, .45, .60, .68, .50]))},
    ]
    st.markdown(
        "<div class='hero2'><div><div class='hero2-kicker'>Weighted KNN · WSM · 9 dimensi kompetensi</div>"
        "<h2>Temukan talenta yang mendekati kebutuhan tim.</h2>"
        "<p>Tentukan profil dan target kompetensi, lalu tinjau kandidat yang jaraknya paling dekat ke kebutuhan posisi.</p></div>"
        f"<div class='hero2-viz'>{radar_svg(_axes, _demo, size=340, dark=True, animate=True)}"
        "<div class='legend'><span><i></i>Profil target</span><span><i class='c'></i>Kandidat terdekat</span></div>"
        "<div class='hero2-cap'>Ilustrasi konsep, bukan data kandidat.</div></div></div>",
        unsafe_allow_html=True,
    )

    valid_programs = model_features["Program Studi"].dropna().astype(str).str.strip()
    valid_programs = valid_programs[~valid_programs.str.casefold().isin(PROGRAM_STUDY_EXCLUDED)]

    valid_universities = profile["Perguruan Tinggi"].dropna().astype(str).str.strip()
    valid_universities = valid_universities[
        ~valid_universities.str.casefold().isin({"", "-", "nan", "none", "tidak diketahui"})
    ]

    col1, col2, col3 = st.columns(3)
    col1.metric("Profil kandidat", f"{len(profile):,}")
    col2.metric("Program studi", f"{valid_programs.nunique():,}")
    col3.metric("Jumlah perguruan tinggi", f"{valid_universities.nunique():,}")

    st.divider()
    section_heading("Insight database kandidat", "Ringkasan distribusi pendidikan dan minat berdasarkan data kandidat yang tersedia.")

    universities = _prepare_top_values(profile, "Perguruan Tinggi", 10)
    program_profile = profile.copy()
    program_values = program_profile["Program Studi"].astype("string").str.strip()
    program_profile = program_profile[~program_values.str.casefold().isin(PROGRAM_STUDY_EXCLUDED)]
    programs = _prepare_top_values(program_profile, "Program Studi", 10)
    interests = _prepare_interests(profile)

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("**10 perguruan tinggi dengan kandidat terbanyak**")
        if not universities.empty:
            st.altair_chart(_top_chart(universities, "Kategori", "Jumlah"), use_container_width=True)
            st.caption(f"Dihitung dari {profile['Perguruan Tinggi'].notna().sum():,} profil dengan data perguruan tinggi.")
    with right:
        st.markdown("**10 program studi dengan kandidat terbanyak**")
        if not programs.empty:
            st.altair_chart(_top_chart(programs, "Kategori", "Jumlah", color="#1D5AA6"), use_container_width=True)
            st.caption(f"Dihitung dari {program_profile['Program Studi'].notna().sum():,} profil setelah mengeluarkan tiga entri yang salah kolom.")

    st.write("")
    st.markdown("**Bidang minat yang paling banyak dipilih**")
    if not interests.empty:
        st.altair_chart(_top_chart(interests, "Bidang", "Jumlah", color="#D3AE22"), use_container_width=True)
        st.caption("Satu kandidat dapat memilih lebih dari satu bidang minat, sehingga jumlah pilihan dapat melebihi jumlah kandidat.")

    st.divider()
    section_heading("Alur kerja", "Gunakan portal dalam urutan berikut untuk membuat rekomendasi yang dapat ditinjau.")
    steps = [
        ("01", "Tentukan posisi", "Masukkan nama perusahaan dan posisi yang dibutuhkan."),
        ("02", "Tetapkan kriteria", "Pilih hard filter dan preferensi yang relevan."),
        ("03", "Atur kompetensi", "Pilih 2–9 dimensi M1–M9 dan target skornya."),
        ("04", "Tinjau hasil", "Bandingkan ranking, baca alasan, lalu buat shortlist."),
    ]
    cols = st.columns(4, gap="medium")
    for col, (number, title, copy) in zip(cols, steps):
        with col:
            st.markdown(
                f"<div class='step-card'><div class='step-number'>{number}</div>"
                f"<div class='step-title'>{title}</div><div class='step-copy'>{copy}</div></div>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.info(
        "Gunakan hasil sebagai rekomendasi awal. Belum tersedia label relevansi dari HR atau outcome rekrutmen historis, "
        "sehingga aplikasi belum dapat menyatakan akurasi atau keberhasilan seleksi."
    )
    if st.button("Mulai pencarian kandidat", type="primary"):
        st.session_state.page = "Cari Kandidat"
        st.rerun()
