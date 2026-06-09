import pandas as pd
import numpy as np

KRITERIA_COLS = {
    "C1": "engagement_rate",
    "C2": "content_quality_score",
    "C3": "niche_relevance",
    "C4": "posting_consistency",
    "C5": "followers"
}

DEFAULT_BOBOT = {"C1": 0.35, "C2": 0.20, "C3": 0.20, "C4": 0.15, "C5": 0.10}

def hitung_wsm(kol_list: list[dict], bobot: dict = None) -> list[dict]:
    if not kol_list:
        return []
    if bobot is None:
        bobot = DEFAULT_BOBOT

    df = pd.DataFrame(kol_list)
    cols = list(KRITERIA_COLS.values())

    # Min-max normalization (benefit criteria)
    X = df[cols].copy().astype(float)
    X_min = X.min()
    X_max = X.max()
    diff = X_max - X_min
    diff = diff.replace(0, 1)  # avoid division by zero
    X_norm = (X - X_min) / diff
    X_norm = X_norm.fillna(0)

    # WSM score
    w = [bobot[k] for k in KRITERIA_COLS.keys()]
    df["skor_total"] = X_norm.dot(w)

    # Kontribusi per kriteria
    for i, (kode, col) in enumerate(KRITERIA_COLS.items()):
        df[f"r_{kode.lower()}"] = X_norm[col].round(4)
        df[f"kontribusi_{kode.lower()}"] = (X_norm[col] * w[i]).round(4)

    df["skor_total"] = df["skor_total"].round(4)
    df = df.sort_values("skor_total", ascending=False).reset_index(drop=True)
    df["posisi"] = df.index + 1

    return df.to_dict(orient="records")
