"""Verifikasi Weighted KNN dan Weighted Scoring terhadap bundle terbaru."""
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from model.matcher import TalentMatcher
from model.ai_evaluator import build_candidate_payload
from model.rubric_evaluator import evaluate_with_internal_rubric

ROOT = Path(__file__).resolve().parent
bundle = joblib.load(ROOT / "model" / "talentmatch_model_bundle.joblib")
matcher = TalentMatcher(bundle)
expected = pd.read_csv(ROOT / "reference" / "top10_recommendations_example.csv")
expected_wsm = pd.read_csv(ROOT / "reference" / "wsm_recommendations_example.csv")
result = matcher.recommend(bundle["company_requirement_example"], bundle["selected_competencies_example"])

assert result.total_candidates == len(bundle["candidate_profile"]), result.total_candidates
assert result.eligible_candidates == 305, result.eligible_candidates
assert result.recommendations["Candidate_ID"].astype(str).tolist() == expected["Candidate_ID"].astype(str).tolist()
assert np.allclose(result.recommendations["Final Distance"].to_numpy(), expected["Final Distance"].to_numpy(), atol=1e-10)
assert len(result.wsm_recommendations) == 10
assert result.wsm_recommendations["Candidate_ID"].astype(str).tolist() == expected_wsm["Candidate_ID"].astype(str).tolist()
assert np.allclose(result.wsm_recommendations["WSM Score"].to_numpy(), expected_wsm["WSM Score"].to_numpy(), atol=1e-10)
assert len(result.comparison) == result.eligible_candidates
assert result.comparison["KNN Rank"].is_unique
assert result.comparison["WSM Rank"].is_unique
assert result.comparison["WSM Score"].between(0, 100).all()

union_ids = list(dict.fromkeys(
    result.recommendations["Candidate_ID"].astype(str).tolist()
    + result.wsm_recommendations["Candidate_ID"].astype(str).tolist()
))
sample = result.comparison[result.comparison["Candidate_ID"].astype(str).isin(union_ids)].copy()
payload = build_candidate_payload(
    sample,
    result.selected_competencies,
    matcher.competency_mapping,
    matcher.competency_scale_max,
)
assert len(payload) <= 20
assert len(payload) == len(union_ids)
assert all("Total Score" not in item and "Skor Kualitas (0-100)" not in item and "gpa_category_code" not in item for item in payload)

position_context = {
    "position_title": bundle["company_requirement_example"].get("Dream Job"),
    "requirements": {
        key: value for key, value in bundle["company_requirement_example"].items()
        if value is not None
    },
}
internal_evaluation = evaluate_with_internal_rubric(
    sample,
    position_context,
    result.selected_competencies,
    matcher.competency_mapping,
    matcher.competency_scale_max,
)
assert len(internal_evaluation) == len(union_ids)
assert internal_evaluation["Candidate_ID"].is_unique
assert internal_evaluation["AI HR Score"].between(0, 100).all()
assert internal_evaluation["AI HR Rank"].tolist() == list(range(1, len(union_ids) + 1))
assert internal_evaluation["Evaluation Method"].eq("Rubrik internal (non-generatif)").all()

print("INTEGRATION TEST: PASSED")
print(f"Candidate records  : {result.total_candidates:,}")
print(f"Eligible candidates: {result.eligible_candidates:,}")
print("KNN top 10         : " + ", ".join(result.recommendations["Candidate_ID"].astype(str).tolist()))
print("WSM top 10         : " + ", ".join(result.wsm_recommendations["Candidate_ID"].astype(str).tolist()))
print(f"Top 10 overlap     : {len(set(result.recommendations['Candidate_ID']) & set(result.wsm_recommendations['Candidate_ID']))}/10")
print(f"AI payload sample  : {len(payload)} pseudonymous candidates (external API not called)")
print(f"Internal evaluation: {len(internal_evaluation)} scores generated locally; range {internal_evaluation['AI HR Score'].min():.2f}–{internal_evaluation['AI HR Score'].max():.2f}")
