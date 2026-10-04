import streamlit as st
from app.gemini.explain import generate_explanation
from app.db.database import save_explanation, get_explanation
from app.processing.data_loader import save_family_data

# Mapping between natural language answers and capacity scores (1-10)
ANSWER_MAP = {
    "Yes, absolutely / Highly prepared": 10,
    "Yes, moderately prepared": 7,
    "Somewhat prepared": 5,
    "Not very prepared": 3,
    "Cannot provide this right now": 1
}
INV_ANSWER_MAP = {v: k for k, v in ANSWER_MAP.items()}

def _get_closest_answer_index(val):
    """Finds the dropdown index that closest matches their current numeric score."""
    closest_score = min(INV_ANSWER_MAP.keys(), key=lambda k: abs(k - val))
    return list(ANSWER_MAP.keys()).index(INV_ANSWER_MAP[closest_score])

def render(scores_df, families_df, current_user_id):
    st.title("👨‍👩‍👧 Family Match Portal")
    
    # Get family details
    family_row = families_df[families_df['family_id'] == current_user_id].iloc[0]
    family_name = family_row['family_name']
    
    st.markdown(f"### Welcome, **{family_name}**!")
    
    # --- INTERACTIVE QUESTIONNAIRE ---
    with st.expander("📝 Update Your Support Capacity (Questionnaire)", expanded=False):
        st.write("Answer these questions to help us match you with children based on the specific support you can provide.")
        
        with st.form("capacity_form"):
            med_ans = st.selectbox(
                "1. How comfortable are you providing specialized medical care?", 
                list(ANSWER_MAP.keys()), 
                index=_get_closest_answer_index(family_row['medical_capacity'])
            )
            beh_ans = st.selectbox(
                "2. How prepared are you to support a child with significant behavioral challenges?", 
                list(ANSWER_MAP.keys()), 
                index=_get_closest_answer_index(family_row['behavioral_capacity'])
            )
            edu_ans = st.selectbox(
                "3. Can you provide extensive support for special educational needs (e.g., tutoring, advocacy)?", 
                list(ANSWER_MAP.keys()), 
                index=_get_closest_answer_index(family_row['educational_capacity'])
            )
            emo_ans = st.selectbox(
                "4. How experienced are you in navigating complex emotional trauma?", 
                list(ANSWER_MAP.keys()), 
                index=_get_closest_answer_index(family_row['emotional_capacity'])
            )
            phy_ans = st.selectbox(
                "5. Is your home adapted, and are you prepared for physical accessibility needs?", 
                list(ANSWER_MAP.keys()), 
                index=_get_closest_answer_index(family_row['physical_capacity'])
            )
            
            if st.form_submit_button("Save Answers & Update Matches", type="primary"):
                # Use Backend Contracts
                import app.backend.contracts as api
                
                profile_data = {
                    'medical_capacity': ANSWER_MAP[med_ans],
                    'behavioral_capacity': ANSWER_MAP[beh_ans],
                    'educational_capacity': ANSWER_MAP[edu_ans],
                    'emotional_capacity': ANSWER_MAP[emo_ans],
                    'physical_capacity': ANSWER_MAP[phy_ans]
                }
                
                # Save and trigger the engine
                api.save_parent_profile(current_user_id, profile_data)
                api.submit_parent_profile(current_user_id)
                
                st.cache_data.clear()
                st.rerun()

    st.divider()
    
    # --- STATUS MESSAGE ---
    st.info("⏳ **Profile Submitted!** Waiting for Admin review and invitations.")
    
    # --- TABS: INVITATIONS & REJECTIONS ---
    import app.backend.contracts as api
    
    tab_invite, tab_reject = st.tabs(["📨 Invitations", "🚫 Incompatible Matches (System Rejected)"])
    
    with tab_invite:
        invites = api.get_parent_invitations(current_user_id)
        if invites.empty:
            st.write("No invitations from the Admin yet. Please check back later!")
        else:
            for idx, row in invites.iterrows():
                st.success(f"**Invitation!** You have been invited to review **Child {row['child_id']}**! (Status: {row['status'].title()})")
                cols = st.columns([1, 1, 4])
                cols[0].button("Accept", key=f"acc_{row['invitation_id']}", type="primary")
                cols[1].button("Decline", key=f"dec_{row['invitation_id']}")
                
    with tab_reject:
        barriers = api.get_barriers_for_parent(current_user_id)
        if barriers.empty:
            st.write("No system rejections recorded yet.")
        else:
            st.write("The matching engine automatically filtered out the following children due to capacity constraints. This ensures we only present matches where you can fully support the child's needs.")
            
            for idx, row in barriers.iterrows():
                with st.expander(f"Child {row['child_id']} - {row['severity']} Barrier"):
                    st.error(f"**Category:** {row['category'].title()}")
                    st.write(f"**Reason:** {row['reason']}")
