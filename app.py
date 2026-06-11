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
