"""Verifikasi hard filter perguruan tinggi dan hasil di bawah 10 kandidat."""
from pathlib import Path
import joblib
import pandas as pd

from model.matcher import TalentMatcher

ROOT = Path(__file__).resolve().parent
bundle = joblib.load(ROOT / "model" / "talentmatch_model_bundle.joblib")
matcher = TalentMatcher(bundle)

campus_counts = matcher.profile["Perguruan Tinggi"].dropna().astype(str).value_counts()
single_campus = campus_counts[campus_counts == 1]
small_campus = campus_counts[(campus_counts >= 2) & (campus_counts < 10)]
assert not single_campus.empty, "Dataset tidak memiliki kampus dengan satu kandidat untuk pengujian."
assert not small_campus.empty, "Dataset tidak memiliki kampus dengan 2–9 kandidat untuk pengujian."

competency_options = matcher.competency_options()
selected_competencies = {
    item["code"]: round(item["max"] * 0.7, 2)
    for item in competency_options[:2]
}

base_requirement = {
    "Program Studi": None,
    "IPK Minimum": None,
    "Perguruan Tinggi": None,
    "Tempat Magang": None,
    "Pengalaman VINIX7": None,
    "Dream Job": "Data Analyst",
    "Bidang Minat": None,
    "Work Values": None,
    "Motivasi": None,
    "Cognitive Style": None,
    "Ukuran Perusahaan": None,
    "Kultur Kerja": None,
    "Preferensi Lokasi": None,
    "Level Bahasa Inggris": None,
}

# One candidate: the result should still be ranked and displayed.
one_campus = str(single_campus.index[0])
one_result = matcher.recommend(
    {**base_requirement, "Perguruan Tinggi": one_campus}, selected_competencies
)
assert one_result.eligible_candidates == 1
assert len(one_result.recommendations) == 1
assert len(one_result.wsm_recommendations) == 1
assert one_result.recommendations.iloc[0]["Perguruan Tinggi"] == one_campus
assert one_result.wsm_recommendations.iloc[0]["Perguruan Tinggi"] == one_campus
assert "Perguruan Tinggi" not in one_result.active_profile_groups
assert "Exact Match" not in one_result.active_profile_groups

# Between 2 and 9 candidates: display every eligible candidate, not a forced Top 10.
small_campus_name = str(small_campus.index[0])
expected_count = int(small_campus.iloc[0])
small_result = matcher.recommend(
    {**base_requirement, "Perguruan Tinggi": small_campus_name}, selected_competencies
)
assert small_result.eligible_candidates == expected_count
assert len(small_result.recommendations) == expected_count
assert len(small_result.wsm_recommendations) == expected_count
assert small_result.recommendations["Perguruan Tinggi"].eq(small_campus_name).all()
assert small_result.wsm_recommendations["Perguruan Tinggi"].eq(small_campus_name).all()

# An unavailable campus should return a clear no-candidate error.
try:
    matcher.recommend(
        {**base_requirement, "Perguruan Tinggi": "Kampus Uji yang Tidak Ada"},
        selected_competencies,
    )
except ValueError as exc:
    assert "Tidak ada kandidat" in str(exc)
else:
    raise AssertionError("Kampus yang tidak tersedia seharusnya menghasilkan pesan tanpa kandidat.")

print("CAMPUS FILTER TEST: PASSED")
print(f"Single-candidate campus : {one_campus} (1 candidate shown)")
print(f"Small campus cohort     : {small_campus_name} ({expected_count} candidates shown)")
print("Unavailable campus      : clear validation message")
