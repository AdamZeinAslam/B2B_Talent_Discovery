from __future__ import annotations

import html
import os
import json
import hashlib
import pandas as pd
import streamlit as st

from components import radar_svg, page_header, section_heading
from model.ai_evaluator import build_candidate_payload, evaluate_candidates
from model.rubric_evaluator import evaluate_with_internal_rubric
from views.guide import COMPETENCY_GUIDE

IPK_LABELS = {1: "Di bawah 2.50", 2: "2.50–2.99", 3: "3.00–3.49", 4: "3.50–4.00"}
GUIDE_BY_CODE = {item["code"]: item for item in COMPETENCY_GUIDE}


def _display_ipk(value) -> str:
    number = pd.to_numeric(value, errors="coerce")
    return IPK_LABELS.get(int(number), "Tidak diketahui") if pd.notna(number) else "Tidak diketahui"


def _candidate_table(frame: pd.DataFrame, method: str) -> pd.DataFrame:
    table = frame.copy()
    table["IPK"] = table["IPK"].map(_display_ipk)
    if method == "knn":
        columns = [
            "Ranking", "Candidate_ID", "Program Studi", "Perguruan Tinggi", "IPK",
            "Dream Job Utama", "Final Distance", "Total Score", "Skor Kualitas (0-100)",
        ]
        rename = {
            "Ranking": "Peringkat", "Candidate_ID": "ID Kandidat", "IPK": "Kategori IPK",
            "Dream Job Utama": "Minat Karier Utama", "Final Distance": "Final Distance",
            "Total Score": "Total M1–M9", "Skor Kualitas (0-100)": "Rata-rata Kompetensi (0–100)",
        }
    else:
        columns = [
            "Ranking", "Candidate_ID", "Program Studi", "Perguruan Tinggi", "IPK",
            "Dream Job Utama", "WSM Score", "Profile Fit Score", "Competency Fit Score",
        ]
        rename = {
            "Ranking": "Peringkat", "Candidate_ID": "ID Kandidat", "IPK": "Kategori IPK",
            "Dream Job Utama": "Minat Karier Utama", "WSM Score": "Skor WSM (0–100)",
            "Profile Fit Score": "Kesesuaian Profil", "Competency Fit Score": "Kesesuaian Kompetensi",
        }
    available = [column for column in columns if column in table.columns]
    table = table[available].rename(columns=rename)
    number_formats = {}
    if method == "knn":
        number_formats = {
            "Final Distance": st.column_config.NumberColumn(format="%.4f"),
            "Rata-rata Kompetensi (0–100)": st.column_config.NumberColumn(format="%.2f"),
        }
    else:
        for col in ["Skor WSM (0–100)", "Kesesuaian Profil", "Kesesuaian Kompetensi"]:
            number_formats[col] = st.column_config.NumberColumn(format="%.1f")
    return table


def _show_candidate_details(recommendations: pd.DataFrame, context: dict, namespace: str) -> None:
    st.markdown("#### Detail kandidat")
    shortlist = st.session_state.setdefault("shortlist", {})
    for _, row in recommendations.iterrows():
        candidate_id = str(row["Candidate_ID"])
        title_text = f"{int(row.get('Ranking', row.get('WSM Rank', 0))):02d}  {candidate_id}  ·  {row.get('Program Studi', 'Program studi tidak dicantumkan')}"
        with st.expander(
            title_text, expanded=False, key=f"candidate_detail_{namespace}_{candidate_id}"
        ):
            col_a, col_m, col_b = st.columns([1.2, 1, 0.9])
            with col_a:
                st.markdown(f"<div class='candidate-id'>{html.escape(candidate_id)}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='candidate-name'>{html.escape(str(row.get('Dream Job Utama', 'Minat karier tidak dicantumkan')))}</div>", unsafe_allow_html=True)
                st.write(f"**Perguruan Tinggi:** {row.get('Perguruan Tinggi', '–')}")
                st.write(f"**Program Studi:** {row.get('Program Studi', '–')}")
                st.write(f"**Kategori IPK:** {_display_ipk(row.get('IPK'))}")
                internship = row.get("Tempat Magang")
                st.write(f"**Tempat Magang:** {internship if pd.notna(internship) and str(internship).strip() else 'Tidak tercatat'}")
                st.write(f"**Dream Job:** {row.get('Dream Job') if pd.notna(row.get('Dream Job')) else 'Tidak tercatat'}")
            with col_m:
                _axes = [{"code": f"M{i}", "max": GUIDE_BY_CODE.get(f"M{i}", {}).get("max", 10)} for i in range(1, 10)]
                _cand = {}
                for _code in [f"M{i}" for i in range(1, 10)]:
                    _col = next((c for c in row.index if c.startswith(f"Skor {_code} (")), None)
                    if _col and pd.notna(row[_col]):
                        _cand[_code] = float(row[_col])
                _tgt = {k: float(v) for k, v in context.get("selected_competencies", {}).items()}
                st.markdown(radar_svg(_axes, [{"cls": "tgt", "values": _tgt}, {"cls": "cand", "values": _cand}], size=300), unsafe_allow_html=True)
                st.caption("Garis putus-putus: target posisi. Area kuning: skor kandidat.")
            with col_b:
                if pd.notna(row.get("Final Distance")):
                    st.metric("Final Distance", f"{float(row['Final Distance']):.4f}")
                if pd.notna(row.get("WSM Score")):
                    st.metric("Skor WSM relatif", f"{float(row['WSM Score']):.1f}/100")
                st.metric("Total M1–M9", f"{row.get('Total Score', 0):g}")
                quality = row.get("Skor Kualitas (0-100)")
                if pd.notna(quality):
                    st.metric("Rata-rata Kompetensi", f"{float(quality):.2f}/100")
                checked = candidate_id in shortlist
                if st.button(
                    "Hapus dari shortlist" if checked else "Tambahkan ke shortlist",
                    key=f"shortlist_btn_{namespace}_{candidate_id}",
                    type="secondary" if checked else "primary",
                    use_container_width=True,
                ):
                    if checked:
                        shortlist.pop(candidate_id, None)
                    else:
                        shortlist[candidate_id] = row.to_dict()
                    st.rerun()
            st.markdown("**Bidang Minat**")
            st.write(row.get("Bidang Minat", "–"))
            st.markdown("**Work Values**")
            st.write(row.get("Work Values", "–"))
            competency_values = []
            targets = context.get("selected_competencies", {})
            for code in [f"M{i}" for i in range(1, 10)]:
                column = next((c for c in row.index if c.startswith(f"Skor {code} (")), None)
                if column:
                    guide = GUIDE_BY_CODE.get(code, {})
                    competency_values.append({
                        "Kode": code,
                        "Dimensi": guide.get("name", column),
                        "Skor Kandidat": row[column],
                        "Target Posisi": f"{float(targets[code]):g}" if code in targets else "Tidak dipilih",
                    })
            if competency_values:
                st.markdown("**Skor kompetensi M1–M9**")
                st.dataframe(pd.DataFrame(competency_values), hide_index=True, use_container_width=True)


def _render_knn(result, context: dict) -> None:
    st.markdown("#### Weighted KNN — metode utama")
    st.caption("Model mengurutkan kandidat menggunakan weighted Euclidean distance. Jarak lebih kecil berarti lebih dekat dengan kriteria yang dimasukkan.")
    st.dataframe(
        _candidate_table(result.recommendations, "knn"),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Peringkat": st.column_config.NumberColumn(width="small"),
            "ID Kandidat": st.column_config.TextColumn(width="small"),
            "Final Distance": st.column_config.NumberColumn(format="%.4f"),
        },
    )
    st.caption("Final Distance bukan persentase kecocokan. Total M1–M9 dan Rata-rata Kompetensi hanya informasi asesmen, bukan fitur ranking KNN.")
    _show_candidate_details(result.recommendations, context, namespace="knn")


def _render_wsm(result) -> None:
    st.markdown("#### Weighted Scoring Model — metode pembanding")
    st.write(
        "WSM mengubah jarak profil dan jarak kompetensi yang sudah dinormalisasi menjadi skor kesesuaian relatif, "
        "kemudian menggabungkannya secara linear menggunakan bobot 70:30. Berbeda dari KNN yang menggabungkan "
        "dua komponen dengan jarak Euclidean."
    )
    st.latex(r"WSM = 0.70 \times ProfileFit + 0.30 \times CompetencyFit")
    st.dataframe(
        _candidate_table(result.wsm_recommendations, "wsm"),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Peringkat": st.column_config.NumberColumn(width="small"),
            "ID Kandidat": st.column_config.TextColumn(width="small"),
            "Skor WSM (0–100)": st.column_config.NumberColumn(format="%.2f"),
            "Kesesuaian Profil": st.column_config.NumberColumn(format="%.2f"),
            "Kesesuaian Kompetensi": st.column_config.NumberColumn(format="%.2f"),
        },
    )
    st.warning(
        "Skor WSM 0–100 adalah skor relatif terhadap kandidat yang lolos filter pada pencarian ini. "
        "Skor tersebut bukan probabilitas diterima dan tidak boleh dibandingkan langsung antar-posisi/pencarian."
    )
    _show_candidate_details(
        result.wsm_recommendations, st.session_state.get("search_context", {}), namespace="wsm"
    )


def _render_comparison(result) -> None:
    comparison = result.comparison.copy()
    knn_top = set(result.recommendations["Candidate_ID"].astype(str))
    wsm_top = set(result.wsm_recommendations["Candidate_ID"].astype(str))
    overlap = len(knn_top & wsm_top)
    corr = comparison[["KNN Rank", "WSM Rank"]].corr(method="spearman").iloc[0, 1]

    a, b, c = st.columns(3)
    a.metric("Kandidat sama di Top 10", f"{overlap}/10")
    b.metric("Kandidat lolos filter", f"{result.eligible_candidates:,}")
    c.metric("Korelasi ranking", f"{corr:.3f}" if pd.notna(corr) else "Tidak tersedia")

    st.caption("Korelasi Spearman mengukur kesamaan urutan ranking KNN dan WSM di seluruh kandidat yang lolos filter. Ini adalah ukuran kesepakatan antarmetode, bukan akurasi rekrutmen.")
    union_ids = knn_top | wsm_top
    union = comparison[comparison["Candidate_ID"].astype(str).isin(union_ids)].copy()
    union = union.sort_values("KNN Rank")
    show = union[[
        "Candidate_ID", "KNN Rank", "WSM Rank", "Final Distance", "WSM Score",
        "Profile Fit Score", "Competency Fit Score",
    ]].rename(columns={
        "Candidate_ID": "ID Kandidat", "KNN Rank": "Peringkat KNN", "WSM Rank": "Peringkat WSM",
        "WSM Score": "Skor WSM", "Profile Fit Score": "Kesesuaian Profil",
        "Competency Fit Score": "Kesesuaian Kompetensi",
    })
    st.dataframe(
        show,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Final Distance": st.column_config.NumberColumn(format="%.4f"),
            "Skor WSM": st.column_config.NumberColumn(format="%.2f"),
            "Kesesuaian Profil": st.column_config.NumberColumn(format="%.2f"),
            "Kesesuaian Kompetensi": st.column_config.NumberColumn(format="%.2f"),
        },
    )
    st.info("Gunakan tab ini untuk melihat apakah dua metode memberikan daftar dan urutan kandidat yang serupa. Perbedaan ranking dapat muncul karena KNN menggunakan agregasi Euclidean, sedangkan WSM menggunakan agregasi linear.")


def _get_secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = default
    return str(value or os.getenv(name, default) or "")


def _render_ai_hr(result, context: dict, matcher) -> None:
    st.markdown("#### Evaluasi kandidat")
    st.write(
        "Gunakan evaluasi ini sebagai pembanding terstruktur untuk meninjau kandidat. "
        "Saat tombol dijalankan, aplikasi menggunakan Generative AI jika persetujuan dan API tersedia. "
        "Jika tidak, sistem tetap menyediakan evaluasi berbasis rubrik internal."
    )

    st.info(
        "AI memberikan penjelasan tambahan berdasarkan data yang tersedia. Jika AI tidak digunakan "
        "atau sedang gagal diakses, aplikasi memakai rubrik internal: 30 poin profil, 50 poin "
        "kompetensi, dan 20 poin relevansi karier/minat. Keduanya bukan keputusan otomatis HR."
    )
    with st.expander("Lihat dasar perhitungan evaluasi", expanded=False):
        st.markdown(
            "- **Profil (maks. 30 poin):** skor kesesuaian profil dari hasil pencocokan, "
            "yang dinormalisasi relatif terhadap kandidat yang lolos filter.\n"
            "- **Kompetensi (maks. 50 poin):** rata-rata pencapaian kandidat terhadap target "
            "M1–M9 yang dipilih perusahaan.\n"
            "- **Relevansi karier (maks. 20 poin):** kemiripan informasi Dream Job, Bidang Minat, "
            "dan Work Values dengan kebutuhan posisi yang diisi."
        )
        st.caption(
            "Karena komponen profil dinormalisasi dalam kumpulan pencarian, skor evaluasi "
            "bersifat relatif untuk pencarian tersebut. Jangan membandingkannya sebagai "
            "probabilitas diterima atau sebagai nilai absolut antarposisi."
        )

    knn_top_ids = result.recommendations["Candidate_ID"].astype(str).tolist()
    wsm_top_ids = result.wsm_recommendations["Candidate_ID"].astype(str).tolist()
    selected_ids = list(dict.fromkeys(knn_top_ids + wsm_top_ids))[:20]
    candidates_frame = result.comparison[
        result.comparison["Candidate_ID"].astype(str).isin(selected_ids)
    ].copy()
    candidates_frame = candidates_frame.set_index("Candidate_ID").loc[selected_ids].reset_index()
    st.caption(
        f"Sampel evaluasi: {len(candidates_frame)} kandidat unik dari gabungan "
        "Top 10 Weighted KNN dan Top 10 Weighted Scoring."
    )

    selected_competencies = context.get("selected_competencies", {})
    position_context = {
        "position_title": context.get("position_title"),
        "requirements": {
            key: value for key, value in context.get("requirement", {}).items()
            if value is not None and key not in {
                "IPK Minimum", "Perguruan Tinggi", "Tempat Magang", "Pengalaman VINIX7"
            }
        },
        "selected_competency_targets": selected_competencies,
    }
    candidate_payload = build_candidate_payload(
        candidates_frame,
        selected_competencies,
        matcher.competency_mapping,
        matcher.competency_scale_max,
    )
    signature_source = json.dumps(
        {"position": position_context, "candidates": candidate_payload},
        ensure_ascii=False, sort_keys=True, default=str,
    )
    evaluation_signature = hashlib.sha256(signature_source.encode("utf-8")).hexdigest()

    groq_key = _get_secret("GROQ_API_KEY")
    gemini_key = _get_secret("GEMINI_API_KEY")
    fallback_enabled = str(_get_secret("ENABLE_GEMINI_FALLBACK", "true")).lower() in {"1", "true", "yes", "on"}
    os.environ["GEMINI_API_KEY"] = gemini_key
    os.environ["GROQ_MODEL"] = _get_secret("GROQ_MODEL", "openai/gpt-oss-20b")
    os.environ["GEMINI_MODEL"] = _get_secret("GEMINI_MODEL", "gemini-2.5-flash")
    os.environ["ENABLE_GEMINI_FALLBACK"] = "true" if fallback_enabled else "false"
    ai_available = bool(groq_key or (fallback_enabled and gemini_key))

    st.caption(
        "Evaluasi Generative AI menggunakan Groq sebagai layanan utama dan Gemini sebagai cadangan. "
        "Jika layanan AI tidak tersedia, evaluasi rubrik internal tetap dapat digunakan."
    )
    external_consent = st.checkbox(
        "Saya menyetujui pengiriman ringkasan data kandidat yang telah diminimalkan ke layanan AI eksternal.",
        key="ai_hr_external_consent",
        disabled=not ai_available,
    )
    if not ai_available:
        st.info(
            "Generative AI belum aktif. Administrator perlu mengatur GROQ_API_KEY "
            "dan, bila diperlukan, GEMINI_API_KEY pada Secrets aplikasi."
        )

    if st.button(
        "Jalankan evaluasi kandidat",
        type="primary",
        key="run_internal_hr_eval",
        use_container_width=True,
    ):
        try:
            if ai_available and external_consent:
                with st.spinner("Generative AI sedang mengevaluasi kandidat..."):
                    evaluation = evaluate_candidates(groq_key, position_context, candidate_payload)
                evaluation["Evaluation Method"] = "Generative AI"
                provider = str(evaluation["AI Provider"].iloc[0]) if "AI Provider" in evaluation else "AI"
                st.session_state.ai_assessment_source = f"Generative AI ({provider})"
                st.success(f"Evaluasi Generative AI berhasil dijalankan menggunakan {provider}.")
            else:
                with st.spinner("Menghitung evaluasi menggunakan rubrik internal..."):
                    evaluation = evaluate_with_internal_rubric(
                        candidates_frame,
                        position_context,
                        selected_competencies,
                        matcher.competency_mapping,
                        matcher.competency_scale_max,
                    )
                st.session_state.ai_assessment_source = "Rubrik internal (non-generatif)"
                if ai_available and not external_consent:
                    st.info("Persetujuan AI eksternal belum diberikan. Hasil dihitung menggunakan rubrik internal.")
                else:
                    st.success("Evaluasi rubrik internal berhasil dihitung.")
            st.session_state.ai_assessment = evaluation
            st.session_state.ai_assessment_signature = evaluation_signature
            st.session_state.ai_external_error = None
        except Exception:
            st.session_state.ai_external_error = (
                "Generative AI belum berhasil menyelesaikan evaluasi. Periksa API key, kuota, "
                "atau koneksi. Evaluasi rubrik internal tetap tersedia."
            )
            st.warning(st.session_state.ai_external_error)
            # Keep a dependable local result available if external AI fails.
            evaluation = evaluate_with_internal_rubric(
                candidates_frame, position_context, selected_competencies,
                matcher.competency_mapping, matcher.competency_scale_max,
            )
            st.session_state.ai_assessment = evaluation
            st.session_state.ai_assessment_signature = evaluation_signature
            st.session_state.ai_assessment_source = "Rubrik internal (fallback)"

    ai_results = st.session_state.get("ai_assessment")
    saved_signature = st.session_state.get("ai_assessment_signature")
    source = st.session_state.get("ai_assessment_source", "Rubrik internal (non-generatif)")
    if (
        isinstance(ai_results, pd.DataFrame)
        and not ai_results.empty
        and saved_signature == evaluation_signature
    ):
        st.divider()
        st.markdown("#### Hasil evaluasi")
        st.caption(f"Sumber penilaian: {source}")
        comparison = result.comparison[["Candidate_ID", "KNN Rank", "WSM Rank"]].copy()
        merged = ai_results.merge(comparison, on="Candidate_ID", how="left")
        rank_corr = merged[["AI HR Rank", "KNN Rank"]].corr(method="spearman").iloc[0, 1]
        x, y = st.columns(2)
        x.metric("Korelasi ranking evaluator–KNN", f"{rank_corr:.3f}" if pd.notna(rank_corr) else "Tidak tersedia")
        y.metric("Kandidat yang dievaluasi", f"{len(ai_results)}")
        st.dataframe(
            merged[["AI HR Rank", "Candidate_ID", "AI HR Score", "KNN Rank", "WSM Rank"]].rename(columns={
                "AI HR Rank": "Peringkat evaluasi", "Candidate_ID": "ID Kandidat", "AI HR Score": "Skor evaluasi",
                "KNN Rank": "Peringkat KNN", "WSM Rank": "Peringkat WSM",
            }),
            hide_index=True,
            use_container_width=True,
            column_config={"Skor evaluasi": st.column_config.NumberColumn(format="%.1f")},
        )
        st.markdown("#### Penjelasan hasil evaluasi")
        st.caption("Buka setiap kandidat untuk melihat alasan penilaian, kelebihan, dan hal yang masih perlu diperiksa.")
        for _, row in merged.iterrows():
            with st.expander(
                f"{int(row['AI HR Rank']):02d} · {row['Candidate_ID']} · Skor {row['AI HR Score']:.1f}",
                key=f"evaluation_detail_{row['Candidate_ID']}",
            ):
                if all(col in row.index for col in ["Profile Points (30)", "Competency Points (50)", "Career Relevance Points (20)"]):
                    p1, p2, p3 = st.columns(3)
                    p1.metric("Profil", f"{row['Profile Points (30)']:.1f}/30")
                    p2.metric("Kompetensi", f"{row['Competency Points (50)']:.1f}/50")
                    p3.metric("Karier/minat", f"{row['Career Relevance Points (20)']:.1f}/20")
                st.markdown("**Mengapa kandidat mendapat nilai ini?**")
                st.write(str(row.get("AI HR Rationale", "Belum ada penjelasan.")))
                st.markdown("**Kelebihan kandidat**")
                strengths = str(row.get("Strengths", "")).strip()
                st.write(strengths if strengths and strengths.lower() != "nan" else "Belum ada kelebihan yang dapat disimpulkan dari data.")
                st.markdown("**Hal yang perlu diperiksa HR**")
                gaps = str(row.get("Gaps / Missing Information", "")).strip()
                st.write(gaps if gaps and gaps.lower() != "nan" else "Tidak ada informasi tambahan yang disebutkan AI.")
        st.download_button(
            "Unduh hasil evaluasi (CSV)",
            data=ai_results.to_csv(index=False).encode("utf-8-sig"),
            file_name="vinix7_candidate_evaluation.csv",
            mime="text/csv",
            key="download_candidate_evaluation",
        )
        st.caption(
            "Skor merupakan alat bantu peninjauan. Bukan probabilitas diterima, label kebenaran HR, "
            "atau dasar tunggal keputusan rekrutmen. Periksa bukti dan lakukan penilaian manusia."
        )
    else:
        st.info("Belum ada hasil untuk pencarian ini. Klik **Jalankan evaluasi kandidat** untuk menampilkan penilaian langsung.")


def render(matcher) -> None:
    result = st.session_state.get("match_result")
    context = st.session_state.get("search_context", {})
    if result is None:
        st.info("Belum ada hasil pencarian. Buat pencarian untuk melihat rekomendasi kandidat.")
        if st.button("Buka pencarian kandidat", type="primary"):
            st.session_state.page = "Cari Kandidat"
            st.rerun()
        return

    title = context.get("position_title") or "Posisi yang dicari"
    company = context.get("company_name")
    page_header(
        "HASIL & PERBANDINGAN",
        f"Kandidat untuk {title}",
        f"{company + ' · ' if company else ''}Hasil KNN, Weighted Scoring, dan evaluasi AI sebagai metode pembanding.",
    )

    a, b, c = st.columns(3)
    a.metric("Profil dalam model", f"{result.total_candidates:,}")
    b.metric("Lolos hard filter", f"{result.eligible_candidates:,}")
    c.metric("Kandidat pada Top 10", f"{len(result.recommendations):,}")

    requirement = context.get("requirement", {})
    targets = context.get("selected_competencies", {})
    with st.expander("Kriteria posisi yang digunakan", expanded=False):
        visible = {key: ("Tidak ditentukan" if value is None else value) for key, value in requirement.items()}
        st.json(visible, expanded=False)
        if targets:
            target_rows = []
            for code, score in targets.items():
                guide = GUIDE_BY_CODE.get(code, {})
                target_rows.append({
                    "Kompetensi": f"{code} — {guide.get('name', '')}",
                    "Target Posisi": score,
                    "Skala": f"0–{matcher.competency_scale_max[matcher.competency_mapping[code]]}",
                })
            st.dataframe(pd.DataFrame(target_rows), hide_index=True, use_container_width=True)

    st.markdown(
        "<div class='method-head'><div>"
        "<div class='mh-eyebrow'>Analisis kandidat</div>"
        "<h3>Metode penilaian dan evaluasi</h3>"
        "<p>Pilih tab untuk melihat ranking, membandingkan metode, atau menjalankan evaluasi kandidat.</p>"
        "</div><span class='mh-hint'>Klik tab untuk berpindah metode</span></div>",
        unsafe_allow_html=True,
    )
    tab_knn, tab_wsm, tab_compare, tab_ai = st.tabs([
        "01  Weighted KNN", "02  Weighted Scoring", "03  Perbandingan", "04  Evaluasi Kandidat",
    ])
    with tab_knn:
        _render_knn(result, context)
    with tab_wsm:
        _render_wsm(result)
    with tab_compare:
        _render_comparison(result)
    with tab_ai:
        _render_ai_hr(result, context, matcher)

    st.download_button(
        "Unduh hasil perbandingan seluruh kandidat (CSV)",
        data=result.comparison.to_csv(index=False).encode("utf-8-sig"),
        file_name="vinix7_knn_wsm_comparison.csv",
        mime="text/csv",
        type="primary",
    )
    st.caption("Ketiga pendekatan merupakan alat bantu eksplorasi. Belum tersedia label relevansi atau outcome rekrutmen historis; keputusan akhir tetap berada pada HR/perusahaan.")
