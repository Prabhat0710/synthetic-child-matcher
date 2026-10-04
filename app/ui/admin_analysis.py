import streamlit as st
import pandas as pd
import altair as alt

def render(scores_df, children_df, families_df):
    st.title("📊 Agency Admin Dashboard")
    
    # Top level metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Children in System", len(children_df))
    col2.metric("Approved Families", len(families_df))
    col3.metric("Possible Pairings Evaluated", len(scores_df))

    tab_dash, tab_parents, tab_children = st.tabs(["📈 Dashboard Overview", "👨‍👩‍👧 Parents (AI Reviews)", "🧒 Children (Matches)"])

    with tab_dash:
        st.subheader("Parent Onboarding Status")
        st.write("Track how many families have completed their capacity questionnaires.")
        
        # Calculate progress for each family
        def calc_progress(row):
            caps = [row['medical_capacity'], row['behavioral_capacity'], row['educational_capacity'], row['emotional_capacity'], row['physical_capacity']]
            return (sum(1 for c in caps if c > 0) / 5.0) * 100

        families_status = families_df.copy()
        families_status['Completion'] = families_status.apply(calc_progress, axis=1)
        
        st.dataframe(
            families_status[['family_id', 'family_name', 'Completion']],
            column_config={
                "family_id": "Family ID",
                "family_name": "Family Name",
                "Completion": st.column_config.ProgressColumn(
                    "Profile Completion",
                    help="Percentage of the questionnaire completed",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        # Gap Analysis Chart
        st.subheader("System-Wide Gap Analysis")
        st.write("Average unmet needs across all possible pairings. Higher positive values mean families generally lack capacity in these areas compared to child needs.")
        
        if not scores_df.empty:
            gap_cols = ['gap_medical', 'gap_behavioral', 'gap_educational', 'gap_emotional', 'gap_physical']
            avg_gaps = scores_df[gap_cols].mean().reset_index()
            avg_gaps.columns = ['Need Category', 'Average Gap']
            avg_gaps['Need Category'] = avg_gaps['Need Category'].str.replace('gap_', '').str.title()
            
            chart = alt.Chart(avg_gaps).mark_bar().encode(
                x=alt.X('Average Gap:Q', title="Average Capacity Gap (Positive = Unmet Need)"),
                y=alt.Y('Need Category:N', sort='-x', title=""),
                color=alt.condition(
                    alt.datum['Average Gap'] > 0,
                    alt.value('#ff4b4b'),  # Red for unmet needs
                    alt.value('#21c354')   # Green for excess capacity
                ),
                tooltip=['Need Category', 'Average Gap']
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No matching scores available yet.")

        st.divider()
        st.subheader("📬 Invitation Status Tracking")
        import app.backend.contracts as api
        
        all_invites = api.get_all_invitations()
        if not all_invites.empty:
            # Join with family names
            fam_map = dict(zip(families_df['family_id'], families_df['family_name']))
            all_invites['Family Name'] = all_invites['parent_id'].map(fam_map)
            
            # Format display df
            display_invites = all_invites[['created_at', 'Family Name', 'parent_id', 'child_id', 'status']].copy()
            display_invites.columns = ['Sent Date', 'Family Name', 'Family ID', 'Child ID', 'Status']
            
            # Color code status
            def color_status(val):
                color = 'orange' if val == 'pending' else 'green' if val == 'accepted' else 'red'
                return f'color: {color}; font-weight: bold'
                
            st.dataframe(display_invites.style.applymap(color_status, subset=['Status']), use_container_width=True, hide_index=True)
        else:
            st.info("No invitations have been sent out yet.")

    with tab_parents:
        st.subheader("Parent Profiles & AI Reviews")
        st.write("Automatically generated analysis of each family's strengths and support limitations based on their questionnaire.")
        
        for _, fam in families_df.iterrows():
            with st.expander(f"Family: {fam['family_name']} (ID: {fam['family_id']})"):
                caps = {
                    "Medical Support": fam['medical_capacity'],
                    "Behavioral Support": fam['behavioral_capacity'],
                    "Educational Support": fam['educational_capacity'],
                    "Emotional Support": fam['emotional_capacity'],
                    "Physical Support": fam['physical_capacity']
                }
                
                if sum(caps.values()) == 0:
                    st.info("This family has not completed their profile yet.")
                else:
                    # Basic rule-based AI review
                    strong = [k for k, v in caps.items() if v >= 7]
                    weak = [k for k, v in caps.items() if v <= 4]
                    moderate = [k for k, v in caps.items() if 4 < v < 7]
                    
                    st.write("**🤖 AI Capacity Assessment:**")
                    if strong:
                        st.success(f"**Strong Points:** This family demonstrates high capacity and readiness for **{', '.join(strong)}**.")
                    if weak:
                        st.error(f"**Weak Points:** This family currently lacks the necessary resources or experience for high **{', '.join(weak)}** needs.")
                    if moderate:
                        st.warning(f"**Moderate Areas:** Their capacity for **{', '.join(moderate)}** is average and may require agency support.")

    with tab_children:
        st.subheader("Child Matching")
        st.write("Select a child to view how all registered parents match against their specific needs.")
        
        import app.backend.contracts as api
        
        if children_df.empty:
             st.info("No children data available.")
        else:
             child_options = children_df['child_id'] + " - " + children_df['name']
             selected_child_str = st.selectbox("Select a Child", child_options)
             
             if selected_child_str:
                 sel_child_id = selected_child_str.split(" - ")[0]
                 
                 child_scores = scores_df[scores_df['child_id'] == sel_child_id].sort_values(by='overall_score', ascending=False)
                 
                 if child_scores.empty:
                     st.warning("No matches computed yet.")
                 else:
                     st.write(f"Showing all mathematical matches for **{selected_child_str}**:")
                     
                     display_df = child_scores[['family_id', 'overall_score', 'gap_medical', 'gap_behavioral', 'gap_educational', 'gap_emotional', 'gap_physical']].copy()
                     fam_map = dict(zip(families_df['family_id'], families_df['family_name']))
                     display_df.insert(1, 'family_name', display_df['family_id'].map(fam_map))
                     
                     styled_df = display_df.style.background_gradient(
                         cmap='RdYlGn', 
                         subset=['overall_score'], 
                         vmin=0, 
                         vmax=1
                     ).format({
                         'overall_score': '{:.1%}',
                         'gap_medical': '{:.2f}',
                         'gap_behavioral': '{:.2f}',
                         'gap_educational': '{:.2f}',
                         'gap_emotional': '{:.2f}',
                         'gap_physical': '{:.2f}'
                     })
                     
                     st.dataframe(styled_df, use_container_width=True, hide_index=True)
                     
                     st.divider()
                     st.subheader("Send Invitation")
                     
                     # Invite UI
                     col1, col2 = st.columns([3, 1])
                     with col1:
                         fam_invite_options = display_df['family_id'] + " - " + display_df['family_name']
                         selected_invite_fam = st.selectbox("Select Family to Invite for this Child:", fam_invite_options, key="invite_sel")
                     with col2:
                         st.write("") # spacing
                         st.write("")
                         if st.button("Send Invite", type="primary", use_container_width=True):
                             fam_id_to_invite = selected_invite_fam.split(" - ")[0]
                             # Mock a match_id since we bypassed the hard engine here, or grab it if it exists
                             import uuid
                             match_id = str(uuid.uuid4()) 
                             
                             if api.create_invitation(fam_id_to_invite, sel_child_id, match_id):
                                 st.success("Invitation sent!")
                             else:
                                 st.error("Error sending invitation.")
