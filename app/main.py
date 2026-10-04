import sys
from pathlib import Path

# Ensure the project root is on the import path so 'app' is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from app.processing.data_loader import load_child_data, load_family_data
from app.processing.preprocess import compute_child_needs, compute_family_capacity
from app.processing.matcher import compute_compatibility_scores
from app.db.database import save_scores, init_db
from app.ui import parent_view, admin_analysis

st.set_page_config(page_title="Child Matcher", layout="wide", page_icon="🤝")

# Ensure DB is initialized
init_db()

# --- INJECT CUSTOM CSS ---
def load_css():
    css_path = Path(__file__).parent / "ui" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# --- DATA PIPELINE ---
@st.cache_data
def get_data():
    """Loads CSVs, runs preprocessing and matching, caches results."""
    children_df = load_child_data("data/synthetic_children.csv")
    families_df = load_family_data("data/families.csv")
    needs_df = compute_child_needs(children_df)
    capacity_df = compute_family_capacity(families_df)
    scores_df = compute_compatibility_scores(needs_df, capacity_df)
    
    # Save scores to SQLite for persistence
    save_scores(scores_df)
    
    return children_df, families_df, scores_df

children_df, families_df, scores_df = get_data()

# --- AUTHENTICATION STATE ---
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# --- SIDEBAR NAV & LOGIN ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.title("Access Portal")
    
    if not st.session_state.role:
        st.write("Please log in to continue.")
        
        with st.form("login_form"):
            username = st.text_input("Username / ID", placeholder="e.g. sharma01")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    # Validate against users.csv
                    import pandas as pd
                    users_df = pd.read_csv("data/users.csv")
                    user_match = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
                    
                    if user_match.empty:
                        st.error("❌ Invalid username or password.")
                    else:
                        user = user_match.iloc[0]
                        st.session_state.role = user['role']
                        st.session_state.user_id = user['family_id'] if user['role'] == 'Parent' else 'admin'
                        st.rerun()
    else:
        st.success(f"Logged in as: **{st.session_state.role}**")
        if st.session_state.role == "Parent":
            fam_name = families_df[families_df['family_id'] == st.session_state.user_id]['family_name'].iloc[0]
            st.caption(f"Profile: {fam_name}")
            
        if st.button("Log out", use_container_width=True):
            st.session_state.role = None
            st.session_state.user_id = None
            st.rerun()

# --- ROUTING ---
if not st.session_state.role:
    st.title("🤝 Welcome to Synthetic Child Matcher")
    st.markdown("""
    This platform uses AI and data matching to pair children in the welfare system with prospective families based on compatibility.
    
    ⬅️ **Please log in using the sidebar** to view your personalized dashboard.
    """)
elif st.session_state.role == "Admin":
    admin_analysis.render(scores_df, children_df, families_df)
elif st.session_state.role == "Parent":
    parent_view.render(scores_df, families_df, st.session_state.user_id)
