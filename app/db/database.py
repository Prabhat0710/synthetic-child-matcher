import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "matches.db"

def _get_conn():
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize core database tables required by the engine."""
    conn = _get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            invitation_id TEXT PRIMARY KEY,
            parent_id TEXT NOT NULL,
            child_id TEXT NOT NULL,
            match_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS barriers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id TEXT NOT NULL,
            child_id TEXT NOT NULL,
            category TEXT,
            reason TEXT,
            severity TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS explanations (
            child_id TEXT, 
            family_id TEXT, 
            explanation TEXT, 
            UNIQUE(child_id, family_id)
        )
    ''')
    conn.commit()
    conn.close()

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

# ==========================================
# Invitations CRUD
# ==========================================
import uuid

def create_invitation(parent_id: str, child_id: str, match_id: str) -> bool:
    """Create a new invitation."""
    conn = _get_conn()
    invitation_id = str(uuid.uuid4())
    try:
        conn.execute(
            "INSERT INTO invitations (invitation_id, parent_id, child_id, match_id) VALUES (?, ?, ?, ?)",
            (invitation_id, parent_id, child_id, match_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating invitation: {e}")
        return False
    finally:
        conn.close()

def get_parent_invitations(parent_id: str) -> pd.DataFrame:
    """Retrieve all invitations for a parent."""
    conn = _get_conn()
    try:
        df = pd.read_sql("SELECT * FROM invitations WHERE parent_id = ?", conn, params=(parent_id,))
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

def update_invitation_status(invitation_id: str, status: str) -> bool:
    """Update invitation status."""
    conn = _get_conn()
    try:
        conn.execute("UPDATE invitations SET status = ? WHERE invitation_id = ?", (status, invitation_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# ==========================================
# Barriers CRUD
# ==========================================

def save_barrier(parent_id: str, child_id: str, category: str, reason: str, severity: str):
    """Save a barrier that prevented a match."""
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO barriers (parent_id, child_id, category, reason, severity) VALUES (?, ?, ?, ?, ?)",
            (parent_id, child_id, category, reason, severity)
        )
        conn.commit()
    finally:
        conn.close()

def get_barriers_for_parent(parent_id: str) -> pd.DataFrame:
    """Retrieve all barriers for a parent."""
    conn = _get_conn()
    try:
        df = pd.read_sql("SELECT * FROM barriers WHERE parent_id = ?", conn, params=(parent_id,))
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()
