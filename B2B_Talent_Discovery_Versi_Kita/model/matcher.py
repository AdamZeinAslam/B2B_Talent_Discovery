"""Mesin Weighted KNN untuk B2B Talent Discovery.

Implementasi ini mengikuti transformasi dan formula pada notebook final:
- Hard filter Program Studi, Perguruan Tinggi, dan kategori IPK
- Profile Distance dari fitur multi-hot, one-hot, TF-IDF, numerik, exact match
- Competency Distance dari kompetensi M1-M9 yang dipilih perusahaan
- Final Distance = sqrt(0.70 * profile_norm^2 + 0.30 * competency_norm^2)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


MISSING_VALUES = {"", "tidak diketahui", "tidak diisi", "none", "nan", "-", "all"}
PROGRAM_STUDY_EXCLUDED_OPTIONS = {"ti", "universitas airlangga", "universitas pancasila"}
VINIX7_INTERNSHIP_PATTERN = r"vinix\s*(?:7|seven)"


def norm_key(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    text = str(value).strip().lower()
    text = re.sub(r"[^\w\s/&+.-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def split_tokens(value: Any) -> list[str]:
    """Mendukung input berupa string CSV maupun list pilihan Streamlit."""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        try:
            if pd.isna(value):
                return []
        except (TypeError, ValueError):
            pass
        values = str(value).split(",")
    return [str(item).strip().lower() for item in values if str(item).strip()]


def is_active(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, set)):
        return len(value) > 0
    try:
        if pd.isna(value):
            return False
    except (TypeError, ValueError):
        pass
    return norm_key(value) not in MISSING_VALUES


def minmax01(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return values
    low, high = float(np.min(values)), float(np.max(values))
    if np.isclose(low, high):
        return np.zeros_like(values, dtype=float)
    return (values - low) / (high - low)


@dataclass
class MatchResult:
    recommendations: pd.DataFrame
    wsm_recommendations: pd.DataFrame
    comparison: pd.DataFrame
    total_candidates: int
    eligible_candidates: int
    active_profile_groups: list[str]
    normalized_profile_weights: dict[str, float]
    profile_weight: float
    competency_weight: float
    selected_competencies: dict[str, float]


class TalentMatcher:
    """Membaca bundle final dan menjalankan pencocokan untuk input perusahaan."""

    def __init__(self, bundle: dict[str, Any]):
        self.bundle = bundle
        self.profile = bundle["candidate_profile"].reset_index(drop=True).copy()
        self.model_features = bundle["candidate_model_features"].reset_index(drop=True).copy()
        self.competencies = bundle["candidate_competencies"].reset_index(drop=True).copy()

        if not (len(self.profile) == len(self.model_features) == len(self.competencies)):
            raise ValueError("Jumlah baris kandidat pada model bundle tidak konsisten.")

        from model.normalize import clean_column, clean_junk_only
        for field in ("Program Studi", "Perguruan Tinggi"):  # gabung typo/alias, buang sampah
            cleaned = clean_column(self.profile[field], field)
            self.profile[field] = cleaned
            self.model_features[field] = cleaned.values
        for frame in (self.profile, self.model_features):
            frame["Dream Job"] = clean_junk_only(frame["Dream Job"])

        self.top_k = int(bundle.get("top_k", 10))
        self.profile_weight = float(bundle["profile_weight"])
        self.competency_weight = float(bundle["competency_weight"])
        self.profile_group_weights = bundle["profile_group_weights"]
        self.competency_mapping = bundle["competency_mapping"]
        self.competency_scale_max = bundle["competency_scale_max"]
        self.multi_fields = bundle["multi_fields"]
        self.onehot_fields = bundle["onehot_fields"]
        self.exact_match_fields = bundle["exact_match_fields"]
        self.numeric_fields = bundle["numeric_fields"]
        self.multihot_encoders = bundle["multihot_encoders"]
        self.onehot_encoder = bundle["onehot_encoder"]
        self.tfidf = bundle["tfidf_dream_job"]
        self.numeric_scaler = bundle["numeric_scaler"]
        self.ipk_mapping = {int(k): float(v) for k, v in bundle["ipk_code_to_lower_bound"].items()}

        self._prepare_candidate_matrices()

    def _prepare_candidate_matrices(self) -> None:
        """Rekonstruksi matriks fitur kandidat menggunakan encoder dari bundle."""
        self.multihot_matrices: dict[str, np.ndarray] = {}
        for field in self.multi_fields:
            encoder = self.multihot_encoders[field]
            values = self.model_features[field].map(split_tokens)
            self.multihot_matrices[field] = encoder.transform(values).astype(float)

        onehot_array = self.onehot_encoder.transform(self.model_features[self.onehot_fields])
        self.onehot_columns = list(self.onehot_encoder.get_feature_names_out(self.onehot_fields))
        self.onehot_matrix = pd.DataFrame(onehot_array, columns=self.onehot_columns).astype(float)

        self.dream_job_matrix = self.tfidf.transform(
            self.model_features["Dream Job"].fillna("").astype(str)
        ).toarray().astype(float)

        self.numeric_matrix = self.numeric_scaler.transform(
            self.model_features[self.numeric_fields]
        ).astype(float)

    def available_options(self) -> dict[str, list[str]]:
        """Pilihan form yang bersumber langsung dari kategori model/dataset."""
        def unique_values(field: str) -> list[str]:
            values = self.model_features[field].dropna().astype(str).unique().tolist()
            values = [v for v in values if norm_key(v) not in MISSING_VALUES]
            return sorted(values, key=lambda x: x.casefold())

        options: dict[str, list[str]] = {
            "Program Studi": [v for v in unique_values("Program Studi") if norm_key(v) not in PROGRAM_STUDY_EXCLUDED_OPTIONS],
            "Perguruan Tinggi": unique_values("Perguruan Tinggi"),
            "Tempat Magang": unique_values("Tempat Magang"),
        }
        for field in self.multi_fields:
            options[field] = [str(v) for v in self.multihot_encoders[field].classes_]
        for index, field in enumerate(self.onehot_fields):
            options[field] = [str(v) for v in self.onehot_encoder.categories_[index]
                              if norm_key(v) not in MISSING_VALUES]
        levels = pd.to_numeric(self.model_features["Level Bahasa Inggris"], errors="coerce").dropna()
        options["Level Bahasa Inggris"] = [str(int(v)) for v in sorted(levels.unique())]
        return options

    def competency_options(self) -> list[dict[str, Any]]:
        items = []
        for code, column in self.competency_mapping.items():
            items.append({
                "code": code,
                "column": column,
                "label": column.replace("Skor ", ""),
                "max": int(self.competency_scale_max[column]),
            })
        return items

    def _hard_filter(self, requirement: dict[str, Any]) -> np.ndarray:
        eligible = pd.Series(True, index=self.profile.index)

        program = requirement.get("Program Studi")
        if is_active(program):
            eligible &= self.profile["Program Studi"].map(norm_key).eq(norm_key(program))

        # Optional hard filter: exact university match. A selected campus narrows
        # the candidate pool before KNN/WSM ranking; it is not a soft distance feature.
        campus = requirement.get("Perguruan Tinggi")
        if is_active(campus):
            eligible &= self.profile["Perguruan Tinggi"].map(norm_key).eq(norm_key(campus))

        minimum_ipk = requirement.get("IPK Minimum")
        if minimum_ipk is not None:
            ipk_code = pd.to_numeric(self.profile["IPK"], errors="coerce")
            ipk_lower_bound = ipk_code.map(self.ipk_mapping)
            if ipk_lower_bound.isna().any():
                raise ValueError(
                    "Ada kode IPK pada data yang belum memiliki mapping. "
                    "Periksa IPK_CODE_TO_LOWER_BOUND pada model bundle."
                )
            eligible &= ipk_lower_bound >= float(minimum_ipk)

        # Optional hard filter: recorded internship experience at VINIX7.
        # Missing internship records remain unknown; they are not assumed to mean 'never'.
        vinix_choice = requirement.get("Pengalaman VINIX7")
        if vinix_choice in {"Pernah magang di VINIX7", "Tidak pernah magang di VINIX7"}:
            internship = self.profile["Tempat Magang"].fillna("").astype(str).str.strip()
            has_record = internship.ne("") & ~internship.map(norm_key).isin(MISSING_VALUES)
            at_vinix = internship.str.contains(VINIX7_INTERNSHIP_PATTERN, case=False, regex=True, na=False)
            if vinix_choice == "Pernah magang di VINIX7":
                eligible &= has_record & at_vinix
            else:
                eligible &= has_record & ~at_vinix

        return np.flatnonzero(eligible.to_numpy())

    def _build_profile_vectors(
        self, requirement: dict[str, Any]
    ) -> tuple[np.ndarray, np.ndarray, list[str], dict[str, float]]:
        candidate_blocks: list[tuple[str, np.ndarray]] = []
        company_blocks: list[tuple[str, np.ndarray]] = []
        active_groups: list[str] = []

        # A. Multi-Hot: Bidang Minat dan Work Values.
        for field in self.multi_fields:
            requested = requirement.get(field)
            if not is_active(requested):
                continue
            encoder = self.multihot_encoders[field]
            tokens = split_tokens(requested)
            known_tokens = set(encoder.classes_)
            unknown = [token for token in tokens if token not in known_tokens]
            if unknown:
                raise ValueError(f"Pilihan {field} tidak dikenali: {', '.join(unknown)}")
            candidate_block = self.multihot_matrices[field]
            company_block = encoder.transform([tokens]).astype(float)
            candidate_blocks.append((field, candidate_block))
            company_blocks.append((field, company_block))
            active_groups.append(field)

        # B. One-Hot: hanya kolom dari atribut yang dipilih perusahaan.
        active_onehot = [field for field in self.onehot_fields if is_active(requirement.get(field))]
        if active_onehot:
            query_values = {
                field: str(self.model_features[field].mode().iloc[0])
                for field in self.onehot_fields
            }
            for field in active_onehot:
                requested = norm_key(requirement[field])
                position = self.onehot_fields.index(field)
                known = {norm_key(value) for value in self.onehot_encoder.categories_[position]}
                if requested not in known:
                    raise ValueError(f"Pilihan '{requirement[field]}' tidak tersedia untuk {field}.")
                query_values[field] = requested

            company_onehot_all = self.onehot_encoder.transform(
                pd.DataFrame([query_values], columns=self.onehot_fields)
            )
            selected_columns: list[str] = []
            for field in active_onehot:
                selected_columns.extend(
                    [column for column in self.onehot_columns if column.startswith(field + "_")]
                )
            column_positions = [self.onehot_columns.index(column) for column in selected_columns]
            candidate_block = self.onehot_matrix.iloc[:, column_positions].to_numpy(dtype=float)
            company_block = np.asarray(company_onehot_all, dtype=float)[:, column_positions]
            candidate_blocks.append(("One-Hot", candidate_block))
            company_blocks.append(("One-Hot", company_block))
            active_groups.append("One-Hot")

        # C. TF-IDF: Dream Job.
        if is_active(requirement.get("Dream Job")):
            candidate_blocks.append(("Dream Job", self.dream_job_matrix))
            company_blocks.append((
                "Dream Job",
                self.tfidf.transform([str(requirement["Dream Job"])]).toarray().astype(float),
            ))
            active_groups.append("Dream Job")

        # D. Numerik: Level Bahasa Inggris. IPK hanya dipakai sebagai hard filter.
        if is_active(requirement.get("Level Bahasa Inggris")):
            level = float(requirement["Level Bahasa Inggris"])
            min_level = float(self.model_features["Level Bahasa Inggris"].min())
            max_level = float(self.model_features["Level Bahasa Inggris"].max())
            if not min_level <= level <= max_level:
                raise ValueError(f"Level Bahasa Inggris harus berada pada rentang {min_level:g}–{max_level:g}.")
            candidate_blocks.append(("Numerik", self.numeric_matrix))
            company_blocks.append((
                "Numerik",
                self.numeric_scaler.transform(pd.DataFrame({"Level Bahasa Inggris": [level]})),
            ))
            active_groups.append("Numerik")

        # E. Exact Match: remaining soft exact-match fields (e.g. internship).
        # Perguruan Tinggi is handled exclusively as a hard filter in _hard_filter.
        active_exact = [
            field for field in self.exact_match_fields
            if field != "Perguruan Tinggi" and is_active(requirement.get(field))
        ]
        if active_exact:
            candidate_block = np.column_stack([
                self.model_features[field].map(norm_key).eq(norm_key(requirement[field])).astype(int).to_numpy()
                for field in active_exact
            ]).astype(float)
            company_block = np.ones((1, len(active_exact)), dtype=float)
            candidate_blocks.append(("Exact Match", candidate_block))
            company_blocks.append(("Exact Match", company_block))
            active_groups.append("Exact Match")

        if not active_groups:
            raise ValueError("Isi minimal satu kriteria profil, misalnya jabatan/Dream Job atau bidang minat.")

        total_weight = sum(self.profile_group_weights[group] for group in active_groups)
        normalized_weights = {
            group: self.profile_group_weights[group] / total_weight
            for group in active_groups
        }

        weighted_candidates: list[np.ndarray] = []
        weighted_company: list[np.ndarray] = []
        for (group, candidate_block), (_, company_block) in zip(candidate_blocks, company_blocks):
            factor = np.sqrt(normalized_weights[group] / candidate_block.shape[1])
            weighted_candidates.append(candidate_block * factor)
            weighted_company.append(company_block * factor)

        return np.hstack(weighted_candidates), np.hstack(weighted_company), active_groups, normalized_weights

    def recommend(
        self,
        requirement: dict[str, Any],
        selected_competencies: dict[str, float],
    ) -> MatchResult:
        """Hitung ranking KNN dan Weighted Scoring pada cohort kandidat yang sama.

        KNN memakai agregasi Euclidean (L2). WSM memakai agregasi linear (L1)
        atas skor profil dan kompetensi yang diturunkan dari normalisasi jarak
        pada kumpulan kandidat yang lolos hard filter. Kedua skor bersifat relatif
        terhadap cohort pencarian, bukan probabilitas keberhasilan rekrutmen.
        """
        if not 2 <= len(selected_competencies) <= 9:
            raise ValueError("Pilih minimal 2 dan maksimal 9 kompetensi M1–M9.")

        for code, target in selected_competencies.items():
            if code not in self.competency_mapping:
                raise ValueError(f"Kode kompetensi tidak dikenal: {code}")
            max_score = self.competency_scale_max[self.competency_mapping[code]]
            if not 0 <= float(target) <= max_score:
                raise ValueError(f"Target {code} harus berada pada rentang 0 sampai {max_score}.")

        eligible_positions = self._hard_filter(requirement)
        if len(eligible_positions) == 0:
            applied_filters = [
                f"Perguruan Tinggi: {requirement.get('Perguruan Tinggi')}"
                if is_active(requirement.get("Perguruan Tinggi")) else None,
                f"Program Studi: {requirement.get('Program Studi')}"
                if is_active(requirement.get("Program Studi")) else None,
                f"IPK minimum: {requirement.get('IPK Minimum')}"
                if requirement.get("IPK Minimum") is not None else None,
            ]
            filter_text = "; ".join(item for item in applied_filters if item)
            detail = f" Filter aktif: {filter_text}." if filter_text else ""
            raise ValueError(
                "Tidak ada kandidat yang memenuhi hard filter yang dipilih."
                f"{detail} Coba pilih perguruan tinggi lain atau longgarkan persyaratan."
            )

        profile_candidates, profile_company, active_groups, normalized_group_weights = (
            self._build_profile_vectors(requirement)
        )
        profile_distance = np.linalg.norm(
            profile_candidates[eligible_positions] - profile_company, axis=1
        )
        profile_distance_normalized = minmax01(profile_distance)

        selected_codes = list(selected_competencies.keys())
        selected_columns = [self.competency_mapping[code] for code in selected_codes]
        candidate_competency_normalized = self.competencies[selected_columns].copy()
        for code, column in zip(selected_codes, selected_columns):
            candidate_competency_normalized[column] = (
                candidate_competency_normalized[column] / self.competency_scale_max[column]
            )
        company_competency_normalized = np.array([
            float(selected_competencies[code]) / self.competency_scale_max[self.competency_mapping[code]]
            for code in selected_codes
        ], dtype=float)

        eligible_competencies = candidate_competency_normalized.iloc[eligible_positions].to_numpy(dtype=float)
        competency_distance = np.linalg.norm(
            eligible_competencies - company_competency_normalized.reshape(1, -1), axis=1
        ) / np.sqrt(len(selected_codes))
        competency_distance_normalized = minmax01(competency_distance)

        # KNN: weighted Euclidean distance (L2) pada dua komponen jarak.
        ranking_matrix = np.column_stack([
            profile_distance_normalized * np.sqrt(self.profile_weight),
            competency_distance_normalized * np.sqrt(self.competency_weight),
        ])
        final_distances = np.linalg.norm(ranking_matrix, axis=1)

        # WSM: kombinasi linear skor kesesuaian profil dan kompetensi (L1).
        # Skor 0-100 bersifat relatif terhadap kandidat yang lolos filter.
        profile_fit_scores = (1.0 - profile_distance_normalized) * 100.0
        competency_fit_scores = (1.0 - competency_distance_normalized) * 100.0
        wsm_scores = (
            self.profile_weight * profile_fit_scores
            + self.competency_weight * competency_fit_scores
        )

        base = self.profile.iloc[eligible_positions].copy().reset_index(drop=True)
        base["Profile Distance (Normalized)"] = profile_distance_normalized
        base["Competency Distance (Normalized)"] = competency_distance_normalized
        base["Final Distance"] = final_distances
        base["Profile Fit Score"] = profile_fit_scores
        base["Competency Fit Score"] = competency_fit_scores
        base["WSM Score"] = wsm_scores

        knn_order = np.argsort(final_distances, kind="stable")
        wsm_order = np.argsort(-wsm_scores, kind="stable")
        knn_ranks = np.empty(len(base), dtype=int)
        wsm_ranks = np.empty(len(base), dtype=int)
        knn_ranks[knn_order] = np.arange(1, len(base) + 1)
        wsm_ranks[wsm_order] = np.arange(1, len(base) + 1)
        base["KNN Rank"] = knn_ranks
        base["WSM Rank"] = wsm_ranks

        comparison = base.sort_values("KNN Rank", kind="stable").reset_index(drop=True)
        # Display at most top_k recommendations, but allow fewer than 10 when
        # only a small number of candidates pass the hard filters.
        display_count = min(self.top_k, len(comparison))
        recommendations = comparison.head(display_count).copy()
        recommendations.insert(0, "Ranking", np.arange(1, len(recommendations) + 1))

        wsm_recommendations = (
            base.sort_values("WSM Rank", kind="stable").head(display_count).copy().reset_index(drop=True)
        )
        wsm_recommendations.insert(0, "Ranking", np.arange(1, len(wsm_recommendations) + 1))

        return MatchResult(
            recommendations=recommendations,
            wsm_recommendations=wsm_recommendations,
            comparison=comparison,
            total_candidates=len(self.profile),
            eligible_candidates=len(eligible_positions),
            active_profile_groups=active_groups,
            normalized_profile_weights=normalized_group_weights,
            profile_weight=self.profile_weight,
            competency_weight=self.competency_weight,
            selected_competencies={k: float(v) for k, v in selected_competencies.items()},
        )
