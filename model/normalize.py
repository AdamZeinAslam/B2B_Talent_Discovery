"""Pembersihan label teks bebas (Program Studi, Perguruan Tinggi, Tempat Magang).

Aturan deterministik + pengelompokan typo (difflib). Semua penggabungan bisa diaudit lewat
`audit_table()` dan diedit lewat ALIAS_* di bawah. Penggabungan semantik (mis. 'Informatika' =
'Teknik Informatika') adalah keputusan domain: periksa tabel audit sebelum dipakai produksi.
"""
from __future__ import annotations

import difflib
import re
import unicodedata

import pandas as pd

JUNK = {"isis", "asdf", "test", "tes", "xxx", "aaa", "abc", "tidak ada", "none", "null", "nan", "na", "n/a", "-", "dd", "i"}
GENERIC = {"universitas", "university", "univ", "institut", "of", "the", "dan", "and"}
# kunci kanonik -> kunci varian yang disamakan (keputusan domain, bisa diedit)
ALIAS_PROGRAM = {"informatika": ["teknik informatika", "teknin informatika", "teknologi informatika", "pendidikan informatika"]}
ALIAS_CAMPUS = {"bina nusantara": ["binus", "binus jakarta"]}
ALIASES = {"Program Studi": ALIAS_PROGRAM, "Perguruan Tinggi": ALIAS_CAMPUS, "Tempat Magang": {}}


def _key(text: str, drop_generic: bool) -> str:
    t = unicodedata.normalize("NFKC", str(text)).casefold()
    t = re.sub(r"[^\w\s]", " ", t)
    toks = [w for w in t.split() if not (drop_generic and w in GENERIC)]
    return " ".join(toks)


def acronym_evidence(values: pd.Series) -> frozenset:
    """Akronim 2 karakter yang muncul HURUF BESAR >=2x di kolom yang sama dianggap sah ('ui' = 'UI')."""
    c = values.dropna().astype(str).str.strip().value_counts()
    return frozenset(v.casefold() for v, n in c.items() if n >= 2 and v.isupper() and len(re.sub(r"[^A-Za-z0-9]", "", v)) == 2)


def is_junk(text: str, ok: frozenset = frozenset()) -> bool:
    t = str(text).strip()
    letters = re.sub(r"[^A-Za-z0-9]", "", t)  # 'K3' sah; 'i', 'dd' tidak
    if not t or t.casefold() in JUNK or re.search(r"[^\x00-\u024F\u2010-\u2027]", t):  # aksara non-Latin
        return True
    if len(set(letters.casefold())) <= 1:  # 'aaaa', 'ii'
        return True
    if letters.casefold() in ok:
        return False
    return len(letters) < 2 or (len(letters) == 2 and not letters.isupper())


def build_canonical_map(values: pd.Series, field: str, fuzzy: float = 0.93) -> dict[str, str | None]:
    """raw -> label kanonik (None bila sampah). Label kanonik = varian paling sering dalam klaster."""
    counts = values.dropna().astype(str).str.strip().value_counts()
    ok = acronym_evidence(values)
    drop_generic = field != "Program Studi"
    alias = {v: k for k, vs in ALIASES.get(field, {}).items() for v in vs}
    clusters: dict[str, list[str]] = {}
    for raw in counts.index:
        if is_junk(raw, ok):
            continue
        k = _key(raw, drop_generic)
        clusters.setdefault(alias.get(k, k), []).append(raw)
    keys = sorted(clusters, key=lambda k: -sum(counts[r] for r in clusters[k]))
    merged: dict[str, str] = {}
    for k in keys:  # typo -> klaster yang lebih sering muncul
        target = next((m for m in merged.values() if abs(len(m) - len(k)) <= 2 and len(k) > 6
                       and difflib.SequenceMatcher(None, m, k).ratio() >= fuzzy), None)
        merged[k] = target or k
    final: dict[str, list[str]] = {}
    for k, target in merged.items():
        final.setdefault(target, []).extend(clusters[k])
    out: dict[str, str | None] = {}
    for members in final.values():
        label = max(members, key=lambda r: (counts[r], len(r)))
        out.update({r: label for r in members})
    out.update({r: None for r in counts.index if r not in out})
    return out


def clean_column(series: pd.Series, field: str) -> pd.Series:
    mapping = build_canonical_map(series, field)
    return series.map(lambda v: mapping.get(str(v).strip()) if pd.notna(v) else v)


def audit_table(series: pd.Series, field: str) -> pd.DataFrame:
    m = build_canonical_map(series, field)
    counts = series.dropna().astype(str).str.strip().value_counts()
    return pd.DataFrame({"asli": counts.index, "jumlah": counts.values, "menjadi": [m.get(r) for r in counts.index]}).query("asli != menjadi")


def clean_junk_only(series: pd.Series) -> pd.Series:
    """Untuk teks bebas yang tidak boleh digabung (Dream Job): buang sampah, rapikan spasi."""
    ok = acronym_evidence(series) | {"hr", "ui", "ux", "qa", "qc", "it", "ai", "pm", "bi"}
    return series.map(lambda v: None if pd.isna(v) or is_junk(v, ok) else re.sub(r"\s+", " ", str(v)).strip())
