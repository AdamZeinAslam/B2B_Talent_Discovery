"""Generative-AI second opinion using Groq, with optional Gemini fallback.

Only minimized, pseudonymous candidate data is sent after explicit consent.
AI output supports HR review and must not make hiring decisions.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

import pandas as pd
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = """Anda adalah asisten evaluator HR. Berikan analisis yang mudah dipahami,
singkat, netral, dan hanya berdasarkan data yang tersedia. Jangan menebak informasi.
Jangan menyimpulkan atribut sensitif. Jangan memberi rekomendasi diterima/ditolak.
Gunakan rubrik yang sama untuk semua kandidat:
- Kesesuaian profil dengan posisi: 0-30 poin.
- Kesesuaian target kompetensi: 0-50 poin.
- Relevansi arah karier/minat: 0-20 poin.
Total skor 0-100 adalah skor evaluasi berbasis rubrik, bukan peluang diterima.
Tuliskan alasan dengan bahasa Indonesia sederhana. Jika data tidak tersedia,
katakan 'Belum ada informasi'. Hindari jargon dan kalimat yang tidak relevan.
Kembalikan JSON valid:
{"assessments":[{"candidate_id":"...","score":0,"rationale":"...",
"strengths":["..."],"gaps_or_missing_information":["..."]}]}
Satu penilaian untuk setiap candidate_id.
"""


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def build_candidate_payload(candidate_rows: pd.DataFrame, selected_competencies: dict[str, float],
                            competency_mapping: dict[str, str],
                            competency_scale_max: dict[str, int]) -> list[dict[str, Any]]:
    payload = []
    for _, row in candidate_rows.iterrows():
        candidate_id = str(row.get("Candidate_ID", "")).strip()
        competencies = {}
        for code, target in selected_competencies.items():
            column = competency_mapping[code]
            competencies[code] = {
                "candidate_score": _json_safe(row.get(column)),
                "maximum_score": int(competency_scale_max[column]),
                "position_target": float(target),
            }
        internship_raw = row.get("Tempat Magang")
        if internship_raw is None or pd.isna(internship_raw) or not str(internship_raw).strip():
            internship_status = "Tidak diketahui / tidak tercatat"
        elif re.search(r"vinix\s*(?:7|seven)", str(internship_raw), flags=re.IGNORECASE):
            internship_status = "Tercatat pernah magang di VINIX7"
        else:
            internship_status = "Terdapat catatan magang di tempat lain; bukan VINIX7"
        payload.append({
            "candidate_id": candidate_id,
            "program_study": _json_safe(row.get("Program Studi")),
            "primary_career_interest": _json_safe(row.get("Dream Job Utama")),
            "career_interests": _json_safe(row.get("Bidang Minat")),
            "work_values": _json_safe(row.get("Work Values")),
            "dream_job_text": _json_safe(row.get("Dream Job")),
            "vinix7_internship_status": internship_status,
            "selected_competencies": competencies,
        })
    return payload


def _extract_json(content: str) -> dict[str, Any]:
    text = (content or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("Respons AI tidak memiliki format yang valid.")
        parsed = json.loads(text[start:end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Format hasil evaluasi tidak sesuai.")
    return parsed


def _request_groq(api_key: str, model: str, messages: list[dict]) -> str:
    response = requests.post(
        GROQ_API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "temperature": 0.2, "max_tokens": 6500,
              "response_format": {"type": "json_object"}, "messages": messages},
        timeout=(15, 150),
    )
    if not response.ok:
        raise RuntimeError(f"Groq tidak tersedia (HTTP {response.status_code}).")
    data = response.json()
    return str(data["choices"][0]["message"]["content"])


def _request_gemini(api_key: str, model: str, messages: list[dict]) -> str:
    # Convert the shared system/user messages to Gemini's REST request format.
    system_text = messages[0]["content"]
    user_text = messages[1]["content"]
    response = requests.post(
        GEMINI_API_URL.format(model=model),
        params={"key": api_key},
        json={
            "systemInstruction": {"parts": [{"text": system_text}]},
            "contents": [{"role": "user", "parts": [{"text": user_text}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
                "maxOutputTokens": 6500,
            },
        },
        timeout=(15, 150),
    )
    if not response.ok:
        raise RuntimeError(f"Gemini tidak tersedia (HTTP {response.status_code}).")
    data = response.json()
    return "".join(part.get("text", "") for part in
                   data["candidates"][0]["content"]["parts"] if isinstance(part, dict))


def evaluate_candidates(api_key: str | None, position_context: dict[str, Any],
                        candidates: list[dict[str, Any]]) -> pd.DataFrame:
    """Try Groq first; use Gemini only when enabled and Groq fails."""
    groq_key = (os.getenv("GROQ_API_KEY") or api_key or "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    fallback_enabled = os.getenv("ENABLE_GEMINI_FALLBACK", "true").lower() in {"1", "true", "yes", "on"}

    if not candidates:
        raise ValueError("Tidak ada kandidat untuk dievaluasi.")
    if not groq_key and not (fallback_enabled and gemini_key):
        raise RuntimeError("Layanan evaluasi AI belum disiapkan oleh administrator.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            "Evaluasi kandidat untuk posisi berikut. Terapkan rubrik yang sama dan keluarkan JSON.\n\n"
            + json.dumps({"position_context": position_context, "candidates": candidates},
                         ensure_ascii=False, default=str)
        )},
    ]
    provider_used = ""
    content = ""
    errors = []
    if groq_key:
        try:
            content = _request_groq(groq_key, groq_model, messages)
            provider_used = "Groq"
        except Exception as exc:
            errors.append(str(exc))
    if not content and fallback_enabled and gemini_key:
        try:
            content = _request_gemini(gemini_key, gemini_model, messages)
            provider_used = "Gemini (cadangan)"
        except Exception as exc:
            errors.append(str(exc))
    if not content:
        raise RuntimeError(
            "Evaluasi AI belum berhasil dijalankan. Periksa konfigurasi API atau coba kembali. "
            "Evaluasi rubrik internal tetap tersedia."
        )

    parsed = _extract_json(content)
    assessments = parsed.get("assessments")
    if not isinstance(assessments, list):
        raise ValueError("Hasil evaluasi AI belum mengikuti format yang diharapkan.")
    expected_ids = {str(item["candidate_id"]) for item in candidates}
    rows, seen = [], set()
    for item in assessments:
        if not isinstance(item, dict):
            continue
        cid = str(item.get("candidate_id", "")).strip()
        if cid not in expected_ids or cid in seen:
            continue
        try:
            score = float(item.get("score"))
        except (TypeError, ValueError):
            continue
        if not 0 <= score <= 100:
            continue
        seen.add(cid)
        strengths = item.get("strengths") or []
        gaps = item.get("gaps_or_missing_information") or []
        rows.append({
            "Candidate_ID": cid, "AI HR Score": score,
            "AI HR Rationale": str(item.get("rationale", "Belum ada penjelasan.")),
            "Strengths": "; ".join(map(str, strengths)) if isinstance(strengths, list) else str(strengths),
            "Gaps / Missing Information": "; ".join(map(str, gaps)) if isinstance(gaps, list) else str(gaps),
            "AI Provider": provider_used,
        })
    if expected_ids - seen:
        raise ValueError("Hasil evaluasi AI belum lengkap. Silakan coba kembali.")
    output = pd.DataFrame(rows).sort_values("AI HR Score", ascending=False, kind="stable").reset_index(drop=True)
    output.insert(0, "AI HR Rank", range(1, len(output) + 1))
    return output
