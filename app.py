import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="Synthetic Mindset Engine", layout="wide")

# Custom Styling to make it look less like default Streamlit
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: 500; color: #4A4A4A;}
    .metric-container { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ff9f43; }
    </style>
    """, unsafe_allow_html=True)

st.title("Growth Target & Mindset Engine 🎯")
st.markdown("<p class='big-font'>Fusing quantitative predispositions with qualitative human truths.</p>", unsafe_allow_html=True)

# 1. Data Ingestion
with st.sidebar:
    st.header("1. Ingest Data")
    st.markdown("Upload respondent-level data. Ensure your Growth Targets (Mindsets) are included as a column.")
    uploaded_file = st.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Load Data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    columns = df.columns.tolist()

    # 2. Strategy Configuration
    st.sidebar.header("2. Strategy Configuration")
    
    # Selecting the Growth Target (The Core Mindset)
    target_var = st.sidebar.selectbox("Select Growth Target / Mindset Column", columns, index=0)
    
    # Selecting the behavior/demo to cross against
    explore_var = st.sidebar.selectbox("Select Variable to Explore", columns, index=min(1, len(columns)-1))
    
    weight_var = st.sidebar.selectbox("Select Survey Weight (Optional)", ['None (Unweighted)'] + columns)

    if st.sidebar.button("Run Analysis", type="primary"):
        
        # --- TAB LAYOUT ---
        tab1, tab2 = st.tabs(["📊 The Quant Crosstab", "🧠 The Human Truth (Qual)"])
        
        with tab1:
            st.subheader(f"Profiling '{target_var}' against '{explore_var}'")
            
            # Apply weighting
            weight_col = weight_var if weight_var != 'None (Unweighted)' else '_Weight'
            if weight_col == '_Weight':
                df['_Weight'] = 1
                
            # Calculate Crosstab
            crosstab = pd.crosstab(
                df[explore_var], 
                df[target_var], 
                values=df[weight_col], 
                aggfunc='sum', 
                margins=True, 
                margins_name='Total'
            )
            
            # Calculate Metrics
            results = {}
            for column in crosstab.columns:
                if column != 'Total':
                    count = crosstab[column]
                    vert_pct = (count / crosstab.loc['Total', column]) * 100
                    horz_pct = (count / crosstab['Total']) * 100
                    pop_pct = (crosstab['Total'] / crosstab.loc['Total', 'Total']) * 100
                    index = (vert_pct / pop_pct) * 100
                    
                    results[column] = pd.DataFrame({
                        'Universe Size': count.round(0),
                        'Target Comp (%)': vert_pct.round(1),
                        'Reach (%)': horz_pct.round(1),
                        'Index (100=Avg)': index.round(0)
                    })
            
            final_table = pd.concat(results.values(), axis=1, keys=results.keys())
            final_table = final_table.drop('Total', errors='ignore')
            
            # Highlight high indices
            def color_index(val):
                color = 'green' if val > 115 else 'red' if val < 85 else 'black'
                return f'color: {color}'
            
            # Only apply styling to Index columns
            idx = pd.IndexSlice
            styled_table = final_table.style.applymap(color_index, subset=idx[:, idx[:, 'Index (100=Avg)']])
            
            st.dataframe(styled_table, use_container_width=True, height=400)
            
            st.caption("*Index > 115 indicates a strong predisposition. Index < 85 indicates a barrier.*")

        with tab2:
            st.subheader("Fleshing out the Growth Target")
            st.markdown("Based on the **Five Fundamental Truths**, here is how we contextualize this data.")
            
            # Placeholder for dynamic qualitative integration
            selected_target = st.selectbox("Select a specific segment to view its human truth:", df[target_var].dropna().unique())
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class='metric-container'>
                    <h4>1. Predisposition Driver</h4>
                    <p><i>What underlying motivation or attitude drives {selected_target}?</i></p>
                    <p>(Qualitative input from Ethnography would populate here based on the selected segment.)</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='metric-container'>
                    <h4>4. Master Brand Alignment</h4>
                    <p><i>How does {selected_target} align with where the brand wants to go?</i></p>
                    <p>(Strategic mapping data would populate here.)</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class='metric-container'>
                    <h4>5. The Human Truth</h4>
                    <p><i>Uncovering the defining tension, barrier, or priority.</i></p>
                    <p><b>Observation:</b> High index scores in [X behavior] suggest a desire for efficiency.</p>
                    <p><b>Tension:</b> They want efficiency, but feel brands are sacrificing quality to achieve it.</p>
                </div>
                """, unsafe_allow_html=True)

else:
    # Empty State with Methodology Reminder
    st.info("Awaiting Data Upload in the Sidebar.")
    
    st.divider()
    st.markdown("### The Growth Target Methodology")
    st.markdown("An effective Growth Target delivers on five fundamental truths:")
    
    cols = st.columns(5)
    cols[0].markdown("**1. Predisposition**\nPurchase intent is fleeting, predisposition is forever.")
    cols[1].markdown("**2. Real World**\nGrowth Targets aren't created in a vacuum.")
    cols[2].markdown("**3. Direction**\nA Growth Target gets you where you want to go.")
    cols[3].markdown("**4. Alignment**\nKey to where you want a brand to go.")
    cols[4].markdown("**5. Human Truth**\nGrowth requires clarity & conviction.")
