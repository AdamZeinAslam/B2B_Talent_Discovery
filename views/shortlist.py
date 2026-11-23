from __future__ import annotations

import pandas as pd
import streamlit as st

from components import page_header
from views.results import IPK_LABELS


def render() -> None:
    page_header(
        "SHORTLIST KANDIDAT",
        "Kandidat yang ingin ditinjau lebih lanjut.",
        "Simpan kandidat dari hasil rekomendasi untuk memudahkan pembahasan internal perusahaan.",
    )
    shortlist = st.session_state.setdefault("shortlist", {})
    if not shortlist:
        st.info("Shortlist masih kosong. Buka hasil rekomendasi dan tambahkan kandidat yang ingin dipertimbangkan.")
        if st.button("Lihat hasil rekomendasi", type="primary"):
            st.session_state.page = "Hasil Rekomendasi"
            st.rerun()
        return

    rows = list(shortlist.values())
    df = pd.DataFrame(rows)
    df["IPK"] = pd.to_numeric(df["IPK"], errors="coerce").map(IPK_LABELS).fillna("Tidak diketahui")
    columns = [c for c in ["Candidate_ID", "KNN Rank", "WSM Rank", "Program Studi", "Perguruan Tinggi", "IPK", "Dream Job Utama", "WSM Score", "Final Distance"] if c in df.columns]
    st.metric("Kandidat dalam shortlist", len(df))
    st.dataframe(df[columns], hide_index=True, use_container_width=True,
                 column_config={
                     "Final Distance": st.column_config.NumberColumn(format="%.4f"),
                     "WSM Score": st.column_config.NumberColumn(format="%.2f"),
                 })

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Unduh shortlist (CSV)",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="talentmatch_shortlist.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        if st.button("Kosongkan shortlist", use_container_width=True):
            st.session_state.shortlist = {}
            st.rerun()
    st.caption("Shortlist ini tersimpan selama sesi aplikasi berjalan. Belum menggunakan database permanen.")
