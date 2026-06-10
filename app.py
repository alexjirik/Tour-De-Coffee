import streamlit as st
from PIL import Image

# Sets up the browser tab
st.set_page_config(page_title="Tour de Coffee", page_icon="☕", layout="centered")

# The Header
st.title("☕ Tour de Coffee")

# --- INSTAGRAM LINK RIGHT UNDER TITLE ---
st.link_button("Follow the Instagram!", "https://instagram.com/alexxjirik")

st.write("Welcome to the lineup! Drop your latest coffee shop finds here. Let's keep the community caffeinated. 🤙")

st.divider()

# --- REVIEW INPUT SECTION ---
st.subheader("Log a New Spot")

shop_name = st.text_input("Where are we drinking coffee today?")

st.write("Overall Vibe & Taste (Out of 5)")
# This creates the clickable star rating! 
# It returns a number from 0 to 4 (so we add 1 later for a 1-5 scale)
rating = st.feedback("stars")

review_text = st.text_area("Spill the beans... How was the brew? Good outdoor seating? Friendly baristas?")

# The photo uploader
uploaded_file = st.file_uploader("Drop a pic of your cup (or the shop!)", type=["jpg", "jpeg", "png"])

# The submit button
if st.button("Post Review"):
    if shop_name and review_text and rating is not None:
        st.success(f"Yeww! Thanks for reviewing {shop_name}! 🌊")
        
        st.divider()
        
        # --- DISPLAY THE REVIEW ---
        st.subheader(f"Latest Review: {shop_name}")
        
        # Convert the 0-4 rating into actual star emojis to display
        stars_display = "⭐" * (rating + 1)
        st.write(f"**Rating:** {stars_display}")
        
        st.write(f"**Thoughts:** {review_text}")
        
        # If they uploaded a picture, display it!
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Fresh brew from {shop_name}", use_container_width=True)
    else:
        st.error("Hold up! Make sure you fill in the shop name, a review, and click a star rating before paddling out.")
