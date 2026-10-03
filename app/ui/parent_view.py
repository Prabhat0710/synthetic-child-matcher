import streamlit as st
from app.gemini.explain import generate_explanation
from app.db.database import save_explanation, get_explanation

def render(scores_df, families_df, current_user_id):
    st.title("👨‍👩‍👧 Family Match Portal")
    
    # Get family details
    family_name = families_df[families_df['family_id'] == current_user_id]['family_name'].iloc[0]
    st.markdown(f"### Welcome, **{family_name}**!")
    st.write("Here are the children whose needs most closely align with your family's support capacity.")

    # Filter scores to only show this family's matches
    my_matches = scores_df[scores_df['family_id'] == current_user_id].sort_values('overall_score', ascending=False)
    
    if my_matches.empty:
        st.info("No matches found.")
        return
        
    st.divider()

    # Pretty UI for matches
    for idx, row in my_matches.head(5).iterrows():
        score = row['overall_score']
        
        # Color coding the expander header based on score
        if score >= 0.8:
            emoji = "🌟"
            color = "green"
        elif score >= 0.6:
            emoji = "✨"
            color = "orange"
        else:
            emoji = "💡"
            color = "gray"
            
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
                if existing_exp:
                    st.info(existing_exp)
                else:
                    with st.spinner("Generating insights..."):
                        exp = generate_explanation(row.to_dict())
                        save_explanation(row['child_id'], row['family_id'], exp)
                        st.info(exp)
