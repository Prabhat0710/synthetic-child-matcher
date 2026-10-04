import pandas as pd
import numpy as np


def compute_child_needs(children_df: pd.DataFrame) -> pd.DataFrame:
    """Derive a normalised 'needs' profile for each child.

    Expected input columns (from synthetic_children.csv):
        child_id, name, age, medical_needs, behavioral_needs,
        educational_needs, emotional_needs, physical_needs

    Returns a DataFrame with child_id and one 0‑1 score per need category.
    """
    need_cols = [
        "medical_needs",
        "behavioral_needs",
        "educational_needs",
        "emotional_needs",
        "physical_needs",
    ]

    needs = children_df[["child_id"] + need_cols].copy()

    # Static normalise each need column to 0-1 (assuming 1-10 scale)
    for col in need_cols:
        needs[col] = needs[col] / 10.0

    return needs


def compute_family_capacity(families_df: pd.DataFrame) -> pd.DataFrame:
    """Derive a normalised 'capacity' profile for each family.

    Expected input columns (from families.csv):
        family_id, family_name, medical_capacity, behavioral_capacity,
        educational_capacity, emotional_capacity, physical_capacity

    Returns a DataFrame with family_id and one 0‑1 score per capacity category.
    """
    cap_cols = [
        "medical_capacity",
        "behavioral_capacity",
        "educational_capacity",
        "emotional_capacity",
        "physical_capacity",
    ]

    capacity = families_df[["family_id"] + cap_cols].copy()

    for col in cap_cols:
        capacity[col] = capacity[col] / 10.0

    return capacity
