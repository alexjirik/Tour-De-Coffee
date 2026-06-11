import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Sets up the browser tab
st.set_page_config(page_title="Tour de Coffee", page_icon="☕", layout="centered")

# Custom CSS Injection for Coffee & Surf Aesthetics AND Pro UX!
st.markdown("""
    <style>
    /* Import both the handwritten header font and the clean body font from Google */
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Montserrat:wght@400;600&display=swap');
    
    /* 1. THE VIBE: Apply Caveat to our main headers */
    h1, h2, h3 {
        font-family: 'Caveat', cursive !important;
        letter-spacing: 1px;
    }

    /* 2. THE UX: Apply Montserrat to all the regular text for perfect legibility */
    html, body, p, div, input, textarea, button {
        font-family: 'Montserrat', sans-serif !important;
    }

    /* 3. THE BUTTONS: A little extra breathing room for touch screens (Better UX for thumbs!) */
    div.stButton > button:first-child {
        background-color: #D27D2D;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease; /* Smooth hover effect */
    }
    div.stButton > button:first-child:hover {
        background-color: #A0522D;
        color: white;
        transform: translateY(-2px); /* Makes the button 'lift' when pressed/hovered */
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("☕ Tour de Coffee")
st.caption("Keeping the community caffeinated & stoked. 🤙")
st.link_button("📸 Follow the Instagram", "https://instagram.com/tour.decoffee")

st.divider()

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="Reviews", ttl=0)

if existing_data is not None:
    existing_data = existing_data.dropna(how="all")
else:
    # Ensure column headers exist even if the sheet is completely blank
    existing_data = pd.DataFrame(columns=["Shop", "Stars", "Review"])

# --- APP METRICS ---
# Unique shops counted separately from total reviews logged
unique_shops_count = existing_data["Shop"].nunique() if not existing_data.empty else 0
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Unique Cafés Found", value=unique_shops_count)
with col2:
    st.metric(label="Total Reviews Logged", value=len(existing_data))

st.divider()

# --- THE FEED (The Local Lineup) ---
st.subheader("✨ The Local Lineup")

if existing_data.empty:
    st.info("No reviews in the database yet. Be the first to drop one!")
else:
    # Make a clean copy to handle math operations safely
    df = existing_data.copy()
    
    # Crucial: convert Stars column to numeric just in case data types get mismatched
    df["Stars"] = pd.to_numeric(df["Stars"], errors='coerce').fillna(5)
    
    # Group by shop name, get the average rating, and sort so the highest rated spots appear first!
    avg_ratings = df.groupby("Shop")["Stars"].mean().sort_values(ascending=False)
    
    # Loop through each unique shop
    for shop, avg_score in avg_ratings.items():
        # Filter down all the individual reviews just for this specific shop
        shop_reviews = df[df["Shop"] == shop]
        
        # Format the mathematical average back into a friendly visual star string
        star_emojis = "⭐" * int(round(avg_score))
        
        # Render a structured visual card container for the cafe
        with st.container(border=True):
            shop_col, star_col = st.columns([3, 1.5])
            with shop_col:
                st.markdown(f"### 📍 {shop}")
            with star_col:
                # Displays the visual stars along with the exact numeric average (e.g., 4.3)
                st.markdown(f"### {star_emojis} `({avg_score:.1f})`")
            
            # The "Folder" mechanic: st.expander bundles all user comments inside a neat drop-down
            with st.expander(f"📖 View Reviews ({len(shop_reviews)})"):
                # Loop backwards through this specific shop's history so the freshest comments hit first
                for _, row in shop_reviews.iloc[::-1].iterrows():
                    individual_stars = "⭐" * int(row['Stars'])
                    st.markdown(f"**Score given:** {individual_stars}")
                    st.caption(f"\"{row['Review']}\"")
                    st.write("---")

# --- LOG A NEW SPOT ---
st.sidebar.header("📥 Drop a New Review")
with st.sidebar:
    st.write("Found a new gem or returning to an old favorite? Log it below.")
    
    shop_name = st.text_input("Where are we drinking coffee?", placeholder="e.g., Sunrise Coffee Roasters").strip()
    
    st.write("Overall Vibe & Taste")
    rating = st.feedback("stars")
    
    review_text = st.text_area(
        "Spill the beans...", 
        placeholder="How was the brew? Good seating? Fast Wi-Fi?",
        max_chars=280
    )
    
    if st.button("Post Review", use_container_width=True):
        if shop_name and review_text and rating is not None:
            # IMPORTANT: Save the raw numeric values (1 to 5) straight into Google Sheets
            numeric_rating = rating + 1
            
            new_review = pd.DataFrame([{
                "Shop": shop_name,
                "Stars": numeric_rating,
                "Review": review_text
            }])
            
            updated_df = pd.concat([existing_data, new_review], ignore_index=True)
            conn.update(worksheet="Reviews", data=updated_df)
            
            st.success(f"Added review for {shop_name}! 🌊")
            st.rerun()
        else:
            st.error("Hold up! Fill out all fields before paddling out.")
