import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "matches.db"

def _get_conn():
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def save_scores(scores_df: pd.DataFrame):
    """Save computed compatibility scores to SQLite."""
    conn = _get_conn()
    scores_df.to_sql("matches", conn, if_exists="replace", index=False)
    conn.close()

def load_scores() -> pd.DataFrame:
    """Load compatibility scores from SQLite."""
    conn = _get_conn()
    try:
        df = pd.read_sql("SELECT * FROM matches", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def save_explanation(child_id: str, family_id: str, explanation: str):
    """Cache the Gemini explanation in SQLite to save API calls."""
    conn = _get_conn()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS explanations (child_id TEXT, family_id TEXT, explanation TEXT, UNIQUE(child_id, family_id))"
    )
    conn.execute(
        "INSERT OR REPLACE INTO explanations VALUES (?, ?, ?)",
        (child_id, family_id, explanation)
    )
    conn.commit()
    conn.close()

def get_explanation(child_id: str, family_id: str) -> str:
    """Retrieve a cached explanation if it exists."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT explanation FROM explanations WHERE child_id=? AND family_id=?", (child_id, family_id))
        res = cur.fetchone()
        return res[0] if res else None
    except:
        return None
    finally:
        conn.close()
