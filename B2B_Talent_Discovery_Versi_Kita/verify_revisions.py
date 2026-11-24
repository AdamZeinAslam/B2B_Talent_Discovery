from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import joblib
import pandas as pd

from model.matcher import TalentMatcher, norm_key
from model.ai_evaluator import evaluate_candidates

BASE = Path(__file__).resolve().parent
bundle = joblib.load(BASE / "model" / "talentmatch_model_bundle.joblib")
matcher = TalentMatcher(bundle)

# Program Study options hide the explicitly requested wrong-column values.
program_options = {norm_key(v) for v in matcher.available_options()["Program Studi"]}
for excluded in ["TI", "Universitas Airlangga", "Universitas Pancasila"]:
    assert norm_key(excluded) not in program_options, f"Still shown: {excluded}"

# The raw model candidate count remains unchanged.
assert len(matcher.profile) == 2988

# VINIX7 internship filter is a distinct filter and unknown rows are not inferred as 'never'.
base_requirement = {"Program Studi": None, "IPK Minimum": None}
all_positions = matcher._hard_filter(base_requirement)
vinix_positions = matcher._hard_filter({**base_requirement, "Pengalaman VINIX7": "Pernah magang di VINIX7"})
not_vinix_positions = matcher._hard_filter({**base_requirement, "Pengalaman VINIX7": "Tidak pernah magang di VINIX7"})
assert len(vinix_positions) > 0
assert len(not_vinix_positions) > 0
assert len(vinix_positions) + len(not_vinix_positions) <= len(all_positions)

# Groq primary and Gemini fallback are tested with local mocks; no external API call.
import os
from unittest.mock import patch
from model.ai_evaluator import evaluate_candidates

fake_content = json.dumps({"assessments": [{
    "candidate_id": "C_TEST", "score": 80, "rationale": "Kompetensi sesuai kebutuhan posisi.",
    "strengths": ["Kompetensi relevan"], "gaps_or_missing_information": ["Pengalaman belum tercatat"]
}]})

class FakeResponse:
    ok = True
    status_code = 200
    def __init__(self, payload): self.payload = payload
    def json(self): return self.payload

groq_response = FakeResponse({"choices": [{"message": {"content": fake_content}}]})
candidate_payload = [{"candidate_id": "C_TEST", "vinix7_internship_status": "Tidak diketahui / tidak tercatat",
                      "selected_competencies": {"M1": {"candidate_score": 7}}}]
with patch.dict(os.environ, {"GROQ_API_KEY": "test-groq", "GEMINI_API_KEY": "test-gemini",
                             "ENABLE_GEMINI_FALLBACK": "true"}):
    with patch("model.ai_evaluator.requests.post", return_value=groq_response) as mock_post:
        ai = evaluate_candidates(None, {"position_title": "Analyst"}, candidate_payload)
        assert len(ai) == 1 and ai.iloc[0]["AI HR Score"] == 80
        assert ai.iloc[0]["AI Provider"] == "Groq"
        assert mock_post.call_args.args[0].startswith("https://api.groq.com/")

    # If Groq fails, Gemini fallback is used.
    gemini_response = FakeResponse({"candidates": [{"content": {"parts": [{"text": fake_content}]}}]})
    with patch("model.ai_evaluator.requests.post", side_effect=[
        RuntimeError("Groq unavailable"), gemini_response
    ]) as mock_post:
        ai = evaluate_candidates(None, {"position_title": "Analyst"}, candidate_payload)
        assert ai.iloc[0]["AI Provider"] == "Gemini (cadangan)"
        assert mock_post.call_count == 2
        assert "generativelanguage.googleapis.com" in mock_post.call_args.args[0]

print("REVISION TEST: PASSED")
print(f"Candidates preserved: {len(matcher.profile):,}")
print(f"Selectable Program Study values: {len(program_options):,}")
print(f"Recorded VINIX7 internship: {len(vinix_positions):,}")
print("Groq primary: mocked request/response passed")
print("Gemini fallback: mocked request/response passed")
print("No live API call was made; real credentials and provider quota still need a live test.")
