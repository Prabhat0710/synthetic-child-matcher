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
                # Update the DataFrame
                families_df.loc[families_df['family_id'] == current_user_id, 'medical_capacity'] = ANSWER_MAP[med_ans]
                families_df.loc[families_df['family_id'] == current_user_id, 'behavioral_capacity'] = ANSWER_MAP[beh_ans]
                families_df.loc[families_df['family_id'] == current_user_id, 'educational_capacity'] = ANSWER_MAP[edu_ans]
                families_df.loc[families_df['family_id'] == current_user_id, 'emotional_capacity'] = ANSWER_MAP[emo_ans]
                families_df.loc[families_df['family_id'] == current_user_id, 'physical_capacity'] = ANSWER_MAP[phy_ans]
                
                # Save to CSV and clear cache so the matching engine re-runs
                save_family_data(families_df)
                st.cache_data.clear()
                st.rerun()

    st.write("Here are the children whose needs most closely align with your current capacity profile.")

    # --- MATCHES DISPLAY ---
    my_matches = scores_df[scores_df['family_id'] == current_user_id].sort_values('overall_score', ascending=False)
    
    if my_matches.empty:
        st.info("No matches found.")
        return
        
    st.divider()

    for idx, row in my_matches.head(5).iterrows():
        score = row['overall_score']
        
        if score >= 0.8:
            emoji = "🌟"
        elif score >= 0.6:
            emoji = "✨"
        else:
            emoji = "💡"
            
        with st.expander(f"{emoji} Match with Child {row['child_id']} - Score: {score:.0%}"):
            st.progress(score, text=f"Overall Compatibility: {score:.0%}")
            
            cols = st.columns([1, 2])
            with cols[0]:
                st.write("**Capacity Analysis:**")
                for col in ['gap_medical', 'gap_behavioral', 'gap_educational', 'gap_emotional', 'gap_physical']:
                    val = row[col]
                    category = col.replace('gap_', '').title()
                    if val > 0.2: 
                        st.markdown(f"- {category}: ⚠️ *Gap ({val:.1f})*")
                    elif val > 0:
                        st.markdown(f"- {category}: 🟡 *Slight Gap ({val:.1f})*")
                    else:
                        st.markdown(f"- {category}: ✅ *Covered*")
                        
            with cols[1]:
                st.write("**AI Match Analyst Insight:**")
                existing_exp = get_explanation(row['child_id'], row['family_id'])
                
                # Do not display if it's an old cached error
                if existing_exp and "[Gemini" in existing_exp:
                    existing_exp = None
                    
                if existing_exp:
                    st.info(existing_exp)
                else:
                    if st.button("✨ Generate AI Insight", key=f"gen_{row['child_id']}"):
                        with st.spinner("Analyzing match..."):
                            exp = generate_explanation(row.to_dict())
                            if "[Gemini" not in exp:
                                save_explanation(row['child_id'], row['family_id'], exp)
                                st.rerun()
                            else:
                                st.error(exp)
