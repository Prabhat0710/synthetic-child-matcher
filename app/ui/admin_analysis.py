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

    st.divider()
    
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

    st.divider()

    # Detailed Match Table
    st.subheader("Match Database")
    st.write("Full matrix of compatibility scores.")
    
    # Apply background gradient to overall score
    styled_df = scores_df.style.background_gradient(
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
    
    st.dataframe(styled_df, use_container_width=True, height=400)
