import streamlit as st
from datetime import datetime

# 1. Page Configuration (Setting the vibe right out of the gate)
st.set_page_config(page_title="Coastal Cafe", page_icon="☕", layout="centered")

# 2. Define your custom Coastal Cafe CSS
coastal_cafe_theme = """
<style>
/* Import the beans directly from Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Open+Sans:wght@300;400&display=swap');

/* Blanket the app in the clean, breezy base font */
html, body, [class*="css"]  {
    font-family: 'Open Sans', sans-serif;
}

/* Dial in the massive Montserrat Headers for that bold contrast */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 800 !important;
    color: #222222 !important; /* Espresso black, much softer on the eyes than pure black */
    line-height: 1.1 !important;
}

/* Ensure paragraph text stays clean, readable, and perfectly spaced */
p, li, span, div {
    font-family: 'Open Sans', sans-serif !important;
    color: #4A4A4A;
    line-height: 1.6;
}

/* Bump up the standard text slightly for a better mobile reading experience */
p {
    font-size: 18px !important;
}

/* Clean up the blockquote style so our guestbook messages look elevated */
blockquote {
    border-left: 4px solid #E0E0E0;
    padding-left: 1rem;
    color: #666666;
    font-style: italic;
    margin-top: 0.5rem;
}
</style>
"""

# 3. Inject the CSS into the Streamlit app so it actually renders
st.markdown(coastal_cafe_theme, unsafe_allow_html=True)


# --- THE MAIN EXPERIENCE ---

st.title("Welcome to the Lineup")
st.write("Grab a fresh pour-over, find a spot on the patio, and check out what the community is up to. This space is all about good coffee, clean waves, and great friends.")

st.markdown("---")


# --- THE GUESTBOOK ---

# Set up the digital notebook in session state
if 'guestbook' not in st.session_state:
    st.session_state.guestbook = []

st.subheader("The Community Board")
st.write("Drop a recommendation, tell us how the water is today, or just say hey.")

# The Pen and Paper (Input Form)
with st.form("guestbook_form", clear_on_submit=True):
    name = st.text_input("Your Name")
    message = st.text_area("Your Message")
    
    # The submit button
    submit = st.form_submit_button("Post to Board")
    
    if submit and name and message:
        now = datetime.now().strftime("%B %d, %Y")
        st.session_state.guestbook.append({
            "name": name, 
            "message": message, 
            "date": now
        })
        st.success(f"Stoked you stopped by, {name}! Message posted.")
        st.balloons() 

# Displaying the Board
st.markdown("---")

if st.session_state.guestbook:
    for entry in reversed(st.session_state.guestbook): 
        # Clean typography hierarchy for the posts
        st.markdown(f"**{entry['name']}** &nbsp; • &nbsp; *{entry['date']}*")
        st.markdown(f"> {entry['message']}")
        st.write("") 
else:
    st.info("The lineup is empty. Be the first to drop in!")
