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

# --- AUTHENTICATION & ROUTING STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# If logged in, force page to app
if st.session_state.role:
    st.session_state.page = "app"

# --- SIDEBAR (Only for logged-in users) ---
if st.session_state.role:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("Care Map Portal")
        st.success(f"Logged in as: **{st.session_state.role}**")
        if st.session_state.role == "Parent":
            fam_name = families_df[families_df['family_id'] == st.session_state.user_id]['family_name'].iloc[0]
            st.caption(f"Profile: {fam_name}")
            
        if st.session_state.role == "Admin":
            st.divider()
            st.subheader("Data Management")
            uploaded_file = st.file_uploader("Upload Children (CSV)", type="csv")
            if uploaded_file is not None:
                with open("data/synthetic_children.csv", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Children data updated successfully!")
                st.cache_data.clear()
                
        if st.button("Log out", use_container_width=True):
            st.session_state.role = None
            st.session_state.user_id = None
            st.session_state.page = "home"
            st.rerun()

# --- ROUTING ---
if st.session_state.page == "home":
    st.markdown("""
        <style>
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid #bbd1ea;
            margin-bottom: 4rem;
        }
        .logo-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .logo-icon {
            font-size: 2.4rem; padding-top: 5px;
        }
        .logo-text {
            line-height: normal; padding-top: 5px;
        }
        .logo-text strong {
            font-size: 1.8rem; display: inline-block;
            color: #04080f;
        }
        .logo-text small {
            font-size: 0.65rem;
            color: #507dbc;
            letter-spacing: 0.05em;
        }
        .nav-links {
            display: flex;
            gap: 1.5rem;
        }
        .nav-links a {
            text-decoration: none;
            color: #507dbc;
            font-weight: 500;
            font-size: 0.9rem;
        }
        .nav-links a:hover {
            color: #04080f;
        }
        .nav-actions {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        .get-involved-btn {
            background-color: #507dbc;
            color: white !important;
            padding: 0.5rem 1.2rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .get-involved-btn:hover {
            background-color: #a1c6ea;
            color: #04080f !important;
        }
        
        /* Hero Section */
        .hero-subtitle {
            font-size: 0.85rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #507dbc;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 3.2rem !important;
            line-height: 1.1 !important;
            color: #04080f !important;
            margin-bottom: 1.5rem !important;
            font-weight: 700 !important;
        }
        .hero-desc {
            font-size: 1.1rem;
            color: #04080f;
            line-height: 1.6;
            margin-bottom: 2rem;
        }
        
        /* Hide padding above header */
        .block-container {
            padding-top: 1rem;
        }
        </style>
        
        <div class="header-container">
            <div class="logo-group">
                <div class="logo-icon">💙</div>
                <div class="logo-text">
                    <strong>Care Map</strong><br>
                    <small>ADOPTION SERVICES</small>
                </div>
            </div>
            <div class="nav-links">
                <a href="#">Home</a>
                <a href="#about-section">About</a>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, spacer, col2 = st.columns([1, 0.1, 1.2])
    with col1:
        st.markdown('<div class="hero-subtitle">REAL FAMILIES. BRIGHTER TOMORROWS.</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="hero-title">Adoption changes<br>lives — including<br>yours.</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-desc">We connect children with safe, loving, and permanent families. Whether you are looking to adopt, foster, or support, you are part of a bigger story.</p>', unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns([1.5, 1])
        with btn_col1:
            if st.button("Start Your Adoption Journey →", type="primary", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
            
    with col2:
        st.image("app/ui/hero_image_cropped.png", use_container_width=True)

    st.write("")
    st.divider()
    
    st.markdown('<div id="about-section" style="padding-top: 4rem;"></div>', unsafe_allow_html=True)
    st.markdown("### About Care Map")
    st.markdown("**What are we building?**")
    st.markdown("Care Map is an intelligent, data-driven matching platform designed to bridge the gap between children in the welfare system and prospective families. By analyzing complex capacity profiles and detailed child needs, our system provides precise, actionable recommendations to welfare agencies and parents alike.")
    st.markdown("**Why did we build it?**")
    st.markdown("The traditional placement process can be slow, opaque, and often struggles to properly align a child's specific needs (medical, behavioral, educational) with a family's true capacity. Care Map was built to ensure safer, more stable, and longer-lasting placements by eliminating guesswork and using rigorous capability matching.")

elif st.session_state.page == "login":
    st.title("Log In or Register")
    st.write("Join Care Map to begin the matching process.")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Log In", "Register as New Parent"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username / ID", placeholder="e.g. sharma01")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)
                
                if submitted:
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        import pandas as pd
                        users_df = pd.read_csv("data/users.csv")
                        user_match = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
                        
                        if user_match.empty:
                            st.error("❌ Invalid username or password.")
                        else:
                            user = user_match.iloc[0]
                            st.session_state.role = user['role']
                            st.session_state.user_id = user['family_id'] if user['role'] == 'Parent' else 'admin'
                            st.session_state.page = "app"
                            st.rerun()
                            
        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type="password")
                new_family_name = st.text_input("Family Name", placeholder="e.g. Smith Family")
                signup_submitted = st.form_submit_button("Register", type="primary", use_container_width=True)
                
                if signup_submitted:
                    if not new_username or not new_password or not new_family_name:
                        st.error("Please fill out all fields.")
                    else:
                        import pandas as pd
                        users_df = pd.read_csv("data/users.csv")
                        if new_username in users_df['username'].values:
                            st.error("Username already exists. Please choose another.")
                        else:
                            families_df = pd.read_csv("data/families.csv")
                            # Create new family ID
                            new_family_id = f"F{len(families_df)+1:03d}"
                            
                            # Add to users.csv
                            new_user = pd.DataFrame([{"username": new_username, "password": new_password, "role": "Parent", "family_id": new_family_id}])
                            new_user.to_csv("data/users.csv", mode='a', header=False, index=False)
                            
                            # Add to families.csv with 0 capacities (unanswered)
                            new_family = pd.DataFrame([{
                                "family_id": new_family_id, 
                                "family_name": new_family_name, 
                                "medical_capacity": 0, 
                                "behavioral_capacity": 0, 
                                "educational_capacity": 0, 
                                "emotional_capacity": 0, 
                                "physical_capacity": 0
                            }])
                            new_family.to_csv("data/families.csv", mode='a', header=False, index=False)
                            
                            st.success("Account created! You can now switch to the 'Log In' tab to access your dashboard.")
                            st.cache_data.clear()
                            
    st.write("")
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

elif st.session_state.page == "app":
    if st.session_state.role == "Admin":
        admin_analysis.render(scores_df, children_df, families_df)
    elif st.session_state.role == "Parent":
        parent_view.render(scores_df, families_df, st.session_state.user_id)
