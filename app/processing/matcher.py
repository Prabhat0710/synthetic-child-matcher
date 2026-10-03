import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Maps need columns → capacity columns
_NEED_TO_CAPACITY = {
    "medical_needs": "medical_capacity",
    "behavioral_needs": "behavioral_capacity",
    "educational_needs": "educational_capacity",
    "emotional_needs": "emotional_capacity",
    "physical_needs": "physical_capacity",
}

NEED_COLS = list(_NEED_TO_CAPACITY.keys())
CAP_COLS = list(_NEED_TO_CAPACITY.values())


def compute_compatibility_scores(
    needs_df: pd.DataFrame,
    capacity_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute compatibility between every child and every family.

    Uses cosine similarity between the child‑needs vector and the
    family‑capacity vector, then also records per‑category gaps.

    Returns
    -------
    pd.DataFrame
        Columns: child_id, family_id, overall_score,
                 gap_medical, gap_behavioral, gap_educational,
                 gap_emotional, gap_physical
    """
    needs_matrix = needs_df[NEED_COLS].values      # (n_children, 5)
    cap_matrix = capacity_df[CAP_COLS].values       # (n_families, 5)

    # Cosine similarity → (n_children, n_families)
    sim_matrix = cosine_similarity(needs_matrix, cap_matrix)

    rows = []
    for i, child_id in enumerate(needs_df["child_id"]):
        for j, family_id in enumerate(capacity_df["family_id"]):
            overall = float(np.clip(sim_matrix[i, j], 0, 1))

            # Per‑category gap = need − capacity (positive → unmet need)
            gaps = {}
            for need_col, cap_col in _NEED_TO_CAPACITY.items():
                gap = float(needs_df.iloc[i][need_col] - capacity_df.iloc[j][cap_col])
                short_name = need_col.replace("_needs", "")
                gaps[f"gap_{short_name}"] = round(gap, 3)

            rows.append(
                {
                    "child_id": child_id,
                    "family_id": family_id,
                    "overall_score": round(overall, 3),
                    **gaps,
                }
            )

    return pd.DataFrame(rows)
