"""Deterministic, dependency-free candidate evaluation rubric.

This is NOT generative AI. It creates an always-available, explainable
comparison score so users can evaluate candidates even when an external AI
provider is unavailable. Scores are exploratory and not validated HR labels.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

import numpy as np
import pandas as pd

STOPWORDS = {
    "dan", "atau", "untuk", "dengan", "di", "ke", "dari", "yang", "the",
    "a", "an", "of", "to", "in", "for", "and", "or", "as", "on",
    "posisi", "staff", "intern", "internship", "junior", "senior",
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def _tokens(value: Any) -> set[str]:
    words = re.findall(r"[a-z0-9]+", _text(value).casefold())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def _similarity(target: Any, candidate: Any) -> float | None:
    """Target-term coverage blended with string similarity (0..1)."""
    target_text, candidate_text = _text(target), _text(candidate)
    target_tokens, candidate_tokens = _tokens(target_text), _tokens(candidate_text)
    if not target_tokens or not candidate_tokens:
        return None
    coverage = len(target_tokens & candidate_tokens) / len(target_tokens)
    seq = SequenceMatcher(None, target_text.casefold(), candidate_text.casefold()).ratio()
    return float(np.clip(0.8 * coverage + 0.2 * seq, 0.0, 1.0))


def _multi_similarity(target: Any, candidate: Any) -> float | None:
    target_tokens, candidate_tokens = _tokens(target), _tokens(candidate)
    if not target_tokens or not candidate_tokens:
        return None
    return len(target_tokens & candidate_tokens) / len(target_tokens)


def evaluate_with_internal_rubric(
    comparison: pd.DataFrame,
    position_context: dict[str, Any],
    selected_competencies: dict[str, float],
    competency_mapping: dict[str, str],
    competency_scale_max: dict[str, int],
) -> pd.DataFrame:
    """Score the current eligible candidate pool using a fixed 30/50/20 rubric.

    30 points: normalized profile fit from the matching cohort.
    50 points: attainment of the selected M1-M9 position targets.
    20 points: career/interest/value relevance using explicit string/token match.
    """
    if comparison is None or comparison.empty:
        raise ValueError("Tidak ada kandidat yang dapat dievaluasi.")
    if not selected_competencies:
        raise ValueError("Kompetensi target belum tersedia.")

    requirements = position_context.get("requirements", {}) or {}
    position_title = position_context.get("position_title") or requirements.get("Dream Job", "")
    rows: list[dict[str, Any]] = []

    for _, candidate in comparison.iterrows():
        candidate_id = _text(candidate.get("Candidate_ID"))

        # 1) Profile fit (0-30). The model's fit is min-max normalized within
        # the candidates who passed the current search filters.
        raw_profile_fit = candidate.get("Profile Fit Score")
        if pd.isna(raw_profile_fit):
            distance = pd.to_numeric(candidate.get("Profile Distance (Normalized)"), errors="coerce")
            raw_profile_fit = 100.0 * (1.0 - float(distance)) if pd.notna(distance) else 0.0
        profile_fit = float(np.clip(float(raw_profile_fit), 0.0, 100.0))
        profile_points = 0.30 * profile_fit

        # 2) Selected competency target attainment (0-50).
        attainment_values: list[float] = []
        passed_competencies: list[str] = []
        below_competencies: list[str] = []
        missing_competencies: list[str] = []
        for code, target in selected_competencies.items():
            column = competency_mapping[code]
            maximum = float(competency_scale_max[column])
            actual = pd.to_numeric(candidate.get(column), errors="coerce")
            target_value = float(target)
            if pd.isna(actual):
                missing_competencies.append(code)
                continue
            if target_value > 0:
                attainment = min(float(actual) / target_value, 1.0)
            else:
                attainment = float(actual) / maximum if maximum > 0 else 0.0
            attainment_values.append(float(np.clip(attainment, 0.0, 1.0)))
            if float(actual) >= target_value:
                passed_competencies.append(f"{code} ({float(actual):g}/{target_value:g})")
            else:
                below_competencies.append(f"{code} ({float(actual):g}/{target_value:g})")

        competency_fit = (
            float(np.mean(attainment_values) * 100.0) if attainment_values else 0.0
        )
        competency_points = 0.50 * competency_fit

        # 3) Career relevance (0-20). Only supplied requirements are compared;
        # missing requirement dimensions are omitted and remaining weights
        # are proportionally re-normalized.
        career_dimensions: list[tuple[str, float, float]] = []
        dream_target = requirements.get("Dream Job") or position_title
        dream_candidate = " ".join(filter(None, [
            _text(candidate.get("Dream Job Utama")), _text(candidate.get("Dream Job"))
        ]))
        dream_score = _similarity(dream_target, dream_candidate)
        if dream_score is not None:
            career_dimensions.append(("kesesuaian minat karier", dream_score, 0.60))

        interest_target = requirements.get("Bidang Minat")
        if interest_target:
            interest_score = _multi_similarity(interest_target, candidate.get("Bidang Minat"))
            if interest_score is not None:
                career_dimensions.append(("kesesuaian bidang minat", interest_score, 0.25))

        values_target = requirements.get("Work Values")
        if values_target:
            values_score = _multi_similarity(values_target, candidate.get("Work Values"))
            if values_score is not None:
                career_dimensions.append(("kesesuaian nilai kerja", values_score, 0.15))

        if career_dimensions:
            weight_total = sum(item[2] for item in career_dimensions)
            career_fit = 100.0 * sum(score * weight for _, score, weight in career_dimensions) / weight_total
        else:
            career_fit = 0.0
        career_points = 0.20 * career_fit

        total_score = float(np.clip(profile_points + competency_points + career_points, 0.0, 100.0))
        rationale_parts = [
            f"Kesesuaian profil relatif {profile_fit:.1f}/100 ({profile_points:.1f}/30 poin).",
            f"Pencapaian target kompetensi {competency_fit:.1f}/100 ({competency_points:.1f}/50 poin).",
            f"Relevansi minat/karier {career_fit:.1f}/100 ({career_points:.1f}/20 poin).",
        ]
        if not career_dimensions:
            rationale_parts.append("Kriteria minat karier tidak cukup lengkap untuk dinilai.")
        rationale = " ".join(rationale_parts)

        strengths = []
        if passed_competencies:
            strengths.append("Mencapai target: " + ", ".join(passed_competencies))
        if career_fit >= 70 and career_dimensions:
            strengths.append("Minat karier cukup relevan dengan posisi yang dicari.")
        if profile_fit >= 70:
            strengths.append("Profil relatif dekat dengan kebutuhan posisi pada kumpulan kandidat ini.")

        gaps = []
        if below_competencies:
            gaps.append("Di bawah target: " + ", ".join(below_competencies))
        if missing_competencies:
            gaps.append("Skor tidak tersedia: " + ", ".join(missing_competencies))
        if career_fit < 50:
            gaps.append("Keterkaitan minat karier dengan posisi perlu ditinjau lebih lanjut.")
        if not gaps:
            gaps.append("Tidak ada kesenjangan utama yang terdeteksi oleh rubrik ini; tetap verifikasi melalui asesmen HR.")

        rows.append({
            "Candidate_ID": candidate_id,
            "AI HR Score": round(total_score, 2),
            "AI HR Rationale": rationale,
            "Strengths": "; ".join(strengths),
            "Gaps / Missing Information": "; ".join(gaps),
            "Evaluation Method": "Rubrik internal (non-generatif)",
            "Profile Points (30)": round(profile_points, 2),
            "Competency Points (50)": round(competency_points, 2),
            "Career Relevance Points (20)": round(career_points, 2),
        })

    output = pd.DataFrame(rows).sort_values(
        ["AI HR Score", "Candidate_ID"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    output.insert(0, "AI HR Rank", range(1, len(output) + 1))
    return output
