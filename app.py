import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
from datetime import datetime

# Sets up the browser tab
st.set_page_config(page_title="Tour de Coffee", page_icon="☕", layout="centered")

# Custom CSS Injection for Coffee & Surf Aesthetics AND Pro UX (Editorial Fonts)
st.markdown("""
    <style>
    /* Import Montserrat (800 Extra Bold) and Open Sans (400 Regular) */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&family=Open+Sans:wght@300;400&display=swap');
    
    /* 1. THE VIBE: Apply Montserrat Extra Bold to our main headers */
    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px; 
    }

    /* 2. THE UX: Apply Open Sans Regular to all the body text */
    html, body, p, div, input, textarea, button, .stRadio > label {
        font-family: 'Open Sans', sans-serif !important;
        font-weight: 400 !important;
    }

    /* 3. THE BUTTONS: A little extra breathing room */
    div.stButton > button:first-child {
        background-color: #D27D2D;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.6rem 2rem;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
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
    existing_data = pd.DataFrame(columns=["Shop", "Stars", "Review", "Latitude", "Longitude", "Date", "Tags"])

# --- DATA CLEANUP ---
# Ensure all columns exist just in case the sheet is lagging
if "Latitude" not in existing_data.columns: existing_data["Latitude"] = None
if "Longitude" not in existing_data.columns: existing_data["Longitude"] = None
if "Date" not in existing_data.columns: existing_data["Date"] = None
if "Tags" not in existing_data.columns: existing_data["Tags"] = None

if not existing_data.empty:
    existing_data["Shop"] = existing_data["Shop"].astype(str).str.strip().str.title()

# Master DataFrame for math and map tracking
df = existing_data.copy()
if not df.empty:
    df["Stars"] = pd.to_numeric(df["Stars"], errors='coerce').fillna(5)

# --- APP METRICS ---
unique_shops_count = df["Shop"].nunique() if not df.empty else 0
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Unique Cafés Found", value=unique_shops_count)
with col2:
    st.metric(label="Total Reviews Logged", value=len(df))

st.divider()

# --- LOG A NEW SPOT (MOVED OUT OF SIDEBAR FOR MOBILE UX) ---
with st.expander("📥 Drop a New Review (Click to Open)", expanded=False):
    st.write("Found a new gem in MPLS? Log it below.")
    
    shop_name = st.text_input("Where are we drinking coffee?", placeholder="e.g., Spyhouse Coffee").strip().title()
    shop_address = st.text_input("Street Address (Optional)", placeholder="e.g., 945 Broadway St NE", help="Leave blank! Only needed if the map misses the shop.").strip()
    
    st.write("Overall Vibe & Taste")
    rating = st.feedback("stars")
    
    # NEW: Vibe Tags!
    vibe_tags = st.multiselect(
        "Vibe Check (Select all that apply)", 
        ["💻 Good for Working", "☀️ Great Patio", "🥐 Amazing Pastries", "🚗 Drive-Thru", "🐕 Dog Friendly", "🛋️ Cozy Seating", "☕ Elite Espresso"]
    )
    
    review_text = st.text_area(
        "Spill the beans...", 
        placeholder="How was the brew? Fast Wi-Fi?",
        max_chars=280
    )
    
    if st.button("Post Review", use_container_width=True):
        if shop_name and review_text and rating is not None:
            numeric_rating = rating + 1
            
            # --- THE MAGIC LOCATOR ---
            geolocator = Nominatim(user_agent="tour_de_coffee_mpls")
            search_query = f"{shop_address}, Minneapolis, Minnesota" if shop_address else f"{shop_name}, Minneapolis, Minnesota"
            
            try:
                location = geolocator.geocode(search_query, timeout=5)
            except:
                location = None
                
            if not location and not shop_address:
                st.warning("📍 The map couldn't find this shop by name! Please add the Street Address in the box above and hit Post again.")
                st.stop()
                
            shop_lat = location.latitude if location else None
            shop_lon = location.longitude if location else None
            
            # NEW: Grab the current month and year automatically
            current_date = datetime.now().strftime("%B %Y")
            
            # Combine the tags into a clean comma-separated string
            tags_string = ", ".join(vibe_tags) if vibe_tags else ""
            
            new_review = pd.DataFrame([{
                "Shop": shop_name,
                "Stars": numeric_rating,
                "Review": review_text,
                "Latitude": shop_lat,
                "Longitude": shop_lon,
                "Date": current_date,
                "Tags": tags_string
            }])
            
            updated_df = pd.concat([existing_data, new_review], ignore_index=True)
            conn.update(worksheet="Reviews", data=updated_df)
            
            if shop_lat and shop_lon:
                st.success(f"Yeww! Added {shop_name} and dropped a pin on the map! 🌊📍")
            else:
                st.success(f"Added {shop_name}! (Review safely saved). 🌊")
                
            st.rerun()
        else:
            st.error("Hold up! Fill out all fields before paddling out.")

st.divider()

# --- THE MAP (The Interactive Radar) ---
st.subheader("🗺️ The Local Radar")

if not df.empty:
    map_data = df.dropna(subset=["Latitude", "Longitude"]).copy()
    map_data["Latitude"] = pd.to_numeric(map_data["Latitude"], errors="coerce")
    map_data["Longitude"] = pd.to_numeric(map_data["Longitude"], errors="coerce")
    map_data = map_data.dropna(subset=["Latitude", "Longitude"]) 
    
    if not map_data.empty:
        center_lat = map_data["Latitude"].mean()
        center_lon = map_data["Longitude"].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="CartoDB positron")
        unique_mapped_shops = map_data["Shop"].unique()
        
        for shop in unique_mapped_shops:
            shop_reviews = df[df["Shop"] == shop]
            avg_stars = shop_reviews["Stars"].mean()
            review_count = len(shop_reviews)
            shop_lat = map_data[map_data["Shop"] == shop]["Latitude"].iloc[0]
            shop_lon = map_data[map_data["Shop"] == shop]["Longitude"].iloc[0]
            
            popup_html = f"""
            <div style="font-family: 'Open Sans', sans-serif; min-width: 150px;">
                <h4 style="margin-bottom: 5px; color: #006884; font-family: 'Montserrat', sans-serif; font-weight: 800;">{shop}</h4>
                <p style="margin: 0; font-size: 14px; font-weight: 600;">{avg_stars:.1f} ⭐ ({review_count} reviews)</p>
            </div>
            """
            
            folium.Marker(
                location=[shop_lat, shop_lon],
                tooltip=f"<span style='font-family: Montserrat; font-weight: bold;'>{shop}</span>", 
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="orange", icon="coffee", prefix="fa")
            ).add_to(m)
            
        st_folium(m, width=700, height=400, returned_objects=[])
    else:
        st.info("No mapped locations yet! Add a shop to drop the first pin.")
else:
    st.info("No mapped locations yet! Add a shop to drop the first pin.")

st.divider()

# --- THE FEED (The Local Lineup) ---
st.subheader("✨ The Local Lineup")

if df.empty:
    st.info("No reviews in the database yet. Be the first to drop one!")
else:
    sort_method = st.radio(
        "Sort the Lineup:", 
        ["Highest Rated ⭐", "Most Reviewed 📝", "Alphabetical (A-Z)"], 
        horizontal=True
    )
    
    if sort_method == "Highest Rated ⭐":
        sorted_shops = df.groupby("Shop")["Stars"].mean().sort_values(ascending=False).index.tolist()
    elif sort_method == "Most Reviewed 📝":
        sorted_shops = df["Shop"].value_counts().index.tolist()
    else:
        sorted_shops = sorted(df["Shop"].unique())
    
    st.write("") 
    
    for shop in sorted_shops:
        shop_reviews = df[df["Shop"] == shop]
        avg_stars = shop_reviews["Stars"].mean()
        review_count = len(shop_reviews)
        
        with st.container(border=True):
            st.markdown(f"### 📍 {shop} `({avg_stars:.1f}⭐ | {review_count} reviews)`")
            
            with st.expander(f"📖 Read the Reviews"):
                for _, row in shop_reviews.iloc[::-1].iterrows():
                    individual_stars = "⭐" * int(row['Stars'])
                    
                    # Safely handle the Date and Tags in case older reviews don't have them
                    date_display = f" • {row['Date']}" if pd.notna(row.get('Date')) and row['Date'] else ""
                    
                    st.markdown(f"**Score:** {individual_stars}{date_display}")
                    
                    if pd.notna(row.get('Tags')) and row['Tags']:
                        st.markdown(f"*{row['Tags']}*")
                        
                    st.caption(f"\"{row['Review']}\"")
                    st.write("---")
