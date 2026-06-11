import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from geopy.geocoders import Nominatim

# Sets up the browser tab
st.set_page_config(page_title="Tour de Coffee", page_icon="☕", layout="centered")

# Custom CSS Injection for Coffee & Surf Aesthetics AND Pro UX (Laptop Hack Included)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Montserrat:wght@400;600&display=swap');
    
    /* 1. THE VIBE: Apply Caveat to our main headers */
    h1, h2, h3 {
        font-family: 'Caveat', cursive !important;
        letter-spacing: 1px;
    }

    /* 2. THE UX: Apply Montserrat to all the regular text */
    html, body, p, div, input, textarea, button {
        font-family: 'Montserrat', sans-serif !important;
    }

    /* 3. THE BUTTONS: A little extra breathing room */
    div.stButton > button:first-child {
        background-color: #D27D2D;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease; 
    }
    div.stButton > button:first-child:hover {
        background-color: #A0522D;
        color: white;
        transform: translateY(-2px); 
    }

    /* 4. THE COLORS: Temporary Laptop Hack */
    .stApp {
        background-color: #F4F1EA;
    }
    [data-testid="stSidebar"] {
        background-color: #EAE5D9;
    }
    h1, h2, h3, p, span, label, div {
        color: #006884 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("☕ Tour de Coffee: MPLS")
st.caption("Keeping the Minneapolis community caffeinated & stoked. 🤙")
st.link_button("📸 Follow the Instagram", "https://instagram.com/tour.decoffee")

st.divider()

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="Reviews", ttl=0)

if existing_data is not None:
    existing_data = existing_data.dropna(how="all")
else:
    existing_data = pd.DataFrame(columns=["Shop", "Stars", "Review", "Latitude", "Longitude"])

# --- DATA CLEANUP ---
if "Latitude" not in existing_data.columns:
    existing_data["Latitude"] = None
if "Longitude" not in existing_data.columns:
    existing_data["Longitude"] = None

if not existing_data.empty:
    existing_data["Shop"] = existing_data["Shop"].astype(str).str.strip().str.title()

# --- APP METRICS ---
unique_shops_count = existing_data["Shop"].nunique() if not existing_data.empty else 0
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Unique Cafés Found", value=unique_shops_count)
with col2:
    st.metric(label="Total Reviews Logged", value=len(existing_data))

st.divider()

# --- THE MAP (The Local Radar) ---
st.subheader("🗺️ The Local Radar")

if not existing_data.empty:
    map_data = existing_data.dropna(subset=["Latitude", "Longitude"]).copy()
    
    map_data["Latitude"] = pd.to_numeric(map_data["Latitude"], errors="coerce")
    map_data["Longitude"] = pd.to_numeric(map_data["Longitude"], errors="coerce")
    map_data = map_data.dropna(subset=["Latitude", "Longitude"]) 
    
    if not map_data.empty:
        map_data = map_data.rename(columns={"Latitude": "lat", "Longitude": "lon"})
        st.map(map_data, color="#D27D2D", size=200) 
    else:
        st.info("No mapped locations yet! Add a shop to drop the first pin.")
else:
    st.info("No mapped locations yet! Add a shop to drop the first pin.")

st.divider()

# --- THE FEED (The Local Lineup) ---
st.subheader("✨ The Local Lineup")

if existing_data.empty:
    st.info("No reviews in the database yet. Be the first to drop one!")
else:
    df = existing_data.copy()
    df["Stars"] = pd.to_numeric(df["Stars"], errors='coerce').fillna(5)
    unique_shops = df["Shop"].unique()
    
    for shop in unique_shops:
        shop_reviews = df[df["Shop"] == shop]
        with st.container(border=True):
            st.markdown(f"### 📍 {shop}")
            with st.expander(f"📖 View Reviews ({len(shop_reviews)})"):
                for _, row in shop_reviews.iloc[::-1].iterrows():
                    individual_stars = "⭐" * int(row['Stars'])
                    st.markdown(f"**Score given:** {individual_stars}")
                    st.caption(f"\"{row['Review']}\"")
                    st.write("---")

# --- LOG A NEW SPOT ---
st.sidebar.header("📥 Drop a New Review")
with st.sidebar:
    st.write("Found a new gem in MPLS? Log it below.")
    
    shop_name = st.text_input("Where are we drinking coffee?", placeholder="e.g., Spyhouse Coffee").strip().title()
    
    # NEW: Optional Address Field
    shop_address = st.text_input("Street Address (Optional)", placeholder="e.g., 945 Broadway St NE", help="Leave blank! Only needed if the map misses the shop by name.").strip()
    
    st.write("Overall Vibe & Taste")
    rating = st.feedback("stars")
    
    review_text = st.text_area(
        "Spill the beans...", 
        placeholder="How was the brew? Good seating? Fast Wi-Fi?",
        max_chars=280
    )
    
    if st.button("Post Review", use_container_width=True):
        if shop_name and review_text and rating is not None:
            numeric_rating = rating + 1
            
            geolocator = Nominatim(user_agent="tour_de_coffee_mpls")
            
            # Use the address if they provided one, otherwise guess by name
            if shop_address:
                search_query = f"{shop_address}, Minneapolis, Minnesota"
            else:
                search_query = f"{shop_name}, Minneapolis, Minnesota"
            
            try:
                location = geolocator.geocode(search_query, timeout=5)
            except:
                location = None
                
            # THE MAGIC BRAKE: If it fails and they didn't give an address, stop everything!
            if not location and not shop_address:
                st.warning("📍 The map couldn't find this shop by name! Please add the Street Address in the box above and hit Post again.")
                st.stop()
                
            shop_lat = location.latitude if location else None
            shop_lon = location.longitude if location else None
            
            new_review = pd.DataFrame([{
                "Shop": shop_name,
                "Stars": numeric_rating,
                "Review": review_text,
                "Latitude": shop_lat,
                "Longitude": shop_lon
            }])
            
            updated_df = pd.concat([existing_data, new_review], ignore_index=True)
            conn.update(worksheet="Reviews", data=updated_df)
            
            if shop_lat and shop_lon:
                st.success(f"Yeww! Added {shop_name} and dropped a pin on the map! 🌊📍")
            else:
                st.success(f"Added {shop_name}! (Even with the address, the free map missed the pin, but the review is safely saved). 🌊")
                
            st.rerun()
        else:
            st.error("Hold up! Fill out all fields before paddling out.")
