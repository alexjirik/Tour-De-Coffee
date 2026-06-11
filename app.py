import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Sets up the browser tab
st.set_page_config(page_title="Tour de Coffee", page_icon="☕", layout="centered")

# The Header
st.title("☕ Tour de Coffee")
st.link_button("Follow the Instagram!", "https://instagram.com/tour.decoffee")
st.write("Welcome to the lineup! Drop your latest coffee shop finds here. Let's keep the community caffeinated. 🤙")

st.divider()

# --- CONNECT TO THE DATABASE (The Espresso Machine) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the current reviews from the "Reviews" tab
# Removed usecols so we safely read the whole structure before updating it later
existing_data = conn.read(worksheet="Reviews", ttl=0)

if existing_data is not None:
    existing_data = existing_data.dropna(how="all")  # Cleans up any empty rows
else:
    existing_data = pd.DataFrame(columns=["Shop", "Stars", "Review"])

# --- THE FEED (Showing Past Reviews) ---
st.subheader("The Local Lineup")

if existing_data.empty:
    st.info("No reviews in the database yet. Be the first to drop one!")
else:
    # This loops through your Google Sheet and prints every review!
    for index, row in existing_data.iterrows():
        st.write(f"### 📍 {row['Shop']}")
        st.write(f"**Rating:** {row['Stars']}")
        st.write(f"**Thoughts:** {row['Review']}")
        st.write("---")  # A subtle visual line between reviews

# --- LOG A NEW SPOT ---
st.subheader("Drop a New Review")

shop_name = st.text_input("Where are we drinking coffee today?")
st.write("Overall Vibe & Taste (Out of 5)")
rating = st.feedback("stars")
review_text = st.text_area("Spill the beans... How was the brew? Good outdoor seating?")

# The submit button
if st.button("Post Review"):
    if shop_name and review_text and rating is not None:
        # Convert the 0-4 rating into actual star emojis
        stars_display = "⭐" * (rating + 1)
        
        # Package the new review exactly how Google Sheets expects it
        new_review = pd.DataFrame([{
            "Shop": shop_name,
            "Stars": stars_display,
            "Review": review_text
        }])
        
        # Combine the old list of reviews with the new one
        updated_df = pd.concat([existing_data, new_review], ignore_index=True)
        
        # Push the updated list back to the Google Sheet!
        conn.update(worksheet="Reviews", data=updated_df)
        
        st.success(f"Yeww! Added {shop_name} to the lineup! 🌊")
        st.rerun()  # Refresh the page to show the feed instantly
    else:
        st.error("Hold up! Make sure you fill in the shop name, a review, and click a star rating before paddling out.")
