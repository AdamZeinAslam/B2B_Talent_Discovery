"""Bersihkan data mentah konsultasi karir -> Excel bersih + laporan perubahan yang bisa diaudit.

Pakai:  python scripts/clean_dataset.py Konsultasi_Karir.xlsx hasil/
Aturan ada di model/normalize.py (junk, typo, alias). Tidak ada baris yang dihapus: baris
bermasalah diberi 'Catatan Kualitas' agar keputusan membuang/mempertahankan tetap di tangan manusia.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from openpyxl.styles import Font, PatternFill

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.normalize import clean_column, clean_junk_only  # noqa: E402

FIELDS = ["Program Studi", "Perguruan Tinggi", "Tempat Magang"]


def main(src: str, out_dir: str) -> None:
    df = pd.read_excel(src)
    out = df.drop(columns=[c for c in df if "EMAIL" in c.upper()])  # data pribadi, tidak dipakai model
    notes = pd.Series([[] for _ in range(len(df))], index=df.index)
    log = []
    cleaned = {f: clean_column(df[f], f) for f in FIELDS}
    cleaned["Dream Job"] = clean_junk_only(df["Dream Job"])
    for f, new in cleaned.items():
        raw = df[f].astype("string").str.strip()
        changed = raw.notna() & (raw != new.astype("string")).fillna(True)  # NA = dikosongkan
        for (a, b), n in pd.DataFrame({"a": raw[changed], "b": new[changed]}).fillna("").value_counts().items():
            log.append({"Kolom": f, "Asli": a, "Menjadi": b or "(dikosongkan)", "Jenis": "dibuang" if not b else "digabung/dirapikan", "Jumlah": n})
        for i in df.index[raw.notna() & new.isna()]:
            notes[i].append(f"{f}: tidak valid, dikosongkan")
        out.insert(out.columns.get_loc(f) + 1, f"{f} (asli)", df[f]) if f in FIELDS else None
        out[f] = new
    for i in df.index[df["Perguruan Tinggi"].notna() & cleaned["Perguruan Tinggi"].astype("string").str.fullmatch(r"[A-Z]{2,3}").fillna(False)]:
        notes[i].append(f"Perguruan Tinggi: akronim ambigu ({cleaned['Perguruan Tinggi'][i]})")
    out["Catatan Kualitas"] = notes.map("; ".join)
    report = pd.DataFrame(log).sort_values(["Kolom", "Jumlah"], ascending=[True, False])
    summary = pd.DataFrame({
        "Kolom": FIELDS + ["Dream Job"],
        "Nilai unik sebelum": [df[f].nunique() for f in FIELDS + ["Dream Job"]],
        "Nilai unik sesudah": [cleaned[f].nunique() for f in FIELDS + ["Dream Job"]],
        "Baris dikosongkan": [int((df[f].notna() & cleaned[f].isna()).sum()) for f in FIELDS + ["Dream Job"]],
    })
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    path = Path(out_dir) / "Konsultasi_Karir_bersih.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        for name, frame in [("Data_Bersih", out), ("Laporan_Perubahan", report), ("Ringkasan", summary)]:
            frame.to_excel(xw, sheet_name=name, index=False)
            ws = xw.sheets[name]
            ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                cell.font = Font(name="Arial", bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="173F91")
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(42, max(12, len(str(col[0].value)) + 4))
    print(summary.to_string(index=False)); print("baris bercatatan:", int((out["Catatan Kualitas"] != "").sum()), "| disimpan:", path)


if __name__ == "__main__":
    main(*sys.argv[1:3])
