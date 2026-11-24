from __future__ import annotations

from pathlib import Path
import joblib
import streamlit as st

from components import brand_sidebar, footer, inject_styles
from model.matcher import TalentMatcher
from views import dashboard, guide, results, search, shortlist

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "talentmatch_model_bundle.joblib"


@st.cache_resource(show_spinner="Memuat model VINIX7 Talent Discovery...")
def load_matcher(model_path: str) -> TalentMatcher:
    return TalentMatcher(joblib.load(model_path))


st.set_page_config(
    page_title="VINIX7 | Talent Discovery",
    page_icon=str(BASE_DIR / "assets" / "vinix7_logo_centered.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

if not MODEL_PATH.exists():
    st.error("Model tidak ditemukan. Pastikan file model/talentmatch_model_bundle.joblib tersedia.")
    st.stop()

try:
    matcher = load_matcher(str(MODEL_PATH))
except Exception as exc:
    st.error(f"Model gagal dimuat: {exc}")
    st.info("Jalankan instalasi dependensi dari requirements.txt. Gunakan versi scikit-learn 1.6.1 sesuai model bundle.")
    st.stop()

st.session_state.setdefault("page", "Dashboard")
st.session_state.setdefault("shortlist", {})
st.session_state.setdefault("match_result", None)
st.session_state.setdefault("search_context", {})
st.session_state.setdefault("ai_assessment", None)
st.session_state["competency_mapping"] = matcher.competency_mapping

brand_sidebar()
st.sidebar.markdown("<div class='small-label'>WORKSPACE</div>", unsafe_allow_html=True)
nav_items = [
    ("Overview", "Dashboard"),
    ("Panduan Aplikasi", "Panduan"),
    ("Cari Kandidat", "Cari Kandidat"),
    ("Hasil & Perbandingan", "Hasil Rekomendasi"),
    ("Shortlist", "Shortlist"),
]
for label, page in nav_items:
    disabled = page == "Hasil Rekomendasi" and st.session_state.match_result is None
    current = st.session_state.page == page
    if st.sidebar.button(
        ("●  " if current else "   ") + label,
        key=f"nav_{page}",
        use_container_width=True,
        disabled=disabled,
        type="primary" if current else "secondary",
    ):
        st.session_state.page = page
        st.rerun()

st.sidebar.divider()
st.sidebar.markdown("**METODE AKTIF**")
st.sidebar.caption("Weighted KNN · metode utama")
st.sidebar.caption("Weighted Scoring · metode pembanding")
st.sidebar.caption("Evaluasi kandidat berbasis rubrik")
st.sidebar.divider()
st.sidebar.caption(f"{len(matcher.profile):,} profil kandidat dalam model")
st.sidebar.caption("Prototype · shortlist tersimpan selama sesi aplikasi.")

page = st.session_state.page
if page == "Dashboard":
    dashboard.render(matcher.bundle)
elif page == "Panduan":
    guide.render(matcher)
elif page == "Cari Kandidat":
    search.render(matcher)
elif page == "Hasil Rekomendasi":
    results.render(matcher)
elif page == "Shortlist":
    shortlist.render()
else:
    st.session_state.page = "Dashboard"
    st.rerun()

footer()
