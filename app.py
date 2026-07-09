import streamlit as st

# 1. Define your custom Coastal Cafe CSS as a string
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
</style>
"""

# 2. Inject the CSS into the Streamlit app so it actually renders
st.markdown(coastal_cafe_theme, unsafe_allow_html=True)

# --- Your normal Streamlit app code starts here ---
st.title("Your Bold New Header")
st.write("This body text is now a beautifully clean Open Sans, perfect for reading on the beach after a morning session.")
