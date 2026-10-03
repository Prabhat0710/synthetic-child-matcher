import pandas as pd
from pathlib import Path

def _resolve_path(relative_path: str) -> Path:
    """Resolve a path relative to the project root (the scratch folder)."""
    # The project root is two levels up from this file (app/processing)
    return Path(__file__).resolve().parents[2] / relative_path

def load_child_data(csv_path: str) -> pd.DataFrame:
    """Load synthetic child data.

    Parameters
    ----------
    csv_path: str
        Path relative to the project root, e.g. "data/synthetic_children.csv".

    Returns
    -------
    pd.DataFrame
        Loaded child dataframe.
    """
    full_path = _resolve_path(csv_path)
    return pd.read_csv(full_path)

def load_family_data(csv_path: str) -> pd.DataFrame:
    """Load family data (capacity information)."""
    full_path = _resolve_path(csv_path)
    return pd.read_csv(full_path)
