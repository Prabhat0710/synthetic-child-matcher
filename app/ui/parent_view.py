import streamlit as st
import pandas as pd
from app.gemini.explain import generate_explanation
from app.db.database import save_explanation, get_explanation
from app.processing.data_loader import save_family_data
from app.ui.questions import QUESTIONNAIRE, score_answer

def render(scores_df, families_df, current_user_id):
    st.title("👨‍👩‍👧 Family Match Portal")
    
    # Get family details
    family_row = families_df[families_df['family_id'] == current_user_id].iloc[0]
    family_name = family_row['family_name']
    
    st.markdown(f"### Welcome, **{family_name}**!")
    
    # Initialize session state for answers if not present
    state_key = f"answers_{current_user_id}"
    ANSWERS_FILE = "data/parent_answers.json"
    
    if state_key not in st.session_state:
        import json
        import os
        
        if os.path.exists(ANSWERS_FILE):
            with open(ANSWERS_FILE, 'r') as f:
                try:
                    all_answers = json.load(f)
                except json.JSONDecodeError:
                    all_answers = {}
                    
            if current_user_id in all_answers:
                st.session_state[state_key] = all_answers[current_user_id]
                # If they have saved answers in the file, they have submitted before
                st.session_state[f"submitted_{current_user_id}"] = True
            else:
                st.session_state[state_key] = {}
        else:
            st.session_state[state_key] = {}
        
    answers = st.session_state[state_key]
    
    # Calculate Live Progress
    total_q = sum(len(q_list) for q_list in QUESTIONNAIRE.values())
    answered_q = sum(1 for v in answers.values() if v and v != "Select an option...")
    progress_pct = int((answered_q / total_q) * 100)
    
    st.progress(progress_pct, text=f"Profile Completion: {progress_pct}% ({answered_q}/{total_q} questions answered)")
    st.write("")
    
    # --- INTERACTIVE QUESTIONNAIRE ---
    with st.expander("📝 Update Your Support Capacity (Questionnaire)", expanded=True):
        st.write("Answer these questions to help us match you with children based on the specific support you can provide.")
        
        for section, questions in QUESTIONNAIRE.items():
            st.markdown(f"#### {section}")
            for q in questions:
                q_id = q['id']
                q_type = q.get('type', 'select')
                
                if q_type == 'select':
                    opts = ["Select an option..."] + q['options']
                    # Get current val
                    current_val = answers.get(q_id, "Select an option...")
                    idx = opts.index(current_val) if current_val in opts else 0
                    
                    val = st.selectbox(q['text'], opts, index=idx, key=f"sb_{q_id}")
                    answers[q_id] = val
                    
                elif q_type == 'multiselect':
                    current_val = answers.get(q_id, [])
                    val = st.multiselect(q['text'], q['options'], default=current_val, key=f"ms_{q_id}")
                    answers[q_id] = val
                    
                elif q_type == 'text':
                    current_val = answers.get(q_id, "")
                    val = st.text_area(q['text'], value=current_val, key=f"ta_{q_id}")
                    answers[q_id] = val
                    
            st.write("")
            
        if st.button("Submit & Save Profile", type="primary", use_container_width=True):
            # Calculate 5 core capacities by mapping
            cap_scores = {'medical_capacity': [], 'behavioral_capacity': [], 'educational_capacity': [], 'emotional_capacity': [], 'physical_capacity': []}
            
            for section, questions in QUESTIONNAIRE.items():
                for q in questions:
                    if 'maps_to' in q:
                        ans = answers.get(q['id'], "Select an option...")
                        if ans != "Select an option...":
                            cap_scores[q['maps_to']].append(score_answer(ans))
                            
            profile_data = {}
            for cap, scores in cap_scores.items():
                # Average the scores, default to 0 if none answered
                profile_data[cap] = int(sum(scores)/len(scores)) if scores else 0
                
            # Save raw answers to JSON so they persist across logins
            import json
            import os
            
            all_ans = {}
            if os.path.exists(ANSWERS_FILE):
                with open(ANSWERS_FILE, 'r') as f:
                    try:
                        all_ans = json.load(f)
                    except json.JSONDecodeError:
                        pass
            
            all_ans[current_user_id] = answers
            with open(ANSWERS_FILE, 'w') as f:
                json.dump(all_ans, f)
                
            import app.backend.contracts as api
            api.save_parent_profile(current_user_id, profile_data)
            api.submit_parent_profile(current_user_id)
            
            st.session_state[f"submitted_{current_user_id}"] = True
            st.cache_data.clear()
            st.rerun()

    # --- SUBMITTED STATE & TABS ---
    if st.session_state.get(f"submitted_{current_user_id}", False):
        st.divider()
        
        st.info("⏳ **Profile Submitted!** Waiting for Admin review and invitations.")
        
        import app.backend.contracts as api
        
        tab_invite, tab_reject = st.tabs(["📨 Invitations", "🚫 Incompatible Matches (System Rejected)"])
        
        with tab_invite:
            invites = api.get_parent_invitations(current_user_id)
            if invites is None or invites.empty:
                st.write("No invitations from the Admin yet. Please check back later!")
            else:
                for idx, row in invites.iterrows():
                    st.success(f"**Invitation!** You have been invited to review **Child {row['child_id']}**! (Status: {row['status'].title()})")
                    cols = st.columns([1, 1, 4])
                    cols[0].button("Accept", key=f"acc_{row['invitation_id']}", type="primary")
                    cols[1].button("Decline", key=f"dec_{row['invitation_id']}")
                    
        with tab_reject:
            barriers = api.get_barriers_for_parent(current_user_id)
            if barriers is None or barriers.empty:
                st.write("No system rejections recorded yet.")
            else:
                st.write("The matching engine automatically filtered out the following children due to capacity constraints. This ensures we only present matches where you can fully support the child's needs.")
                
                for idx, row in barriers.iterrows():
                    with st.expander(f"Child {row['child_id']} - {row['severity']} Barrier"):
                        st.error(f"**Category:** {row['category'].title()}")
                        st.write(f"**Reason:** {row['reason']}")
