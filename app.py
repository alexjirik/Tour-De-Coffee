import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Sets up the browser tab with a wide layout for better side-by-side structures
st.set_page_config(page_title="Tour de Coffee", page_icon="☕", layout="centered")

# 2. Custom CSS Injection for Coffee & Surf Aesthetics
# This changes the primary button color to a warm, caffeinated terracotta/amber tone
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #D27D2D;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #A0522D;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
# Cleaned up into a nice hero layout
st.title("☕ Tour de Coffee")
st.caption("Keeping the community caffeinated & stoked. 🤙")
st.link_button("Follow the Instagram", "https://instagram.com/tour.decoffee")

st.divider()

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="Reviews", ttl=0)

if existing_data is not None:
    existing_data = existing_data.dropna(how="all")
else:
    existing_data = pd.DataFrame(columns=["Shop", "Stars", "Review"])

# --- APP METRICS (Gamifying the feed) ---
# Displays a cool stat counter at the top of the feed
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Cafés Discovered", value=len(existing_data))
with col2:
    st.metric(label="Community Stoked Level", value="100%")

st.divider()

# --- THE FEED (The Local Lineup) ---
st.subheader("✨ The Local Lineup")

if existing_data.empty:
    st.info("No reviews in the database yet. Be the first to drop one!")
else:
    # Reverse the dataframe so the LATEST reviews appear at the top of the feed!
    for index, row in existing_data.iloc[::-1].iterrows():
        # Wrap each review inside a clean card container with a border
        with st.container(border=True):
            # Header Row: Shop Name and Stars side-by-side
            shop_col, star_col = st.columns([3, 1])
            with shop_col:
                st.markdown(f"### 📍 {row['Shop']}")
            with star_col:
                st.markdown(f"### {row['Stars']}")
            
            # Sub-content with cleaner formatting
            st.markdown("**The Brew & The Vibe:**")
            st.write(row['Review'])

# --- LOG A NEW SPOT ---
st.sidebar.header("📥 Drop a New Review")
with st.sidebar:
    st.write("Found a new gem? Add it to the map.")
    
    shop_name = st.text_input("Where are we drinking coffee?", placeholder="e.g., Sunrise Coffee Roasters")
    
    st.write("Overall Vibe & Taste")
    rating = st.feedback("stars")
    
    review_text = st.text_area(
        "Spill the beans...", 
        placeholder="How was the brew? Good seating? Fast Wi-Fi? Dog friendly?",
        max_chars=280 # Keeps reviews punchy like a tweet/Instagram caption
    )
    
    # The submit button inside the sidebar
    if st.button("Post Review", use_container_width=True):
        if shop_name and review_text and rating is not None:
            stars_display = "⭐" * (rating + 1)
            
            new_review = pd.DataFrame([{
                "Shop": shop_name,
                "Stars": stars_display,
                "Review": review_text
            }])
            
            updated_df = pd.concat([existing_data, new_review], ignore_index=True)
            conn.update(worksheet="Reviews", data=updated_df)
            
            st.success(f"Added {shop_name}! 🌊")
            st.rerun()
        else:
            st.error("Hold up! Fill out all fields before paddling out.")
