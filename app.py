import streamlit as st
from PIL import Image

# Sets up the browser tab
st.set_page_config(page_title="Tour de Coffee", page_icon="☕", layout="centered")

# --- INITIALIZE MEMORY (The Filing Cabinet) ---
# This creates a dictionary to hold our "folders" if it doesn't exist yet
if 'shops' not in st.session_state:
    st.session_state.shops = {}

# The Header
st.title("☕ Tour de Coffee")
st.link_button("Follow the Instagram!", "https://instagram.com/tour.decoffee")
st.write("Welcome to the lineup! Drop your latest coffee shop finds here. Let's keep the community caffeinated. 🤙")

st.divider()

# --- THE NAVIGATION (Selecting or Creating a Folder) ---
st.subheader("Where are we dropping in?")

# Get the list of shops we've already added, plus an option to create a new one
existing_shops = list(st.session_state.shops.keys())
options = ["✨ Add a New Shop"] + existing_shops

selected_option = st.selectbox("Choose a spot or add a new one:", options)

st.divider()

# --- LOGIC FOR ADDING A NEW SHOP ---
if selected_option == "✨ Add a New Shop":
    st.write("### Start a New Thread")
    new_shop_name = st.text_input("Name of the new coffee shop:")
    
    if st.button("Create Shop Folder"):
        if new_shop_name and new_shop_name not in st.session_state.shops:
            # Create an empty list (folder) for this new shop
            st.session_state.shops[new_shop_name] = []
            st.success(f"Yeww! Added {new_shop_name} to the lineup.")
            st.rerun() # Refreshes the page to update the dropdown
        elif new_shop_name in st.session_state.shops:
            st.warning("That spot is already in the lineup! Select it from the dropdown above.")
        else:
            st.error("Gotta name the spot first!")

# --- LOGIC FOR AN EXISTING SHOP ---
else:
    current_shop = selected_option
    st.write(f"### 📍 {current_shop}")
    
    # 1. Display all past reviews for this specific shop
    reviews = st.session_state.shops[current_shop]
    
    if not reviews:
        st.info("No reviews here yet. Be the first to drop one!")
    else:
        for r in reviews:
            st.write(f"**Rating:** {r['stars']}")
            st.write(f"**Thoughts:** {r['text']}")
            if r['image'] is not None:
                st.image(r['image'], use_container_width=True)
            st.write("---") # A subtle line between reviews

    # 2. Form to add a new review to THIS shop
    st.write(f"**Leave a review for {current_shop}:**")
    
    rating = st.feedback("stars")
    review_text = st.text_area("Spill the beans... How was the brew? Good outdoor seating?")
    uploaded_file = st.file_uploader("Drop a pic of your cup", type=["jpg", "jpeg", "png"])
    
    if st.button("Post Review"):
        if review_text and rating is not None:
            # Open the image if they uploaded one
            img_data = Image.open(uploaded_file) if uploaded_file else None
            
            # Package the review up
            new_review = {
                "stars": "⭐" * (rating + 1),
                "text": review_text,
                "image": img_data
            }
            
            # Save it to this shop's folder
            st.session_state.shops[current_shop].append(new_review)
            st.rerun() # Refresh to show the new review instantly
        else:
            st.error("Hold up! Make sure you fill in a review and click a star rating before paddling out.")
        st.error("Hold up! Make sure you fill in the shop name, a review, and click a star rating before paddling out.")
